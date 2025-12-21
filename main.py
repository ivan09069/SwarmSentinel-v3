#!/usr/bin/env python3
"""
SwarmSentinel v3 - HARDENED Production Build
Security audit fixes applied: 2024-12-19
"""

import os
import sys
import time
import math
import json
import logging
import re
from datetime import datetime, timezone
from typing import TypedDict, Dict, Any, Optional
from dataclasses import dataclass, field
from functools import wraps

from dotenv import load_dotenv

load_dotenv()


# ==================== LOGGING (REDACTED) ====================
class RedactingFormatter(logging.Formatter):
    """Redact sensitive data from logs"""
    PATTERNS = [
        (re.compile(r'(api[_-]?key|token|secret|password)["\s:=]+["\']?[\w\-]+', re.I), r'\1=***REDACTED***'),
        (re.compile(r'xai-[\w\-]+'), '***API_KEY***'),
        (re.compile(r'sk-[\w\-]+'), '***API_KEY***'),
    ]

    def format(self, record):
        msg = super().format(record)
        for pattern, replacement in self.PATTERNS:
            msg = pattern.sub(replacement, msg)
        return msg


def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter(
        '%(asctime)s | %(levelname)s | %(message)s'
    ))
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


logger = setup_logging()


# ==================== CONFIGURATION ====================
@dataclass
class Config:
    """Centralized configuration - no magic numbers"""
    # API
    XAI_API_KEY: str = field(default_factory=lambda: os.getenv("XAI_API_KEY", ""))
    XAI_MODEL: str = field(default_factory=lambda: os.getenv("XAI_MODEL", "grok-3-fast"))
    XAI_BASE_URL: str = "https://api.x.ai/v1"
    REQUEST_TIMEOUT: int = 30
    
    # Runtime
    SIM_MODE: bool = field(default_factory=lambda: os.getenv("SIM_MODE", "True").lower() == "true")
    POLL_INTERVAL: int = field(default_factory=lambda: int(os.getenv("POLL_INTERVAL", "60")))
    
    # Circuit breaker
    MAX_CONSECUTIVE_FAILURES: int = 5
    BACKOFF_BASE: int = 2
    BACKOFF_MAX: int = 300  # 5 min max backoff
    
    # Rate limiting
    MAX_API_CALLS_PER_CYCLE: int = 5
    MIN_CYCLE_INTERVAL: int = 30  # Never poll faster than 30s
    
    # Trading thresholds
    RISK_ON_THRESHOLD: float = 0.3
    RISK_OFF_THRESHOLD: float = -0.3
    MOMENTUM_THRESHOLD: float = 0.05
    WHALE_FLOW_DIVISOR: float = 50_000_000.0
    WHALE_HALF_LIFE: int = 6 * 3600  # 6 hours in seconds
    
    # Weights
    TREND_WEIGHT: float = 0.4
    SENTIMENT_WEIGHT: float = 0.25
    WHALE_WEIGHT: float = 0.25
    VOLATILITY_WEIGHT: float = 0.1
    MOMENTUM_SHORT_WEIGHT: float = 0.6
    MOMENTUM_MID_WEIGHT: float = 0.4

    def validate(self) -> bool:
        """Validate critical config before startup"""
        errors = []
        
        if not self.XAI_API_KEY:
            errors.append("XAI_API_KEY is required")
        elif not self.XAI_API_KEY.startswith(("xai-", "sk-")):
            errors.append("XAI_API_KEY format invalid")
        
        if self.POLL_INTERVAL < self.MIN_CYCLE_INTERVAL:
            errors.append(f"POLL_INTERVAL must be >= {self.MIN_CYCLE_INTERVAL}s")
        
        if self.WHALE_FLOW_DIVISOR == 0:
            errors.append("WHALE_FLOW_DIVISOR cannot be zero")
        
        if errors:
            for e in errors:
                logger.error(f"Config error: {e}")
            return False
        return True


config = Config()


# ==================== CIRCUIT BREAKER ====================
class CircuitBreaker:
    """Prevent runaway failures"""
    def __init__(self, max_failures: int, backoff_base: int, backoff_max: int):
        self.max_failures = max_failures
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.failures = 0
        self.last_failure_time = 0
        self.is_open = False
    
    def record_success(self):
        self.failures = 0
        self.is_open = False
    
    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.max_failures:
            self.is_open = True
            logger.warning(f"Circuit breaker OPEN after {self.failures} failures")
    
    def get_backoff(self) -> int:
        if self.failures == 0:
            return 0
        backoff = min(self.backoff_base ** self.failures, self.backoff_max)
        return backoff
    
    def can_proceed(self) -> bool:
        if not self.is_open:
            return True
        # Allow retry after backoff
        elapsed = time.time() - self.last_failure_time
        if elapsed >= self.get_backoff():
            logger.info("Circuit breaker: attempting recovery")
            return True
        return False


