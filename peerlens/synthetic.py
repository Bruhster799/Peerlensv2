"""Synthetic financial statements for any set of Nifty 500 companies.

Used for Demo mode (works offline, never rate-limited) and for the course's data-generator
requirement. Every company gets randomised parameters drawn around its industry's archetype.

Business rules built in:
  * revenue grows each year with noise; one industry-wide margin shock in FY2023
  * fixed assets = revenue / fixed-asset turnover; depreciation = 5% of fixed assets
  * interest = 9% of opening debt; tax = 25% of profit before tax (only when profitable)
  * equity grows by retained profit; cash is the balancing figure, so
    Total assets = Equity + Debt + Current liabilities always holds
"""
import zlib

import numpy as np
import pandas as pd

from .schema import ALL_COLUMNS

YEARS = ["FY2021", "FY2022", "FY2023", "FY2024", "FY2025"]
DEPRECIATION_RATE = 0.05
INTEREST_RATE = 0.09
TAX_RATE = 0.25
MIN_CASH_SHARE = 0.03

# margin = EBITDA / revenue, fa_turnover = revenue / fixed assets, leverage = debt / fixed assets,
# days = inventory, receivable and payable days, growth = average revenue growth, pe = typical P/E
DEFAULT_ARCHETYPE = dict(margin=0.16, fa_turnover=1.6, leverage=0.35, inventory_days=45,
                         receivable_days=40, payable_days=55, growth=0.11, pe=32, shock=-0.08,
                         depreciation_rate=DEPRECIATION_RATE, interest_rate=INTEREST_RATE)
ARCHETYPES = {
    "Information Technology": dict(margin=0.24, fa_turnover=6.0, leverage=0.05, inventory_days=0,
                                   receivable_days=70, payable_days=30, growth=0.12, pe=30, shock=-0.03),
    "Construction Materials": dict(margin=0.18, fa_turnover=0.9, leverage=0.30, inventory_days=35,
                                   receivable_days=12, payable_days=60, growth=0.10, pe=40, shock=-0.22),
    "Fast Moving Consumer Goods": dict(margin=0.21, fa_turnover=3.5, leverage=0.10, inventory_days=40,
                                       receivable_days=15, payable_days=65, growth=0.09, pe=55, shock=-0.10),
    "Metals & Mining": dict(margin=0.17, fa_turnover=1.0, leverage=0.55, inventory_days=70,
                            receivable_days=25, payable_days=60, growth=0.08, pe=14, shock=-0.25),
    "Healthcare": dict(margin=0.22, fa_turnover=2.2, leverage=0.15, inventory_days=90,
                       receivable_days=75, payable_days=60, growth=0.11, pe=38, shock=-0.05),
    "Automobile and Auto Components": dict(margin=0.13, fa_turnover=2.0, leverage=0.25, inventory_days=35,
                                           receivable_days=30, payable_days=70, growth=0.12, pe=28, shock=-0.12),
    "Power": dict(margin=0.30, fa_turnover=0.4, leverage=0.60, inventory_days=20,
                  receivable_days=60, payable_days=45, growth=0.09, pe=20, shock=-0.05),
    # For lenders the "fixed assets" stand in for the loan book: revenue is interest income, interest
    # expense is the cost of deposits and borrowings, and there is little physical depreciation.
    "Financial Services": dict(margin=0.80, fa_turnover=0.11, leverage=0.80, inventory_days=0,
                               receivable_days=5, payable_days=20, growth=0.15, pe=22, shock=-0.04,
                               depreciation_rate=0.004, interest_rate=0.065),
}


def archetype_for(industry):
    return {**DEFAULT_ARCHETYPE, **ARCHETYPES.get(industry, {})}


