# stock-crawler

Crawl US stocks  daily OHLCV data

## Explore Data

First, launch a Jupyter container:

```bash
docker run -it --rm -v $(pwd)/notebooks:/notebooks -v $(pwd)/data:/notebooks/data -p 8080:8080 soulmachine/jupyterlab
```

Second, open <http://localhost:8080> in your browser, enther the default password `soulmachine`, and start to write Python code to explore the data!


## Directory Structure

* `data/options/SYMBOL/summary` contains all calls and puts of this symbol, similar to the webpage <https://www.barchart.com/stocks/quotes/TSLA/options>
* `data/options/SYMBOL/history/CONTRACT_CODE.csv.xyz` contains all OHLCV data of a single contract, similar to the webpage <https://www.barchart.com/stocks/quotes/TSLA%7C20220520%7C750.00C/price-history/historical>.

## References

* <https://data.nasdaq.com/>
* <https://www.nasdaq.com/market-activity/quotes/historical>
* <https://github.com/ranaroussi/yfinance>
