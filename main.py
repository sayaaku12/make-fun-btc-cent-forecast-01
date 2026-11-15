#!/usr/bin/env python3
"""btc-cent-forecast-01 entry (Python 3.13, stdlib only).

Reads each /input/<id>.in (72h of BTC 1-minute closes, 4,320 prices) and
writes /output/<id>.out with one forecast: the expected price 240 minutes
after the checkpoint. Score is mean absolute error in cents; the house
baseline is persistence (guess the checkpoint close), so this entry must
beat persistence, not just match it.

Method (v2): work in log prices. The 4h-ahead forecast is the checkpoint
close faded slightly against its own last-4h move — but only when that
move is material (>0.5%): small moves are noise and are left alone.
Measured on 89 out-of-sample-style Binance cases (checkpoints every 4h,
2026-10-31 -> 2026-11-14) this beats persistence by ~2%, and it also beats
persistence on the kit's own 6 practice cases (~1%); the edge is small and
not statistically significant (paired 95% CI includes 0), so the weight is
kept tiny (-0.08) and the drift is capped — the worst case is ~1% worse
than persistence, not a blow-up. Momentum in the same direction, 24h/48h
trend terms, volatility-scaled drift, and hour-of-day drift were all tested
and rejected: each won on one dataset and lost on the other, or lost in the
most recent (crash) regime. Deterministic: pure arithmetic on the input
prices, no randomness, no clock, no network.
"""

import json
import math
import os
from os import path

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

MIN_PRICE = 0.00001
MAX_PRICE = 9_999_999.99999

# v2 coefficients (measured; see NOTES.md for the full table):
#   K: minimum |4h log return| before fading it (moves below this are noise)
#   W: fade weight on the 4h log return (negative = contrarian)
#   CAP: max |drift| in log points
PARAMS = {"K": 0.005, "W": -0.08, "CAP": 0.004}


def forecast(prices, params=None):
    """Expected price 240 minutes after the last close in `prices`.

    Never raises on odd input: any bad value falls back to the checkpoint
    close (persistence), because an invalid case forfeits the prize while
    a persistence guess merely ties the baseline on that case.
    """
    p = params if params is not None else PARAMS
    if not prices:
        return 1.0
    n = len(prices)
    last = prices[-1]
    if not isinstance(last, (int, float)) or not math.isfinite(last) or last <= 0:
        # No usable checkpoint close: fall back to the last finite
        # positive price in the window, else 1.0 (still a valid guess).
        last = 1.0
        for x in reversed(prices):
            if isinstance(x, (int, float)) and math.isfinite(x) and x > 0:
                last = x
                break
    if n < 241:
        return last
    try:
        base = prices[-241]
        if base <= 0 or not math.isfinite(last) or not math.isfinite(base):
            return last
        r4h = math.log(last / base)
        if not math.isfinite(r4h):
            return last
        drift = p["W"] * r4h if abs(r4h) > p["K"] else 0.0
    except (ValueError, OverflowError, TypeError):
        return last
    cap = p["CAP"]
    if drift > cap:
        drift = cap
    elif drift < -cap:
        drift = -cap
    guess = last * math.exp(drift)
    guess = round(min(MAX_PRICE, max(MIN_PRICE, guess)) * 1e5) / 1e5
    return guess


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    names = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".in"))
    for name in names:
        case_id = name[: -len(".in")]
        with open(path.join(INPUT_DIR, name), "r", encoding="utf-8") as fh:
            case = json.load(fh)
        markets = case["markets"]
        if len(markets) != 1:
            raise ValueError(f"{name} does not hold exactly one market")
        price = forecast(markets[0]["prices"])
        out = {"forecasts": [{"case": case_id, "price": price}]}
        with open(path.join(OUTPUT_DIR, case_id + ".out"), "w", encoding="utf-8") as fh:
            fh.write(json.dumps(out) + "\n")


if __name__ == "__main__":
    main()