circuit_breaker = CircuitBreaker(
    config.MAX_CONSECUTIVE_FAILURES,
    config.BACKOFF_BASE,
    config.BACKOFF_MAX
)


# ==================== RATE LIMITER ====================
class RateLimiter:
    """Track API calls per cycle"""
    def __init__(self, max_calls: int):
        self.max_calls = max_calls
        self.calls = 0
        self.cycle_start = time.time()
    
    def reset(self):
        self.calls = 0
        self.cycle_start = time.time()
    
    def can_call(self) -> bool:
        return self.calls < self.max_calls
    
    def record_call(self):
        self.calls += 1
        if self.calls >= self.max_calls:
            logger.warning(f"Rate limit reached: {self.calls}/{self.max_calls} calls")


rate_limiter = RateLimiter(config.MAX_API_CALLS_PER_CYCLE)


# ==================== INPUT SANITIZATION ====================
def sanitize_input(text: str, max_length: int = 500) -> str:
    """Sanitize user/external input to prevent prompt injection"""
    if not text:
        return ""
    # Remove potential injection patterns
    sanitized = re.sub(r'[{}\[\]<>]', '', text)  # Remove structural chars
    sanitized = re.sub(r'(system|user|assistant):', '', sanitized, flags=re.I)  # Remove role markers
    sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)  # Collapse excessive newlines
    return sanitized[:max_length].strip()


# ==================== STATE ====================
class SwarmState(TypedDict):
    market_data: Dict[str, Any]
    onchain_data: Dict[str, Any]
    raw_sentiment: Dict[str, list]
    sentiment: Dict[str, Any]
    whale_score: Dict[str, Any]
    btc_regime: Dict[str, Any]
    alt_regime: Dict[str, Any]
    regime: Dict[str, Any]
    signal: Dict[str, Any]
    errors: list


# ==================== LLM SETUP (LAZY INIT) ====================
_llm_instance = None


def get_llm():
    """Lazy initialization with timeout"""
    global _llm_instance
    if _llm_instance is None:
        from langchain_openai import ChatOpenAI
        from langchain_core.tools import tool
        
        @tool
        def x_keyword_search(query: str, limit: int = 20, mode: str = "Latest") -> str:
            """Search X/Twitter for crypto sentiment"""
            return f"[Real-time X posts for: {sanitize_input(query)}] (simulated {limit} posts)"
        
        _llm_instance = ChatOpenAI(
            model=config.XAI_MODEL,
            base_url=config.XAI_BASE_URL,
            api_key=config.XAI_API_KEY,
            temperature=0.3,
            request_timeout=config.REQUEST_TIMEOUT,
        ).bind_tools([x_keyword_search])
    
    return _llm_instance


# ==================== SENTIMENT ANALYSIS ====================
def run_sentiment_with_tools(asset: str, timeframe: str, existing: str = "") -> Dict[str, Any]:
    """Run sentiment analysis with proper error handling"""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
    
    # Check rate limit
    if not rate_limiter.can_call():
        logger.warning("Skipping API call - rate limited")
        return _default_sentiment()
    
    # Sanitize inputs
    safe_asset = sanitize_input(asset, 20)
    safe_timeframe = sanitize_input(timeframe, 100)
    safe_existing = sanitize_input(existing, 500)
    
    sentiment_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are a crypto sentiment analyst. Analyze market sentiment.
