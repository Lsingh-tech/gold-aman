"""
Send formatted scan results to Telegram (lands on your iPhone).

Uses the Bot API sendMessage endpoint. No third-party library needed.
"""

import html
import requests

import config

API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def _format(session_label, setups):
    """Build one HTML message for a list of setups."""
    lines = [f"<b>🚀 Ignition Scan — {html.escape(session_label)}</b>"]

    if not setups:
        lines.append("\nNo setups passed the filters this run.")
        return "\n".join(lines)

    for s in setups:
        rr = f"{s['rr']}:1" if s["rr"] else "—"
        extra = []
        if s["rsi"] is not None:
            extra.append(f"RSI {int(s['rsi'])}")
        if s["relvol"] is not None:
            extra.append(f"RelVol {s['relvol']}x")
        if s["dist_high"] is not None:
            extra.append(f"{s['dist_high']}% to 52wH")
        extra.append(f"ATR {s['atr_pct']}%")

        lines.append(
            f"\n<b>${html.escape(s['ticker'])}</b>  (score {s['score']})\n"
            f"  Entry <b>{s['entry']}</b>  •  Stop <b>{s['stop']}</b>  •  "
            f"Target <b>{s['target']}</b>  ({rr})\n"
            f"  <i>{' · '.join(extra)}</i>"
        )

    lines.append(
        "\n<i>Confirm on the daily chart before entering. "
        "Stops are 1.5×ATR, targets 2:1.</i>"
    )
    return "\n".join(lines)


def send(session_label, setups):
    """Send the results. Returns True on success. Raises on config errors."""
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN and/or TELEGRAM_CHAT_ID are not set. Add them "
            "as environment variables (locally in .env, or GitHub secrets)."
        )

    if not setups and not config.NOTIFY_WHEN_EMPTY:
        return False

    text = _format(session_label, setups)
    url = API_URL.format(token=config.TELEGRAM_BOT_TOKEN)
    resp = requests.post(
        url,
        json={
            "chat_id": config.TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return True
