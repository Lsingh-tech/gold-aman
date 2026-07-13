"""
The ignition / squeeze setup logic.

The idea (your "elastic band"): a stock coils into a tight base just under its
highs, in a clean uptrend, then snaps upward hard as volume comes in. We use
Finviz to find the coil, then score how close each name is to the snap, and
attach an ATR-based entry / stop / target so the message is trade-ready.

Longs only - that is where the edge is.
"""

import config


def _num(value):
    """Parse a Finviz cell into a float. Handles '%', '-', 'B'/'M'/'K', ''."""
    if value is None:
        return None
    v = str(value).strip().replace("%", "").replace(",", "")
    if v in ("", "-", "N/A"):
        return None
    mult = 1.0
    if v[-1:] in ("B", "M", "K"):
        mult = {"B": 1e9, "M": 1e6, "K": 1e3}[v[-1]]
        v = v[:-1]
    try:
        return float(v) * mult
    except ValueError:
        return None


def _field(row, *candidates):
    """Find a column value by fuzzy header match (case-insensitive substring)."""
    for key in row:
        low = key.lower()
        for cand in candidates:
            if cand.lower() in low:
                return row[key]
    return None


def evaluate(row):
    """
    Return a dict describing the setup for one row, or None if it fails the
    ignition criteria. Included rows carry a `score` (higher = closer to snap).
    """
    ticker = _field(row, "Ticker")
    price = _num(_field(row, "Price"))
    atr = _num(_field(row, "Average True Range", "ATR"))
    sma20 = _num(_field(row, "SMA20", "20-Day"))
    rsi = _num(_field(row, "Relative Strength Index", "RSI"))
    relvol = _num(_field(row, "Relative Volume", "Rel Volume"))
    change = _num(_field(row, "Change"))
    high52 = _num(_field(row, "52-Week High", "52W High"))

    if not ticker or not price or not atr:
        return None

    atr_pct = (atr / price) * 100.0

    # --- Hard gates: must be a tight base, in position, with momentum ----
    if atr_pct > config.MAX_ATR_PCT:
        return None
    if sma20 is not None and not (config.SMA20_MIN_PCT <= sma20 <= config.SMA20_MAX_PCT):
        return None
    if rsi is not None and not (config.RSI_MIN <= rsi <= config.RSI_MAX):
        return None
    if high52 is not None and high52 < -config.MAX_BELOW_52W_HIGH:
        return None
    if change is not None and change < config.MIN_CHANGE_PCT:
        return None

    # --- Score: reward tightness, proximity to the high, and volume -------
    score = 0.0
    score += max(0.0, config.MAX_ATR_PCT - atr_pct) * 2.0          # tighter = better
    if high52 is not None:
        score += max(0.0, config.MAX_BELOW_52W_HIGH + high52) * 1.5  # nearer high = better
    if relvol is not None:
        score += min(relvol, 5.0) * 3.0                             # more volume = ignition
    if rsi is not None:
        score += max(0.0, 65.0 - abs(rsi - 60.0))                  # sweet spot ~60

    entry = price
    stop = round(entry - config.STOP_ATR_MULT * atr, 2)
    target = round(entry + config.TARGET_ATR_MULT * atr, 2)
    risk = entry - stop
    reward = target - entry
    rr = round(reward / risk, 2) if risk > 0 else None

    return {
        "ticker": ticker,
        "price": round(price, 2),
        "entry": round(entry, 2),
        "stop": stop,
        "target": target,
        "rr": rr,
        "atr_pct": round(atr_pct, 1),
        "rsi": round(rsi, 0) if rsi is not None else None,
        "relvol": round(relvol, 2) if relvol is not None else None,
        "change": round(change, 1) if change is not None else None,
        "dist_high": round(high52, 1) if high52 is not None else None,
        "score": round(score, 1),
    }


def scan(rows):
    """Evaluate every row, drop failures, rank best-first, cap to MAX_RESULTS."""
    setups = [s for s in (evaluate(r) for r in rows) if s]
    setups.sort(key=lambda s: s["score"], reverse=True)
    return setups[: config.MAX_RESULTS]
