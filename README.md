# PeerLens: Nifty 500 peer analysis

Pick an industry in the Nifty 500, choose 2 to 8 peers, and compare their profitability, debt and
efficiency. The app rates every ratio green, amber or red, ranks the peers, writes plain-language
recommendations for a focal company, and exports a live Excel dashboard.

## Run it on your computer
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud (free)
1. Create a new public GitHub repository and upload everything in this folder (keep the folder structure,
   including `data/`, `peerlens/` and `.streamlit/`).
2. Go to https://share.streamlit.io, sign in with GitHub, click **Create app**.
3. Choose the repository, branch `main`, main file `app.py`, then **Deploy**.

## Data modes
- **Live market data:** annual statements, market caps and prices from Yahoo Finance (via `yfinance`),
  converted to ₹ crore. Yahoo limits how often one server can ask, so if you see a rate-limit
  message, wait a few minutes or switch to demo data.
- **Demo data (offline):** a synthetic generator creates realistic statements for any chosen peers,
  using industry-specific assumptions. Optional planted errors show the data-quality checks at work.
  Demo numbers are not the real financials of these companies.

The Nifty 500 list loads from NSE, then a GitHub mirror, then `data/nifty500.csv` (bundled snapshot).

## Project structure
| File | What it does |
|---|---|
| `app.py` | The Streamlit interface: industry, peers, analysis, export |
| `peerlens/universe.py` | Loads the Nifty 500 constituent list |
| `peerlens/live.py` | Fetches and standardises Yahoo Finance statements |
| `peerlens/synthetic.py` | Synthetic data generator (industry archetypes, shocks, planted errors) |
| `peerlens/validator.py` | Data-quality checks and safe fixes |
| `peerlens/ratios.py` | Ratio definitions, ratings, scores, recommendations |
| `peerlens/pipeline.py` | Runs validation → ratios → scores → recommendations |
| `peerlens/charts.py` | All Plotly charts |
| `peerlens/excel_export.py` | Live Excel workbook with formulas, dropdowns and charts |
| `tests/test_core.py` | Edge-case tests (`python -m pytest -q`) |
