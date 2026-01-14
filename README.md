# SwarmSentinel v3 🐝

LangGraph crypto sentiment trading bot powered by Grok AI.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Pipeline-FF6B6B?style=flat)
![Grok](https://img.shields.io/badge/Grok_AI-XAI-000000?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

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

## Installation

### Prerequisites

- Python 3.10+
- Grok API key (from [x.ai](https://x.ai))
- Telegram bot token (optional, for alerts)

### Setup

```bash
# Clone the repository
git clone https://github.com/ivan09069/SwarmSentinel-v3.git
cd SwarmSentinel-v3

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

Required environment variables:

```env
GROK_API_KEY=xai-xxxxxxxxxxxx
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
BASE_RPC_URL=https://mainnet.base.org
PRIVATE_KEY=your_wallet_private_key  # For live trading only
```

## Usage

### Simulation Mode (Recommended for testing)

```bash
python main.py --mode simulation
```

### Live Trading

```bash
python main.py --mode live --chain base
```

### CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `--mode` | `simulation` or `live` | `simulation` |
| `--chain` | Target blockchain (`base`, `eth`, `sol`) | `base` |
| `--interval` | Analysis interval in seconds | `300` |
| `--min-confidence` | Minimum sentiment confidence (0-1) | `0.7` |
| `--dry-run` | Log trades without executing | `false` |

### Example Workflows

**Monitor sentiment without trading:**
```bash
python main.py --mode simulation --dry-run
```

**Live trading on Base chain with 5-min intervals:**
```bash
python main.py --mode live --chain base --interval 300
```

## API Reference

### Pipeline Methods

```python
from swarmsentinel import SwarmPipeline

# Initialize pipeline
pipeline = SwarmPipeline(config_path=".env")

# Run single analysis cycle
result = pipeline.analyze(token="ETH")

# Get current market regime
regime = pipeline.get_regime()  # Returns: "bull", "bear", "sideways"

# Check sentiment score
score = pipeline.sentiment_score(token="BTC")  # Returns: -1.0 to 1.0
```

## Deployment

### Railway (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Docker

```bash
docker build -t swarmsentinel .
docker run -d --env-file .env swarmsentinel
```

## Project Structure

```
SwarmSentinel-v3/
├── main.py              # Entry point
├── pipeline/
│   ├── sentiment.py     # Node 1: Sentiment analysis
│   ├── whale.py         # Node 2: Whale tracking
│   ├── regime.py        # Node 3: Market regime
│   ├── strategy.py      # Node 4: Strategy selection
│   └── execution.py     # Node 5: Trade execution
├── utils/
│   ├── grok_client.py   # Grok API wrapper
│   └── telegram.py      # Alert system
├── config/
│   └── strategies.yaml  # Trading strategies
├── requirements.txt
├── .env.example
└── Dockerfile
```

## Related Projects

- [EchoForge](https://github.com/ivan09069/EchoForge) - Portfolio tracker
- [echoforge-texas-platform](https://github.com/ivan09069/echoforge-texas-platform) - Energy trading + PIPE token
- [JIT-Command-Center](https://github.com/ivan09069/JIT-Command-Center) - Monitoring dashboard

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**EchoForge Studios** | Built for Base chain DeFi
