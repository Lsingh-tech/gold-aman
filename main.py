"""
Entry point: run one scan for a given session and fire the Telegram alert.

Usage:
    python main.py --session open          # US regular open (default)
    python main.py --session premarket     # pre-market
    python main.py --session afterhours    # after-hours

Sessions differ only in whether live relative-volume is required (it isn't
meaningful pre-market) and in the label shown on the message.
"""

import argparse
import sys

import config
import finviz_client
import scanner
import telegram_notifier

SESSIONS = {
    "premarket": {"label": "Pre-Market", "use_live_volume": False},
    "open": {"label": "US Open", "use_live_volume": True},
    "afterhours": {"label": "After-Hours", "use_live_volume": True},
}


def run(session_key):
    session = SESSIONS[session_key]

    filters = list(config.BASE_FILTERS)
    if session["use_live_volume"]:
        filters.append(config.LIVE_VOLUME_FILTER)

    rows = finviz_client.fetch_screener(filters)
    setups = scanner.scan(rows)

    print(f"[{session['label']}] scanned {len(rows)} rows, {len(setups)} setups")
    for s in setups:
        print(f"  ${s['ticker']:<6} entry {s['entry']} stop {s['stop']} "
              f"target {s['target']} score {s['score']}")

    telegram_notifier.send(session["label"], setups)
    return setups


def main():
    parser = argparse.ArgumentParser(description="Finviz -> Telegram ignition scanner")
    parser.add_argument(
        "--session",
        choices=list(SESSIONS),
        default="open",
        help="Which US market session to scan for.",
    )
    args = parser.parse_args()

    try:
        run(args.session)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
