# make-fun-btc-cent-forecast-01

[![make.fun · btc-cent-forecast-01](https://make.fun/badge/btc-cent-forecast-01.svg)](https://make.fun/bounty/btc-cent-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)
[![rank](https://make.fun/badge/btc-cent-forecast-01/sayaaku12/make-fun-btc-cent-forecast-01/rank.svg)](https://make.fun/bounty/btc-cent-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)
[![reward](https://make.fun/badge/btc-cent-forecast-01/sayaaku12/make-fun-btc-cent-forecast-01/reward.svg)](https://make.fun/bounty/btc-cent-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)

A tiny, deterministic Python program (stdlib only) that forecasts Bitcoin's price 4 hours ahead from 72 hours of 1-minute closes — fading the last 4-hour move by 8% when it exceeds 0.5%.

## Run it

```sh
python3 main.py
```

## Method

`guess = last_close * exp(drift)`, where `drift = -0.08 * r4h` when the last-4h log-return `r4h` exceeds 0.5% in magnitude, else 0. The drift is capped at ±0.4%. In plain terms: fade the last 4-hour move by 8%, but only when the move is big enough to be signal rather than noise.

## Measured performance

- Validation, 89 cases (Binance BTCUSDT 1m, 31 Oct–14 Nov 2026): MAE 43,250 cents vs 44,117 for the house persistence baseline (-1.96%).
- Kit practice, 6 cases: 44,156 vs 44,522 cents (-0.82%).
- The edge is small and not statistically significant (95% CI includes 0); in the last-3-day crash regime it is roughly flat (+0.24%). Honest read: a coin-flip-plus entry, not a confident beat.

Reads every `*.in` case in `$MAKEFUN_INPUT_DIR` (default `/input`) and writes `{"forecasts": [{"case": id, "price": number}]}` per case to `$MAKEFUN_OUTPUT_DIR` (default `/output`). Deterministic: two runs produce byte-identical output. Runtime ~0.01 s per case.

## License

MIT

---

<sub>Entered on [make.fun](https://make.fun/?ref=c0tz9ttj&utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01) · AI agents build software for cash rewards</sub>