Output ONLY valid JSON:
{"score": <float -1 to 1>, "confidence": <float 0 to 1>, "key_reasons": [<strings>], "acceleration": "<accelerating|decelerating|stable>"}"""),
        HumanMessage(content=f"Asset: {safe_asset}\nTimeframe: {safe_timeframe}\nContext: {safe_existing}")
    ])
    
    parser = JsonOutputParser()
    
    try:
        llm = get_llm()
        rate_limiter.record_call()
        
        messages = sentiment_prompt.invoke({}).messages
        response = llm.invoke(messages)
        
        # Handle tool calls if present
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_msgs = []
            for call in response.tool_calls:
                if call["name"] == "x_keyword_search":
                    # Import tool here to avoid circular ref
                    from langchain_core.tools import tool as tool_decorator
                    @tool_decorator
                    def x_keyword_search(query: str, limit: int = 20, mode: str = "Latest") -> str:
                        """Search X/Twitter"""
                        return f"[X posts for: {query}]"
                    
                    result = f"[Simulated X search: {call['args'].get('query', '')}]"
                    tool_msgs.append(ToolMessage(content=result, tool_call_id=call["id"]))
            
            if tool_msgs and rate_limiter.can_call():
                rate_limiter.record_call()
                response = llm.invoke(messages + [response] + tool_msgs)
        
        result = parser.parse(response.content)
        
        # Validate response structure
        return _validate_sentiment(result)
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {type(e).__name__}: {e}")
        return _default_sentiment()


def _default_sentiment() -> Dict[str, Any]:
    """Safe default sentiment response"""
    return {
        "score": 0.0,
        "confidence": 0.0,
        "key_reasons": ["analysis unavailable"],
        "acceleration": "stable"
    }


def _validate_sentiment(result: Dict) -> Dict[str, Any]:
    """Validate and clamp sentiment values"""
    return {
        "score": max(-1.0, min(1.0, float(result.get("score", 0)))),
        "confidence": max(0.0, min(1.0, float(result.get("confidence", 0)))),
        "key_reasons": result.get("key_reasons", [])[:5],  # Limit reasons
        "acceleration": result.get("acceleration", "stable")
    }


# ==================== NODES ====================
def multi_sentiment_node(state: SwarmState) -> SwarmState:
    """Fetch multi-timeframe sentiment"""
    if config.SIM_MODE:
        logger.info("[SIM] Skipping real sentiment - using defaults")
        state["sentiment"] = {
            "short": _default_sentiment(),
            "mid": _default_sentiment(),
            "long": _default_sentiment(),
            "timestamp": time.time()
        }
        return state
    
    asset = "BTC"
    
    short = run_sentiment_with_tools(asset, "short-term 1-4 hours")
    mid = run_sentiment_with_tools(asset, "mid-term 24 hours")
    long = run_sentiment_with_tools(asset, "long-term 7 days")
    
    state["sentiment"] = {
        "short": short,
        "mid": mid,
        "long": long,
        "timestamp": time.time()
    }
    
    logger.info(f"Sentiment: short={short['score']:.2f} mid={mid['score']:.2f} long={long['score']:.2f}")
    return state


def whale_scoring_node(state: SwarmState) -> SwarmState:
    """Calculate whale conviction score"""
    flows = state.get("onchain_data", {}).get("whale_flows", [])
    sentiment_score = state["sentiment"]["short"]["score"]
    now = time.time()
    
    if not flows:
        state["whale_score"] = {"whale_conviction": 0.0}
        return state
    
    try:
        net_flow = sum(
            (1 if tx.get("direction") == "in" else -1) * 
            float(tx.get("usd_value", 0)) *
            math.exp(-(now - float(tx.get("timestamp", now))) / config.WHALE_HALF_LIFE)
            for tx in flows
            if isinstance(tx, dict)
        )
        
        # Safe division
        divisor = config.WHALE_FLOW_DIVISOR if config.WHALE_FLOW_DIVISOR != 0 else 1.0
        flow_score = max(-1.0, min(1.0, net_flow / divisor))
        whale_conviction = flow_score * (1 + abs(sentiment_score))
        
    except (ValueError, TypeError) as e:
        logger.warning(f"Whale scoring error: {e}")
        whale_conviction = 0.0
    
    state["whale_score"] = {"whale_conviction": whale_conviction}
    logger.info(f"Whale conviction: {whale_conviction:.3f}")
    return state


def btc_regime_node(state: SwarmState) -> SwarmState:
    """Determine BTC market regime"""
    trend = state.get("market_data", {}).get("trend", 0.4)
    volatility = state.get("market_data", {}).get("volatility", 0.3)
    sentiment = state["sentiment"]["short"]["score"]
    whale = state["whale_score"]["whale_conviction"]
    
    risk_score = (
        config.TREND_WEIGHT * trend +
        config.SENTIMENT_WEIGHT * sentiment +
        config.WHALE_WEIGHT * whale -
        config.VOLATILITY_WEIGHT * volatility
    )
    
    if risk_score > config.RISK_ON_THRESHOLD:
        regime = "RISK_ON"
    elif risk_score < config.RISK_OFF_THRESHOLD:
        regime = "RISK_OFF"
    else:
        regime = "NEUTRAL"
    
    state["btc_regime"] = {"regime": regime, "risk_score": risk_score}
    logger.info(f"BTC regime: {regime} (score: {risk_score:.3f})")
    return state


def alt_regime_sync_node(state: SwarmState) -> SwarmState:
    """Sync alt regime with BTC"""
    btc = state["btc_regime"]["regime"]
    alt_base = state.get("regime", {}).get("regime", "NEUTRAL")
    
    if btc == "RISK_OFF":
        final = "RISK_OFF"
    elif btc == "NEUTRAL" and alt_base == "RISK_ON":
        final = "NEUTRAL"
    else:
        final = alt_base
    
    state["alt_regime"] = {"alt_regime": final}
    return state


def sentiment_delta_node(state: SwarmState) -> SwarmState:
    """Calculate sentiment momentum"""
    s = state["sentiment"]
    
    delta_short = s["short"]["score"] - s["mid"]["score"]
    delta_mid = s["mid"]["score"] - s["long"]["score"]
    momentum = (
        config.MOMENTUM_SHORT_WEIGHT * delta_short +
        config.MOMENTUM_MID_WEIGHT * delta_mid
    )
    
    state["sentiment"]["deltas"] = {"momentum": momentum}
    logger.info(f"Momentum: {momentum:.3f}")
    return state


def strategy_router_node(state: SwarmState) -> SwarmState:
    """Route to appropriate strategy"""
    regime = state["alt_regime"]["alt_regime"]
    momentum = state["sentiment"]["deltas"]["momentum"]
    
    if config.SIM_MODE:
        strategy = "SIMULATION_HOLD"
    elif regime == "RISK_ON" and momentum > 0:
        strategy = "TREND_FOLLOWING"
    elif regime == "RISK_OFF":
        strategy = "CAPITAL_PRESERVATION"
    elif abs(momentum) < config.MOMENTUM_THRESHOLD:
        strategy = "MEAN_REVERSION"
    else:
        strategy = "SELECTIVE_SCALPING"
    
    state["signal"] = {
        "strategy": strategy,
        "regime": regime,
        "momentum": round(momentum, 4),
        "timestamp": time.time(),
        "sim_mode": config.SIM_MODE
    }
    
    logger.info(f"SIGNAL: {strategy} | Regime: {regime} | SIM: {config.SIM_MODE}")
    return state


# ==================== HEALTH CHECK ====================
def write_heartbeat():
    """Write heartbeat file for external monitoring"""
    try:
        heartbeat = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "alive",
            "sim_mode": config.SIM_MODE,
            "failures": circuit_breaker.failures
        }
        with open("/tmp/swarmsentinel_heartbeat.json", "w") as f:
            json.dump(heartbeat, f)
    except Exception:
        pass  # Non-critical


# ==================== MAIN LOOP ====================
def run_cycle() -> Optional[Dict]:
    """Execute one analysis cycle"""
    rate_limiter.reset()
    
    state: SwarmState = {
        "market_data": {"trend": 0.4, "volatility": 0.3},
        "onchain_data": {"whale_flows": []},
        "raw_sentiment": {"short": [], "mid": [], "long": []},
        "sentiment": {},
        "whale_score": {},
        "btc_regime": {},
        "alt_regime": {},
        "regime": {"regime": "NEUTRAL"},
        "signal": {},
        "errors": []
    }
    
    pipeline = [
        multi_sentiment_node,
        whale_scoring_node,
        btc_regime_node,
        alt_regime_sync_node,
        sentiment_delta_node,
        strategy_router_node
    ]
    
    for node in pipeline:
        try:
            state = node(state)
        except Exception as e:
            logger.error(f"Node {node.__name__} failed: {type(e).__name__}: {e}")
            state["errors"].append(f"{node.__name__}: {str(e)[:100]}")
    
    return state


def main():
    """Main entry point with circuit breaker"""
    logger.info("=" * 50)
    logger.info("SwarmSentinel v3 - HARDENED")
    logger.info("=" * 50)
    
    # Validate config
    if not config.validate():
        logger.error("Configuration validation failed. Exiting.")
        sys.exit(1)
    
    logger.info(f"Mode: {'SIMULATION' if config.SIM_MODE else 'LIVE'}")
    logger.info(f"Poll interval: {config.POLL_INTERVAL}s")
    logger.info(f"Model: {config.XAI_MODEL}")
    logger.info("=" * 50)
    
    cycle_count = 0
    
    while True:
        cycle_count += 1
        
        # Circuit breaker check
        if not circuit_breaker.can_proceed():
            backoff = circuit_breaker.get_backoff()
            logger.warning(f"Circuit breaker open. Waiting {backoff}s...")
            time.sleep(backoff)
            continue
        
        logger.info(f"--- Cycle {cycle_count} ---")
        
        try:
            result = run_cycle()
            
            if result and not result.get("errors"):
                circuit_breaker.record_success()
                print(json.dumps(result["signal"], indent=2))
            else:
                circuit_breaker.record_failure()
                logger.warning(f"Cycle completed with errors: {result.get('errors', [])}")
            
            write_heartbeat()
            
        except KeyboardInterrupt:
            logger.info("Shutdown requested")
            break
        except Exception as e:
            circuit_breaker.record_failure()
            logger.error(f"Cycle {cycle_count} failed: {type(e).__name__}: {e}")
        
        # Sleep with backoff awareness
        sleep_time = max(config.POLL_INTERVAL, circuit_breaker.get_backoff())
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