def _company_rows(company, symbol, archetype, rng):
    # Each company is a noisy version of its industry archetype
    size_revenue = float(rng.lognormal(mean=9.3, sigma=0.6))      # ≈ ₹11,000 crore median
    margin = max(archetype["margin"] * rng.normal(1, 0.18), 0.03)
    fa_turnover = archetype["fa_turnover"] * rng.normal(1, 0.15)
    if archetype["leverage"] >= 0.8:                                # lenders: leverage is structural
        leverage = min(archetype["leverage"] * rng.normal(1, 0.04), 0.88)
    else:
        leverage = min(max(archetype["leverage"] * rng.normal(1, 0.45), 0.0), 0.75)
        if rng.random() < 0.2:
            leverage = 0.0                                          # some companies are debt-free
    growth = archetype["growth"] * rng.normal(1, 0.35)
    days = {k: archetype[k] * max(rng.normal(1, 0.2), 0.3)
            for k in ("inventory_days", "receivable_days", "payable_days")}

    rows, equity, opening_debt = [], None, None
    for index, year in enumerate(YEARS):
        revenue = size_revenue * (1 + growth) ** index * rng.normal(1, 0.04)
        year_margin = margin * rng.normal(1, 0.07) * (1 + (archetype["shock"] if year == "FY2023" else 0))
        ebitda = revenue * year_margin
        fixed_assets = revenue / fa_turnover
        depreciation = fixed_assets * archetype["depreciation_rate"]
        debt = fixed_assets * leverage * rng.normal(1, 0.05)
        interest = (opening_debt if opening_debt is not None else debt) * archetype["interest_rate"]
        ebit = ebitda - depreciation
        pretax = ebit - interest
        tax = TAX_RATE * max(pretax, 0)
        net_income = pretax - tax

        inventory = revenue * days["inventory_days"] / 365
        receivables = revenue * days["receivable_days"] / 365
        current_liabilities = revenue * days["payable_days"] / 365

        if equity is None:
            opening_cash = revenue * rng.uniform(0.05, 0.20)
            equity = fixed_assets + inventory + receivables + opening_cash - debt - current_liabilities
        else:
            equity += net_income * (1 - rng.uniform(0.1, 0.4))     # retain 60-90% of profit

        cash = equity + debt + current_liabilities - fixed_assets - inventory - receivables
        if cash < MIN_CASH_SHARE * revenue:                          # borrow any shortfall
            debt += MIN_CASH_SHARE * revenue - cash
            cash = MIN_CASH_SHARE * revenue

        current_assets = inventory + receivables + cash
        rows.append(dict(company=company, symbol=symbol, year=year, revenue=revenue, ebitda=ebitda,
                         ebit=ebit, depreciation=depreciation, interest=interest, pretax_income=pretax,
                         tax=tax, net_income=net_income, total_assets=fixed_assets + current_assets,
                         current_assets=current_assets, current_liabilities=current_liabilities,
                         inventory=inventory, receivables=receivables, cash=cash, total_debt=debt,
                         equity=equity))
        opening_debt = debt
    return rows


def generate_financials(companies, industry, seed=42, inject_errors=False):
    """companies: DataFrame with 'company' and 'symbol'. Returns a table in the standard schema."""
    archetype = archetype_for(industry)
    rows = []
    for record in companies.itertuples(index=False):
        # a per-company generator keeps each company's numbers stable whichever peers are chosen
        company_rng = np.random.default_rng([seed, zlib.crc32(record.symbol.encode())])
        rows.extend(_company_rows(record.company, record.symbol, archetype, company_rng))
    data = pd.DataFrame(rows, columns=ALL_COLUMNS)
    numeric = data.columns[3:]
    data[numeric] = data[numeric].round(1)
    data["current_assets"] = data[["inventory", "receivables", "cash"]].sum(axis=1).round(1)
    fixed = (data["total_assets"] - data["current_assets"]).round(1)
    data["total_assets"] = (fixed + data["current_assets"]).round(1)
    data["equity"] = (data["total_assets"] - data["total_debt"] - data["current_liabilities"]).round(1)

    if inject_errors and len(data) >= 3 * len(YEARS):
        symbols = data["symbol"].unique()
        # 1) missing value   2) sign error   3) duplicated row
        data.loc[(data.symbol == symbols[1]) & (data.year == "FY2023"), "receivables"] = np.nan
        mask = (data.symbol == symbols[2]) & (data.year == "FY2022")
        data.loc[mask, "inventory"] = -data.loc[mask, "inventory"]
        data = pd.concat([data, data[(data.symbol == symbols[0]) & (data.year == "FY2024")]],
                         ignore_index=True)
    return data


def generate_market_snapshot(companies, industry, seed=42):
    """Market cap (₹ crore), P/E and P/B for demo mode, consistent with the generated financials."""
    financials = generate_financials(companies, industry, seed)
    latest = financials[financials.year == YEARS[-1]].set_index("symbol")
    rng = np.random.default_rng(seed + 1)
    pe_base = archetype_for(industry)["pe"]
    records = []
    for symbol, row in latest.iterrows():
        pe = max(pe_base * rng.normal(1, 0.3), 6)
        market_cap = max(row.net_income, row.revenue * 0.01) * pe
        records.append(dict(symbol=symbol, market_cap=market_cap, pe=pe,
                            pb=market_cap / row.equity if row.equity > 0 else np.nan))
    return pd.DataFrame(records)


def generate_prices(symbols, seed=42, days=250):
    """Simulated one-year daily price paths (geometric Brownian motion), rebased to 100."""
    rng = np.random.default_rng(seed + 7)
    dates = pd.bdate_range(end=pd.Timestamp("2026-09-25"), periods=days)
    prices = {}
    for symbol in symbols:
        drift, vol = rng.normal(0.12, 0.12) / days, rng.uniform(0.18, 0.40) / np.sqrt(days)
        prices[symbol] = 100 * np.exp(np.cumsum(rng.normal(drift, vol, days)))
    return pd.DataFrame(prices, index=dates)
