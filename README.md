# Ignition Scanner → Telegram

Scans Finviz Elite for **long "ignition" setups** — a stock coiled in a tight
base just under its highs, in a clean uptrend, ready to snap upward (your
"elastic band" squeeze) — and sends trade-ready alerts to your **iPhone via
Telegram**.

It runs **automatically** six times each US trading day (all times ET):

| Time | Session | Live volume filter |
|---|---|---|
| 07:00 | Early Pre-Market | no |
| 08:00 | Pre-Market | no |
| 09:25 | US Open (5 min before the bell) | yes |
| 09:45 | Opening Drive (first 15 min in) | yes |
| 10:30 | Morning Follow-Through | yes |
| 16:15 | After-Hours | yes |
 **No monthly subscription** — it runs
for free on GitHub Actions (your MacBook and iPhone can stay off).

---

## What each alert gives you

For each setup, ranked best-first:

- **Entry** — current price
- **Stop** — 1.5 × ATR below entry (just under the base)
- **Target** — 2:1 reward:risk
- Context: RSI, relative volume, distance to the 52-week high, ATR tightness

You still confirm on the daily chart before entering — the scan finds the
candidates, it doesn't pull the trigger for you.

---

## The setup logic (`config.py` — all tunable)

**Coarse net (Finviz filters):** price > $5, avg volume > 500K, price above the
20- & 50-day SMAs with 20 > 50 (uptrend), within 10% of the 52-week high, and —
when the market is live — relative volume ≥ 1.5×.

**Fine ignition test (`scanner.py`):** tight base (ATR < 7% of price), price
hugging the 20-day, RSI 50–70 (momentum building, not exhausted), near the
high, green-biased. Each survivor is scored — tighter base + nearer high + more
volume = higher score.

---

## Setup (one time, ~5 minutes)

### 1. Add your three secrets to GitHub
Repo → **Settings → Secrets and variables → Actions → New repository secret**.
Add each of these (values are never committed to the code):

| Secret | Where to get it |
|---|---|
| `FINVIZ_AUTH_TOKEN` | elite.finviz.com → Screener → **export** link → copy the `auth=` value from the URL |
| `TELEGRAM_BOT_TOKEN` | Telegram → **@BotFather** → your bot (looks like `123456789:AA...`) |
| `TELEGRAM_CHAT_ID` | Telegram → message **@userinfobot** → it replies with your id |

### 2. Turn it on
The schedule is already defined in `.github/workflows/scanner.yml`. It starts
running on the next scheduled slot. To test immediately: repo → **Actions →
Ignition Scanner → Run workflow** and pick a session — an alert should hit your
phone within a minute.

That's it. It now runs every weekday on its own.

---

## Running it locally instead (MacBook)

If you'd rather run it on the Mac:

```bash
pip install -r requirements.txt
cp .env.example .env        # then fill in your three values
python main.py --session open
```

Schedule it with `cron` (`crontab -e`) to run at your chosen times.

---

## Note on US daylight saving

GitHub cron is in UTC and doesn't shift with US clocks. The times in
`scanner.yml` target **US Eastern summer (EDT)**. When the US falls back to
winter (EST, roughly Nov–Mar), add one hour to each cron time so the "open"
scan stays at 09:25 ET — and update the matching `case` patterns in the
"Determine session" step to the same new times. (UK and US DST change on different dates, so there are a
couple of mismatched weeks each year — nudge the cron if a scan looks an hour
off.)

---

## TradingView levels overlay

**`tradingview/mb_levels_auto.pine` (recommended)** recalculates the MB watchlist
rule-based levels itself on every chart, every day - entry (dip-buy or breakout),
stop, TP1, TP2, exit line and support for stocks, plus the category
(STRONG / BUILDING / WEAKENING), keep/remove check and today's hits. On
futures, indexes and gold (NQ1!, GC1!, NKD1!, NI225...) it draws a trend-based
trade plan - LONG above yesterday's high when above the 20d & 50d, SHORT below
yesterday's low when under both, both plans when in between - each with entry,
stop (2 ATR), TP1 (2R) and TP2 (3R), plus the 1-month high/low, 20/50/200-day
averages and the overnight high and low.
Nothing to update by hand.

`tradingview/trade_levels.pine` is the fixed 2026-10-27 snapshot.

TradingView (web or desktop, not the phone app) -> **Pine Editor** -> paste ->
**Save** -> **Add to chart**. It then appears on the phone under
Indicators -> My scripts.
