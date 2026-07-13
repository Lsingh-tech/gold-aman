"""
Central configuration for the Finviz -> Telegram ignition scanner.

Secrets are read from environment variables (or a local .env file) and are
NEVER hard-coded here. See .env.example for what to set.
"""

import os

try:
    # Optional: load a local .env when running on a Mac/PC. In GitHub Actions
    # the secrets come from the environment directly, so this is a no-op.
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


# --------------------------------------------------------------------------
# Secrets (set these as environment variables / GitHub Actions secrets)
# --------------------------------------------------------------------------
FINVIZ_AUTH_TOKEN = os.environ.get("FINVIZ_AUTH_TOKEN", "").strip()
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()


# --------------------------------------------------------------------------
# Pre-screen filters sent to Finviz (the "coarse net").
# These narrow the universe to liquid stocks in a clean uptrend that are
# coiled just under their highs. The fine "squeeze / ignition" logic runs
# afterwards in scanner.py on the columns Finviz returns.
#
# Filter codes are Finviz screener codes. If your Elite account rejects any
# of these, adjust them here - they are intentionally kept in one place.
# --------------------------------------------------------------------------
BASE_FILTERS = [
    "sh_price_o5",            # price over $5  (no penny stocks)
    "sh_avgvol_o500",         # avg volume over 500K  (liquid enough to trade)
    "ta_sma20_pa",            # price ABOVE the 20-day SMA
    "ta_sma50_pa",            # price ABOVE the 50-day SMA
    "ta_sma20_sa50",          # 20-day SMA above 50-day SMA (uptrend structure)
    "ta_highlow52w_b0to10h",  # within 10% of the 52-week high (coiled at highs)
]

# Extra filter added when the market is actually trading (relative volume is
# only meaningful once there is live volume - it is useless pre-market).
LIVE_VOLUME_FILTER = "sh_relvol_o1.5"  # today's volume >= 1.5x normal (ignition)


# --------------------------------------------------------------------------
# Fine "ignition / squeeze" thresholds (computed in Python from the CSV).
# Tune these to taste - they are the heart of the setup.
# --------------------------------------------------------------------------
MAX_ATR_PCT = 7.0          # ATR must be < 7% of price  (a TIGHT, coiled base)
SMA20_MIN_PCT = -1.0       # price no more than 1% BELOW the 20-day...
SMA20_MAX_PCT = 9.0        # ...and no more than 9% above (hugging the base)
RSI_MIN = 50.0             # momentum turning up...
RSI_MAX = 70.0             # ...but not yet overbought / exhausted
MAX_BELOW_52W_HIGH = 10.0  # within 10% of the 52-week high
MIN_CHANGE_PCT = -1.0      # allow a small red open, but bias to green (longs)

# Risk model for entry / stop / target (all ATR-based).
STOP_ATR_MULT = 1.5        # stop = entry - 1.5 * ATR (just under the base)
TARGET_ATR_MULT = 3.0      # target = entry + 3.0 * ATR (2:1 reward:risk)

# How many of the best-ranked setups to send per scan.
MAX_RESULTS = 8

# Send a short "nothing today" message so you know the scan actually ran.
NOTIFY_WHEN_EMPTY = True
