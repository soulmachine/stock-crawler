# stock-crawler

Crawl US stocks  daily OHLCV data

## Explore Data

First, launch a Jupyter container:

```bash
docker run -it --rm -v $(pwd)/notebooks:/notebooks -v $(pwd)/data:/notebooks/data -p 8080:8080 soulmachine/jupyterlab
```

Then open <http://localhost:8080> in your browser, and start write Python code to explore the data!
