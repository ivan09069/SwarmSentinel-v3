# SwarmSentinel

Automated mean-reversion crypto trading bot. Buys RSI dips below EMA50, sells at target profit or stop-loss. Runs 24/7 on Railway, trades BTC/ETH/SOL/XRP against USDC on Coinbase.

## How It Works

SwarmSentinel monitors 5-minute candles across four pairs. When RSI drops below 42 **and** price is below the 50-period EMA, it opens a $5 position. Exits happen at +0.8% take-profit, -0.6% stop-loss, or after 9 bars (45 min) max hold time.

```
Market Data → RSI Check (< 42?) → EMA50 Filter → BUY
                                                    ↓
                              SELL ← TP 0.8% / SL 0.6% / 9-bar timeout
```

## Parameters (v5)

| Parameter | Value |
|-----------|-------|
| BUY_RSI | 42 |
| SELL_RSI | 70 |
| Take Profit | 0.8% |
| Stop Loss | 0.6% |
| Max Hold | 9 bars (45 min) |
| Cycle | 300 seconds |
| Trade Size | $5 USDC |
| Daily Limit | $30 |
| Pairs | BTC-USDC, ETH-USDC, SOL-USDC, XRP-USDC |
| Mode | Mean reversion |

## Architecture

**v3** (this repo): LangGraph 5-node pipeline with Grok AI sentiment analysis and Kelly Criterion position sizing. Nodes: Sentinel → Analyst → Strategist → Risk Manager → Executor.

**v5** (live on Railway): Streamlined single-file Python bot focused on mean-reversion. Stripped the AI sentiment layer in favor of pure technical signals for reliability.

## Stack

- Python (pure stdlib on Termux, full deps on Railway)
- Coinbase Advanced Trade API
- RSI + EMA50 technical indicators
- Railway for 24/7 hosting

## Related Repos

- [SwarmOps](https://github.com/ivan09069/SwarmOps) — Multi-agent orchestrator for monitoring
- [trade-executor-service](https://github.com/ivan09069/trade-executor-service) — Multi-chain execution API
- [balance-monitor](https://github.com/ivan09069/balance-monitor) — Wallet balance tracking
- [arb-scanner](https://github.com/ivan09069/arb-scanner) — DEX arbitrage detection
- [whale-tracker](https://github.com/ivan09069/whale-tracker) — Large wallet movement alerts

## Deployment

Currently running on Railway (project ID: `e20ef10a-7244-4bbd-be6d-1d9065c6dbe0`). Also runs from Termux on Android at `~/swarm_sentinel/`.

## Roadmap

- [ ] Deploy `lmi_feed.py` (Liquidity Momentum Index as Kelly multiplier)
- [ ] Backtest OU pair scanner results (JPM/BAC best mean-reversion pair at ~8d half-life)
- [ ] Add Telegram trade notifications via EchoForge bot

## License

MIT
