# SwarmSentinel v3 - Production Deployment

## Overview
LangChain/LangGraph-based crypto trading pattern detection engine using Grok AI.

## Features
- 5-node LangGraph pipeline
- Volume alpha attribution testing
- Live market data integration
- Security-hardened (audit fixes applied 2024-12-19)
- Optional Telegram alerts
- Simulation mode for safe testing

## Requirements
- Python 3.10+
- XAI API key (for Grok access)
- Optional: Telegram bot token for alerts

## Environment Variables
```bash
XAI_API_KEY=xai-...          # Required
TELEGRAM_BOT_TOKEN=...       # Optional
TELEGRAM_CHAT_ID=...         # Optional
SIM_MODE=True                # Set False for live trading
POLL_INTERVAL=60             # Seconds between cycles
XAI_MODEL=grok-3-fast        # AI model to use
```

## Deployment
Configured for Render.com with `render.yaml`.

Deploy to Render:
1. Push to GitHub
2. Connect repo in Render dashboard
3. Add environment variables
4. Deploy

## Status
- ✅ Security hardened
- ✅ Production ready
- ⚠️ Currently showing DEGRADED on Railway (needs env vars)
