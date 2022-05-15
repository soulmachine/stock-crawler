# stock-crawler

Crawl US stocks  daily OHLCV data

## Explore Data

First, launch a Jupyter container:

```bash
docker run -it --rm -v $(pwd)/notebooks:/notebooks -v $(pwd)/data:/notebooks/data -p 8080:8080 soulmachine/jupyterlab
```

Second, open <http://localhost:8080> in your browser, enther the default password `soulmachine`, and start to write Python code to explore the data!
