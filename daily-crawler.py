import json
import logging
import lzma
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests_cache
import yfinance as yf

session = requests_cache.CachedSession("yfinance.cache")
session.headers["User-agent"] = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
)

logging.basicConfig(level=logging.INFO)

with open("config.json", "rt") as f:
    SYMBOL_LIST = json.loads(f.read())["symbols"]


def fetch_all_history(symbol: str) -> str:
    output_file = os.path.join("./data", symbol + ".csv.xz")
    if os.path.exists(output_file):
        raise ValueError(f"{output_file} already exists")
    ticker = yf.Ticker(symbol, session=session)
    hist = ticker.history(period="max")
    if len(hist) == 0:
        raise ValueError(
            f"No history data found for this symbol, {symbol} may be delisted"
        )
    hist.to_csv(output_file, encoding="utf-8", index=True, header=True)
    return output_file


def fetch_daily_ohlcv(symbol: str, begin_day: str, end_day: str) -> bool:
    csv_file = os.path.join("./data", symbol + ".csv.xz")
    ticker = yf.Ticker(symbol, session=session)
    updates = ticker.history(start=begin_day, end=today)
    updates.to_csv(csv_file, mode="a", encoding="utf-8", index=True, header=False)


def read_last_day(symbol: str) -> Optional[str]:
    csv_file = os.path.join("./data", symbol + ".csv.xz")
    if not os.path.exists(csv_file):
        return None
    with lzma.open(csv_file, mode="rt") as f_in:
        last_line = None
        for line in f_in:
            last_line = line
        if last_line is None:
            return None
        return last_line.split(",")[0]


if __name__ == "__main__":
    for symbol in SYMBOL_LIST:
        last_day = read_last_day(symbol)
        if last_day is None:
            logging.info(f"Fetching all history data of {symbol}")
            fetch_all_history(symbol)
        else:
            today = datetime.utcnow().isoformat()[:10]
            begin_day = datetime.strptime(last_day, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            ) + timedelta(days=1)
            begin_day = str(begin_day.date())
            logging.info(f"Fetching {symbol} updates between {begin_day} and {today}")
            fetch_daily_ohlcv(symbol, begin_day, today)
