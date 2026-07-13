"""
Thin client for the Finviz Elite export (CSV) endpoint.

Finviz Elite lets you export the screener as CSV via export.ashx using your
account's `auth` token. We request the "Technical" column set (v=171) which
includes ATR, SMA distances, RSI, relative volume and 52-week-high distance -
everything the ignition logic needs.
"""

import csv
import io
import requests

import config

EXPORT_URL = "https://elite.finviz.com/export.ashx"


def fetch_screener(filters, order="-relativevolume"):
    """
    Pull the screener as a list of dict rows (keyed by CSV header name).

    `filters` is a list of Finviz filter codes; they are joined with commas.
    Raises RuntimeError with a helpful message if the token is missing or the
    request fails.
    """
    if not config.FINVIZ_AUTH_TOKEN:
        raise RuntimeError(
            "FINVIZ_AUTH_TOKEN is not set. Add it as an environment variable "
            "(locally in .env, or as a GitHub Actions secret)."
        )

    params = {
        "v": "171",                      # Technical view = the columns we need
        "f": ",".join(filters),
        "o": order,                      # order by relative volume, high first
        "auth": config.FINVIZ_AUTH_TOKEN,
    }

    try:
        resp = requests.get(EXPORT_URL, params=params, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Finviz request failed: {exc}") from exc

    text = resp.text
    # Finviz returns an HTML/error page (not CSV) if the token is bad.
    if not text.lstrip().lower().startswith('"no.') and "," not in text.split("\n", 1)[0]:
        raise RuntimeError(
            "Finviz did not return CSV - the auth token is probably invalid "
            "or your Elite subscription has lapsed."
        )

    reader = csv.DictReader(io.StringIO(text))
    return list(reader)
