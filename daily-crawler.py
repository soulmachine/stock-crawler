import json
import logging
import lzma
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from symtable import SymbolTableFactory
from typing import List, Optional

import requests_cache
import yfinance as yf

session = requests_cache.CachedSession("yfinance.cache")
session.headers["User-agent"] = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
)

logging.basicConfig(level=logging.INFO)

with open("config.json", "rt") as f:
    SYMBOL_LIST = json.loads(f.read())["symbols"]


def fetch_all_history(symbol: str, output_file: str) -> bool:
    if os.path.exists(output_file):
        raise ValueError(f"{output_file} already exists")
    ticker = yf.Ticker(symbol, session=session)
    hist = ticker.history(period="max")
    if len(hist) == 0:
        return False
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    hist.to_csv(output_file, encoding="utf-8", index=True, header=True)
    return True


def fetch_daily_ohlcv(symbol: str, begin_day: str, end_day: str, csv_file: str) -> bool:
    assert os.path.exists(csv_file)
    ticker = yf.Ticker(symbol, session=session)
    updates = ticker.history(start=begin_day, end=end_day)
    if len(updates) == 0:
        return False
    else:
        updates.to_csv(csv_file, mode="a", encoding="utf-8", index=True, header=False)
        return True


def fetch_one_symbol(symbol: str, csv_file: str) -> bool:
    """Choose between fetch_all_history and fetch_daily_ohlcv."""
    last_day = read_last_day(csv_file)
    if last_day is None:
        logging.info("Fetching all history data of %s", symbol)
        return fetch_all_history(symbol, csv_file)
    else:
        today = datetime.utcnow().isoformat()[:10]
        begin_day = datetime.strptime(last_day, "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        ) + timedelta(days=1)
        begin_day = str(begin_day.date())
        logging.info("Fetching %s updates between %s and %s", symbol, begin_day, today)
        fetch_daily_ohlcv(symbol, begin_day, today, csv_file)
        return True


def read_last_day(csv_file: str) -> Optional[str]:
    if not os.path.exists(csv_file):
        return None
    with lzma.open(csv_file, mode="rt") as f_in:
        last_line = None
        for line in f_in:
            last_line = line
        if last_line is None:
            return None
        return last_line.split(",")[0]


def get_option_symbols(symbol: str) -> List[str]:
    symbols: List[str] = []
    ticker = yf.Ticker(symbol, session=session)
    if len(ticker.options) == 0:
        return []
    os.makedirs(os.path.join("data", "options", symbol, "summary"), exist_ok=True)
    for day in ticker.options:
        option_chain = ticker.option_chain(day)
        calls = option_chain.calls
        calls.to_csv(
            os.path.join("data", "options", symbol, "summary", f"calls-{day}.csv.xz"),
            encoding="utf-8",
            index=False,
            header=True,
        )
        calls = calls[calls["inTheMoney"] == True]
        puts = option_chain.puts
        puts.to_csv(
            os.path.join("data", "options", symbol, "summary", f"puts-{day}.csv.xz"),
            encoding="utf-8",
            index=False,
            header=True,
        )
        puts = puts[puts["inTheMoney"] == True]
        call_symbols = list(calls["contractSymbol"].values)
        put_symbols = list(puts["contractSymbol"].values)
        logging.info(
            "%s %s has %d calls and %d puts",
            symbol,
            day,
            len(call_symbols),
            len(put_symbols),
        )
        symbols.extend(call_symbols)
        symbols.extend(put_symbols)
    symbols.sort()  # sorted by date
    return symbols


if __name__ == "__main__":
    for symbol in SYMBOL_LIST:
        fetch_one_symbol(symbol, os.path.join("data", "stocks", symbol + ".csv.xz"))

        logging.info("Fetching options of %s", symbol)
        option_symbols = get_option_symbols(symbol)
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            args_list = [
                (
                    option_symbol,
                    os.path.join(
                        "data", "options", symbol, "history", option_symbol + ".csv.xz"
                    ),
                )
                for option_symbol in option_symbols
            ]
            executor.map(lambda x: fetch_one_symbol(x[0], x[1]), args_list)
