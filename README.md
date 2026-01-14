# SwarmSentinel v3 🐝

LangGraph crypto sentiment analysis engine powered by Grok AI.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-FF6B6B?style=flat)
![Grok](https://img.shields.io/badge/Grok_AI-000000?style=flat&logo=x&logoColor=white)

## 5-Node Pipeline Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  SENTIMENT   │───▶│    WHALE     │───▶│   REGIME     │
│  ANALYSIS    │    │   SCORING    │    │  DETECTION   │
└──────────────┘    └──────────────┘    └──────────────┘
                                              │
                    ┌──────────────┐    ┌─────▼────────┐
                    │  EXECUTION   │◀───│   STRATEGY   │
                    │   ENGINE     │    │   ROUTING    │
                    └──────────────┘    └──────────────┘
```

## Features

- 🧠 **Grok AI Integration** - xAI's frontier model for market analysis
- 📊 **Volume Alpha Attribution** - Whale movement detection
- 🔄 **Live Market Data** - Real-time price feeds
- 🔐 **Security Hardened** - Audit fixes applied Dec 2024
- 📱 **Telegram Alerts** - Optional notification system
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

| Variable | Required | Description |
|----------|----------|-------------|
| `XAI_API_KEY` | ✅ | Grok API key from x.ai |
| `TELEGRAM_BOT_TOKEN` | ❌ | For alert notifications |
| `TELEGRAM_CHAT_ID` | ❌ | Your Telegram chat ID |
| `SIM_MODE` | ❌ | `True` for paper trading |
| `POLL_INTERVAL` | ❌ | Seconds between cycles (default: 60) |
| `XAI_MODEL` | ❌ | Model selection (default: grok-3-fast) |

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
| Core Engine | ✅ Production Ready |
| Security Audit | ✅ Hardened (Dec 2024) |
| Telegram Integration | ✅ Optional |
| Multi-chain Support | 🔄 In Progress |

## Part of EchoForge Studios

- [EchoForge](https://github.com/ivan09069/EchoForge) - Portfolio Tracker
- [JIT-Command-Center](https://github.com/ivan09069/JIT-Command-Center) - Monitoring Dashboard
- [echoforge-texas-platform](https://github.com/ivan09069/echoforge-texas-platform) - Energy Platform

---

**Built by EchoForge Studios** | *Forged, not finished*

