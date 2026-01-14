# SwarmSentinel v3 🐝

LangGraph crypto sentiment trading bot powered by Grok AI.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Pipeline-FF6B6B?style=flat)
![Grok](https://img.shields.io/badge/Grok_AI-XAI-000000?style=flat)

## 5-Node Pipeline Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  SENTIMENT   │───▶│    WHALE     │───▶│   REGIME     │
│  ANALYSIS    │    │   SCORING    │    │  DETECTION   │
└──────────────┘    └──────────────┘    └──────────────┘
                                               │
                    ┌──────────────┐    ┌──────▼───────┐
                    │  EXECUTION   │◀───│   STRATEGY   │
                    │   ENGINE     │    │   ROUTING    │
                    └──────────────┘    └──────────────┘
```

| Node | Function |
|------|----------|
| Sentiment | Analyze social/news sentiment via Grok |
| Whale Scoring | Track large wallet movements |
| Regime Detection | Market condition classification |
| Strategy Routing | Select optimal trading strategy |
| Execution | Execute trades with risk management |

## Features

- 🤖 **Grok AI Integration** - XAI API for sentiment analysis
- 📊 **Volume Alpha Attribution** - Track smart money flows
- 🔔 **Telegram Alerts** - Real-time notifications
- 🛡️ **Security Hardened** - Audit fixes applied Dec 2024
- 🧪 **Simulation Mode** - Safe testing environment

## Quick Start

```bash
# Clone
git clone https://github.com/ivan09069/SwarmSentinel-v3.git
cd SwarmSentinel-v3

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
python main.py
```

## Environment Variables

```bash
XAI_API_KEY=xai-...          # Required - Grok API
TELEGRAM_BOT_TOKEN=...       # Optional - Alerts
TELEGRAM_CHAT_ID=...         # Optional - Alerts
SIM_MODE=True                # True=paper trading
POLL_INTERVAL=60             # Seconds between cycles
XAI_MODEL=grok-3-fast        # AI model
```

## Deployment

### Railway
```bash
railway login
railway init
railway up
```

### Render
Uses `render.yaml` - connect repo and deploy.

### Docker
```bash
docker build -t swarmsentinel .
docker run -d --env-file .env swarmsentinel
```

## Status

| Component | Status |
|-----------|--------|
| Core Pipeline | ✅ Production Ready |
| Security Audit | ✅ Passed |
| Telegram Alerts | ✅ Working |
| Live Trading | ⚠️ Requires API Keys |

## Part of EchoForge Studios

- [EchoForge](https://github.com/ivan09069/EchoForge) - Portfolio Tracker
- [JIT-Command-Center](https://github.com/ivan09069/JIT-Command-Center) - Monitoring
- [echoforge-texas-platform](https://github.com/ivan09069/echoforge-texas-platform) - Energy Platform

---

**Built by EchoForge Studios** | *Forged, not finished*

