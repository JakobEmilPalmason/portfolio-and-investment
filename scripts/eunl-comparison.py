#!/usr/bin/env python3
"""
EUNL vs Icelandic Savings Account — Real Purchasing-Power Comparison

Fetches monthly data for:
  - EUNL (iShares Core MSCI World UCITS ETF) from Yahoo Finance
  - EUR/ISK exchange rate from Yahoo Finance
  - Icelandic CPI from Statistics Iceland (px.hagstofa.is)

Computes lump-sum and monthly-DCA scenarios, both nominal and CPI-adjusted,
then writes an Excel workbook with embedded charts.

Usage:
    python3 scripts/eunl-comparison.py
    python3 scripts/eunl-comparison.py --lump 2000000 --monthly 100000 --savings-rate 4.5
    python3 scripts/eunl-comparison.py --start 2015-01 --output my-comparison.xlsx
"""

import argparse
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf
import xlsxwriter


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def fetch_eunl_monthly() -> pd.Series:
    """Fetch EUNL.DE (Xetra) monthly close prices in EUR."""
    ticker = yf.Ticker("EUNL.DE")
    hist = ticker.history(period="max")
    if hist.empty:
        raise SystemExit("ERROR: Could not fetch EUNL.DE price history")
    monthly = hist["Close"].resample("ME").last().dropna()
    monthly.index = monthly.index.tz_localize(None)
    return monthly.rename("eunl_eur")


def fetch_eurisk_monthly() -> pd.Series:
    """Fetch EUR/ISK monthly close from Yahoo Finance."""
    ticker = yf.Ticker("EURISK=X")
    hist = ticker.history(period="max")
    if hist.empty:
        raise SystemExit("ERROR: Could not fetch EUR/ISK exchange rate history")
    monthly = hist["Close"].resample("ME").last().dropna()
    monthly.index = monthly.index.tz_localize(None)
    return monthly.rename("eurisk")


def fetch_icelandic_cpi() -> pd.Series:
    """Fetch Icelandic CPI index from Statistics Iceland PX-Web API."""
    url = "https://px.hagstofa.is/pxen/api/v1/en/Efnahagur/visitolur/1_vnv/1_vnv/VIS01000.px"

    # First, get available months
    with urllib.request.urlopen(url, timeout=15) as resp:
        meta = json.loads(resp.read())

    months = None
    for v in meta.get("variables", []):
        if v.get("code") == "Month":
            months = v["values"]
            break
    if not months:
        raise SystemExit("ERROR: Could not parse CPI month list from Statistics Iceland")

    query = {
        "query": [
            {"code": "Index", "selection": {"filter": "item", "values": ["CPI"]}},
            {"code": "Item", "selection": {"filter": "item", "values": ["index"]}},
            {"code": "Month", "selection": {"filter": "item", "values": months}},
        ],
        "response": {"format": "json"},
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(query).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    records = {}
    for row in data.get("data", []):
        month_str = row["key"][0]  # e.g. "2009M10"
        value = float(row["values"][0])
        year, mon = month_str.split("M")
        # Use month-end date to align with price data
        dt = pd.Timestamp(int(year), int(mon), 1) + pd.offsets.MonthEnd(0)
        records[dt] = value

    series = pd.Series(records, name="cpi").sort_index()
    return series


# ---------------------------------------------------------------------------
# Computation
# ---------------------------------------------------------------------------

def build_dataframe(eunl: pd.Series, eurisk: pd.Series, cpi: pd.Series,
                    start: str | None) -> pd.DataFrame:
    """Align all three series on common month-end dates."""
    df = pd.DataFrame({"eunl_eur": eunl, "eurisk": eurisk, "cpi": cpi})
    df = df.dropna()

    if start:
        cutoff = pd.Timestamp(start + "-01") + pd.offsets.MonthEnd(0)
        df = df[df.index >= cutoff]

    if len(df) < 2:
        raise SystemExit("ERROR: Not enough overlapping data after alignment")

    df["eunl_isk"] = df["eunl_eur"] * df["eurisk"]
    df["cpi_factor"] = df["cpi"] / df["cpi"].iloc[0]

    return df


def compute_lump_sum(df: pd.DataFrame, lump: float, savings_rate: float) -> pd.DataFrame:
    """Lump-sum scenario: invest lump ISK at t=0."""
    ls = pd.DataFrame(index=df.index)

    # EUNL: buy units at t=0, track value
    units = lump / df["eunl_isk"].iloc[0]
    ls["eunl_nominal"] = units * df["eunl_isk"]
    ls["eunl_real"] = ls["eunl_nominal"] / df["cpi_factor"]

    # Savings account: compound monthly
    monthly_rate = savings_rate / 100.0 / 12.0
    balances = [lump]
    for _ in range(1, len(df)):
        balances.append(balances[-1] * (1 + monthly_rate))
    ls["account_nominal"] = balances
    ls["account_real"] = ls["account_nominal"] / df["cpi_factor"]

    # Index series (base = 100)
    ls["eunl_nom_idx"] = ls["eunl_nominal"] / ls["eunl_nominal"].iloc[0] * 100
    ls["account_nom_idx"] = ls["account_nominal"] / ls["account_nominal"].iloc[0] * 100
    ls["eunl_real_idx"] = ls["eunl_real"] / ls["eunl_real"].iloc[0] * 100
    ls["account_real_idx"] = ls["account_real"] / ls["account_real"].iloc[0] * 100

    # Drawdown
    ls["eunl_peak"] = ls["eunl_nom_idx"].cummax()
    ls["eunl_drawdown"] = ls["eunl_nom_idx"] / ls["eunl_peak"] - 1

    return ls


def compute_dca(df: pd.DataFrame, monthly_isk: float, savings_rate: float) -> pd.DataFrame:
    """Monthly DCA scenario."""
    dca = pd.DataFrame(index=df.index)

    cumulative_units = 0.0
    total_contributed = 0.0
    account_balance = 0.0
    monthly_rate = savings_rate / 100.0 / 12.0

    units_list, cum_units_list = [], []
    eunl_values, contrib_list = [], []
    acct_list = []

    for i, (dt, row) in enumerate(df.iterrows()):
        # Contribute this month
        total_contributed += monthly_isk
        units_bought = monthly_isk / row["eunl_isk"]
        cumulative_units += units_bought

        # Account: add contribution then compound
        account_balance += monthly_isk
        account_balance *= (1 + monthly_rate)

        units_list.append(units_bought)
        cum_units_list.append(cumulative_units)
        eunl_values.append(cumulative_units * row["eunl_isk"])
        contrib_list.append(total_contributed)
        acct_list.append(account_balance)

    dca["total_contributed"] = contrib_list
    dca["eunl_value"] = eunl_values
    dca["account_value"] = acct_list
    dca["units_bought"] = units_list
    dca["cumulative_units"] = cum_units_list
    dca["eunl_real"] = dca["eunl_value"] / df["cpi_factor"]
    dca["account_real"] = dca["account_value"] / df["cpi_factor"]
    dca["contributed_real"] = dca["total_contributed"] / df["cpi_factor"]

    return dca


def compute_rolling_win_rates(df: pd.DataFrame, savings_rate: float) -> dict:
    """For every possible entry month, simulate lump-sum EUNL vs savings for N years.

    Returns win rates: what % of all possible N-year windows did EUNL beat
    the savings account in real ISK terms?
    """
    eunl_isk = df["eunl_isk"].values
    cpi = df["cpi"].values
    monthly_rate = savings_rate / 100.0 / 12.0
    horizons = [3, 5, 7, 10]  # years
    n = len(df)

    results = {}
    for h_years in horizons:
        h_months = h_years * 12
        if n <= h_months:
            results[h_years] = {"win_rate": None, "windows": 0, "wins": 0,
                                "avg_eunl_gain": None, "avg_acct_gain": None,
                                "worst_eunl_real": None}
            continue

        wins = 0
        total = 0
        eunl_gains = []
        acct_gains = []
        worst_eunl_real = float("inf")

        for start_i in range(n - h_months):
            end_i = start_i + h_months
            # EUNL real return
            eunl_start_isk = eunl_isk[start_i]
            eunl_end_isk = eunl_isk[end_i]
            cpi_factor = cpi[end_i] / cpi[start_i]
            eunl_real_return = (eunl_end_isk / eunl_start_isk) / cpi_factor - 1

            # Savings real return
            acct_nominal_growth = (1 + monthly_rate) ** h_months
            acct_real_return = acct_nominal_growth / cpi_factor - 1

            if eunl_real_return > acct_real_return:
                wins += 1
            total += 1
            eunl_gains.append(eunl_real_return * 100)
            acct_gains.append(acct_real_return * 100)
            if eunl_real_return < worst_eunl_real:
                worst_eunl_real = eunl_real_return

        results[h_years] = {
            "win_rate": wins / total * 100,
            "windows": total,
            "wins": wins,
            "avg_eunl_gain": sum(eunl_gains) / len(eunl_gains),
            "avg_acct_gain": sum(acct_gains) / len(acct_gains),
            "worst_eunl_real": worst_eunl_real * 100,
        }

    return results


def compute_worst_entry(df: pd.DataFrame, savings_rate: float) -> dict:
    """Find the worst possible entry month for EUNL and how long until it
    still beat the savings account in real ISK terms."""
    eunl_isk = df["eunl_isk"].values
    cpi = df["cpi"].values
    dates = df.index
    monthly_rate = savings_rate / 100.0 / 12.0
    n = len(df)

    # Find the month where EUNL ISK price was highest relative to its future
    # (i.e., worst entry = biggest subsequent real drawdown)
    worst_entry_i = 0
    worst_subsequent_real_return = float("inf")

    for start_i in range(n - 1):
        # Look at worst point after this entry
        for end_i in range(start_i + 1, n):
            cpi_factor = cpi[end_i] / cpi[start_i]
            real_return = (eunl_isk[end_i] / eunl_isk[start_i]) / cpi_factor - 1
            if real_return < worst_subsequent_real_return:
                worst_subsequent_real_return = real_return
                worst_entry_i = start_i

    # From worst entry, find how many months until EUNL real > savings real
    months_to_recover = None
    for offset in range(1, n - worst_entry_i):
        end_i = worst_entry_i + offset
        cpi_factor = cpi[end_i] / cpi[worst_entry_i]
        eunl_real = (eunl_isk[end_i] / eunl_isk[worst_entry_i]) / cpi_factor - 1
        acct_real = ((1 + monthly_rate) ** offset) / cpi_factor - 1
        if eunl_real > acct_real:
            months_to_recover = offset
            break

    # Current standing from worst entry
    cpi_factor_now = cpi[-1] / cpi[worst_entry_i]
    months_held = n - 1 - worst_entry_i
    eunl_real_now = (eunl_isk[-1] / eunl_isk[worst_entry_i]) / cpi_factor_now - 1
    acct_real_now = ((1 + monthly_rate) ** months_held) / cpi_factor_now - 1

    return {
        "worst_entry_date": dates[worst_entry_i].strftime("%b %Y"),
        "worst_entry_idx": worst_entry_i,
        "months_to_beat_savings": months_to_recover,
        "years_to_beat_savings": months_to_recover / 12 if months_to_recover else None,
        "eunl_real_return_now": eunl_real_now * 100,
        "acct_real_return_now": acct_real_now * 100,
        "still_ahead": eunl_real_now > acct_real_now,
    }


def compute_summary(df: pd.DataFrame, ls: pd.DataFrame, dca: pd.DataFrame,
                    lump: float, monthly_isk: float, savings_rate: float) -> dict:
    """Compute summary statistics."""
    n_months = len(df)
    years = n_months / 12.0
    total_cpi = (df["cpi_factor"].iloc[-1] - 1) * 100

    def cagr(start, end, y):
        if start <= 0:
            return 0.0
        return ((end / start) ** (1 / y) - 1) * 100

    # Worst 12-month rolling return for EUNL lump
    if n_months > 12:
        rolling_12m = ls["eunl_nom_idx"].pct_change(12).dropna()
        worst_12m = rolling_12m.min() * 100
    else:
        worst_12m = 0.0

    # Rolling win rates and worst entry
    win_rates = compute_rolling_win_rates(df, savings_rate)
    worst_entry = compute_worst_entry(df, savings_rate)

    return {
        "period_start": df.index[0].strftime("%b %Y"),
        "period_end": df.index[-1].strftime("%b %Y"),
        "n_months": n_months,
        "years": years,
        "lump": lump,
        "monthly": monthly_isk,
        "savings_rate": savings_rate,
        # Lump sum
        "ls_eunl_nominal": ls["eunl_nominal"].iloc[-1],
        "ls_eunl_real": ls["eunl_real"].iloc[-1],
        "ls_account_nominal": ls["account_nominal"].iloc[-1],
        "ls_account_real": ls["account_real"].iloc[-1],
        "ls_eunl_cagr_nom": cagr(lump, ls["eunl_nominal"].iloc[-1], years),
        "ls_eunl_cagr_real": cagr(lump, ls["eunl_real"].iloc[-1], years),
        "ls_acct_cagr_nom": cagr(lump, ls["account_nominal"].iloc[-1], years),
        "ls_acct_cagr_real": cagr(lump, ls["account_real"].iloc[-1], years),
        # DCA
        "dca_contributed": dca["total_contributed"].iloc[-1],
        "dca_eunl_nominal": dca["eunl_value"].iloc[-1],
        "dca_eunl_real": dca["eunl_real"].iloc[-1],
        "dca_account_nominal": dca["account_value"].iloc[-1],
        "dca_account_real": dca["account_real"].iloc[-1],
        # Risk
        "max_drawdown": ls["eunl_drawdown"].min() * 100,
        "worst_12m_return": worst_12m,
        "total_cpi_inflation": total_cpi,
        # Selling points
        "win_rates": win_rates,
        "worst_entry": worst_entry,
    }


# ---------------------------------------------------------------------------
# Excel output
# ---------------------------------------------------------------------------

COLORS = {
    "eunl": "#1B6B93",
    "account": "#E8A317",
    "contributed": "#999999",
    "drawdown": "#CC4444",
    "bg_header": "#2C3E50",
    "bg_alt": "#F7F9FC",
}


def write_excel(path: Path, df: pd.DataFrame, ls: pd.DataFrame,
                dca: pd.DataFrame, summary: dict):
    """Write Excel workbook with data sheets and charts."""
    wb = xlsxwriter.Workbook(str(path), {"default_date_format": "yyyy-mm"})

    # Formats
    header_fmt = wb.add_format({
        "bold": True, "bg_color": COLORS["bg_header"],
        "font_color": "white", "border": 1,
    })
    date_fmt = wb.add_format({"num_format": "yyyy-mm", "border": 1})
    num_fmt = wb.add_format({"num_format": "#,##0.00", "border": 1})
    int_fmt = wb.add_format({"num_format": "#,##0", "border": 1})
    pct_fmt = wb.add_format({"num_format": "0.0%", "border": 1})
    money_fmt = wb.add_format({"num_format": "#,##0", "border": 1})
    bold_fmt = wb.add_format({"bold": True})
    bold_money = wb.add_format({"bold": True, "num_format": "#,##0"})
    bold_pct = wb.add_format({"bold": True, "num_format": "0.0%"})

    n = len(df)

    # -- Sheet 1: Raw Data --
    ws1 = wb.add_worksheet("Raw Data")
    cols1 = ["Date", "EUNL (EUR)", "EUR/ISK", "EUNL (ISK)", "CPI Index", "CPI Factor"]
    for c, name in enumerate(cols1):
        ws1.write(0, c, name, header_fmt)
    for r in range(n):
        ws1.write_datetime(r + 1, 0, df.index[r].to_pydatetime(), date_fmt)
        ws1.write_number(r + 1, 1, df["eunl_eur"].iloc[r], num_fmt)
        ws1.write_number(r + 1, 2, df["eurisk"].iloc[r], num_fmt)
        ws1.write_number(r + 1, 3, df["eunl_isk"].iloc[r], num_fmt)
        ws1.write_number(r + 1, 4, df["cpi"].iloc[r], num_fmt)
        ws1.write_number(r + 1, 5, df["cpi_factor"].iloc[r], num_fmt)
    ws1.set_column(0, 0, 12)
    ws1.set_column(1, 5, 14)

    # -- Sheet 2: Lump Sum --
    ws2 = wb.add_worksheet("Lump Sum")
    cols2 = ["Date", "EUNL Nominal (ISK)", "Account Nominal (ISK)",
             "EUNL Real (ISK)", "Account Real (ISK)",
             "EUNL Nom Idx", "Account Nom Idx",
             "EUNL Real Idx", "Account Real Idx", "EUNL Drawdown"]
    for c, name in enumerate(cols2):
        ws2.write(0, c, name, header_fmt)
    for r in range(n):
        ws2.write_datetime(r + 1, 0, df.index[r].to_pydatetime(), date_fmt)
        ws2.write_number(r + 1, 1, ls["eunl_nominal"].iloc[r], int_fmt)
        ws2.write_number(r + 1, 2, ls["account_nominal"].iloc[r], int_fmt)
        ws2.write_number(r + 1, 3, ls["eunl_real"].iloc[r], int_fmt)
        ws2.write_number(r + 1, 4, ls["account_real"].iloc[r], int_fmt)
        ws2.write_number(r + 1, 5, ls["eunl_nom_idx"].iloc[r], num_fmt)
        ws2.write_number(r + 1, 6, ls["account_nom_idx"].iloc[r], num_fmt)
        ws2.write_number(r + 1, 7, ls["eunl_real_idx"].iloc[r], num_fmt)
        ws2.write_number(r + 1, 8, ls["account_real_idx"].iloc[r], num_fmt)
        ws2.write_number(r + 1, 9, ls["eunl_drawdown"].iloc[r], pct_fmt)
    ws2.set_column(0, 0, 12)
    ws2.set_column(1, 9, 18)

    # -- Sheet 3: Monthly DCA --
    ws3 = wb.add_worksheet("Monthly DCA")
    cols3 = ["Date", "Total Contributed", "EUNL Value (ISK)", "Account Value (ISK)",
             "EUNL Real (ISK)", "Account Real (ISK)", "Contributed Real (ISK)",
             "Units Bought", "Cumulative Units"]
    for c, name in enumerate(cols3):
        ws3.write(0, c, name, header_fmt)
    for r in range(n):
        ws3.write_datetime(r + 1, 0, df.index[r].to_pydatetime(), date_fmt)
        ws3.write_number(r + 1, 1, dca["total_contributed"].iloc[r], int_fmt)
        ws3.write_number(r + 1, 2, dca["eunl_value"].iloc[r], int_fmt)
        ws3.write_number(r + 1, 3, dca["account_value"].iloc[r], int_fmt)
        ws3.write_number(r + 1, 4, dca["eunl_real"].iloc[r], int_fmt)
        ws3.write_number(r + 1, 5, dca["account_real"].iloc[r], int_fmt)
        ws3.write_number(r + 1, 6, dca["contributed_real"].iloc[r], int_fmt)
        ws3.write_number(r + 1, 7, dca["units_bought"].iloc[r], num_fmt)
        ws3.write_number(r + 1, 8, dca["cumulative_units"].iloc[r], num_fmt)
    ws3.set_column(0, 0, 12)
    ws3.set_column(1, 8, 18)

    # -- Sheet 4: Summary --
    ws4 = wb.add_worksheet("Summary")
    ws4.set_column(0, 0, 30)
    ws4.set_column(1, 2, 20)

    s = summary
    row = 0

    ws4.write(row, 0, f"EUNL vs Icelandic Savings — {s['period_start']} to {s['period_end']}", bold_fmt)
    row += 1
    ws4.write(row, 0, f"{s['n_months']} months ({s['years']:.1f} years)")
    row += 2

    ws4.write(row, 0, "Parameters", bold_fmt)
    row += 1
    ws4.write(row, 0, "Lump sum (ISK)")
    ws4.write(row, 1, s["lump"], money_fmt)
    row += 1
    ws4.write(row, 0, "Monthly contribution (ISK)")
    ws4.write(row, 1, s["monthly"], money_fmt)
    row += 1
    ws4.write(row, 0, "Savings account rate (annual)")
    ws4.write(row, 1, s["savings_rate"] / 100, pct_fmt)
    row += 2

    # Lump sum results
    ws4.write(row, 0, "LUMP SUM RESULTS", bold_fmt)
    ws4.write(row, 1, "EUNL (ISK)", bold_fmt)
    ws4.write(row, 2, "Savings Account", bold_fmt)
    row += 1
    ws4.write(row, 0, "Ending value — nominal")
    ws4.write(row, 1, s["ls_eunl_nominal"], money_fmt)
    ws4.write(row, 2, s["ls_account_nominal"], money_fmt)
    row += 1
    ws4.write(row, 0, "Ending value — real (today's ISK)")
    ws4.write(row, 1, s["ls_eunl_real"], bold_money)
    ws4.write(row, 2, s["ls_account_real"], bold_money)
    row += 1
    ws4.write(row, 0, "CAGR — nominal")
    ws4.write(row, 1, s["ls_eunl_cagr_nom"] / 100, pct_fmt)
    ws4.write(row, 2, s["ls_acct_cagr_nom"] / 100, pct_fmt)
    row += 1
    ws4.write(row, 0, "CAGR — real")
    ws4.write(row, 1, s["ls_eunl_cagr_real"] / 100, bold_pct)
    ws4.write(row, 2, s["ls_acct_cagr_real"] / 100, bold_pct)
    row += 2

    # DCA results
    ws4.write(row, 0, "MONTHLY DCA RESULTS", bold_fmt)
    ws4.write(row, 1, "EUNL (ISK)", bold_fmt)
    ws4.write(row, 2, "Savings Account", bold_fmt)
    row += 1
    ws4.write(row, 0, "Total contributed")
    ws4.write(row, 1, s["dca_contributed"], money_fmt)
    ws4.write(row, 2, s["dca_contributed"], money_fmt)
    row += 1
    ws4.write(row, 0, "Ending value — nominal")
    ws4.write(row, 1, s["dca_eunl_nominal"], money_fmt)
    ws4.write(row, 2, s["dca_account_nominal"], money_fmt)
    row += 1
    ws4.write(row, 0, "Ending value — real (today's ISK)")
    ws4.write(row, 1, s["dca_eunl_real"], bold_money)
    ws4.write(row, 2, s["dca_account_real"], bold_money)
    row += 2

    # Risk
    ws4.write(row, 0, "RISK & INFLATION", bold_fmt)
    row += 1
    ws4.write(row, 0, "EUNL max drawdown")
    ws4.write(row, 1, s["max_drawdown"] / 100, pct_fmt)
    row += 1
    ws4.write(row, 0, "EUNL worst 12-month return")
    ws4.write(row, 1, s["worst_12m_return"] / 100, pct_fmt)
    row += 1
    ws4.write(row, 0, "Total Icelandic CPI inflation")
    ws4.write(row, 1, s["total_cpi_inflation"] / 100, pct_fmt)
    row += 2

    # Rolling win rates
    win_rates = s["win_rates"]
    ws4.write(row, 0, "WHEN DOES EUNL WIN? (real ISK, lump sum)", bold_fmt)
    row += 1
    ws4.write(row, 0, "Holding period", header_fmt)
    ws4.write(row, 1, "EUNL beat savings", header_fmt)
    ws4.write(row, 2, "Windows tested", header_fmt)
    ws4.write(row, 3, "Avg EUNL real gain", header_fmt)
    ws4.write(row, 4, "Worst EUNL real", header_fmt)
    row += 1
    for h in [3, 5, 7, 10]:
        wr = win_rates.get(h)
        if not wr or wr["win_rate"] is None:
            ws4.write(row, 0, f"{h} years")
            ws4.write(row, 1, "Not enough data")
            row += 1
            continue
        ws4.write(row, 0, f"{h} years")
        ws4.write(row, 1, wr["win_rate"] / 100, pct_fmt)
        ws4.write(row, 2, wr["windows"], int_fmt)
        ws4.write(row, 3, wr["avg_eunl_gain"] / 100, pct_fmt)
        ws4.write(row, 4, wr["worst_eunl_real"] / 100, pct_fmt)
        row += 1
    row += 1

    # Worst entry
    we = s["worst_entry"]
    ws4.write(row, 0, "WORST POSSIBLE ENTRY", bold_fmt)
    row += 1
    ws4.write(row, 0, "Worst month to buy EUNL")
    ws4.write(row, 1, we["worst_entry_date"])
    row += 1
    if we["months_to_beat_savings"] is not None:
        ws4.write(row, 0, "Months until EUNL beat savings")
        ws4.write(row, 1, we["months_to_beat_savings"], int_fmt)
        row += 1
        ws4.write(row, 0, "That's about")
        ws4.write(row, 1, f"{we['years_to_beat_savings']:.1f} years")
    else:
        ws4.write(row, 0, "EUNL has not yet overtaken savings")
        ws4.write(row, 1, "(still recovering)")
    row += 1
    ws4.write(row, 0, "EUNL real return from worst entry")
    ws4.write(row, 1, we["eunl_real_return_now"] / 100, bold_pct)
    row += 1
    ws4.write(row, 0, "Savings real return from worst entry")
    ws4.write(row, 1, we["acct_real_return_now"] / 100, pct_fmt)

    # -- Charts --

    # Chart 1: Nominal ISK Growth (Lump Sum)
    chart1 = wb.add_chart({"type": "line"})
    chart1.set_title({"name": "Lump Sum — Nominal ISK Growth (Index = 100)"})
    chart1.set_x_axis({"name": "Date", "date_axis": True, "num_format": "yyyy"})
    chart1.set_y_axis({"name": "Index"})
    chart1.set_size({"width": 800, "height": 450})
    chart1.add_series({
        "name": "EUNL",
        "categories": ["Lump Sum", 1, 0, n, 0],
        "values": ["Lump Sum", 1, 5, n, 5],
        "line": {"color": COLORS["eunl"], "width": 2.5},
    })
    chart1.add_series({
        "name": "Savings Account",
        "categories": ["Lump Sum", 1, 0, n, 0],
        "values": ["Lump Sum", 1, 6, n, 6],
        "line": {"color": COLORS["account"], "width": 2.5},
    })
    ws2.insert_chart("L2", chart1)

    # Chart 2: Real Purchasing Power (Lump Sum) — THE key chart
    chart2 = wb.add_chart({"type": "line"})
    chart2.set_title({"name": "Lump Sum — Real Purchasing Power (CPI-Adjusted, Index = 100)"})
    chart2.set_x_axis({"name": "Date", "date_axis": True, "num_format": "yyyy"})
    chart2.set_y_axis({"name": "Real Index"})
    chart2.set_size({"width": 800, "height": 450})
    chart2.add_series({
        "name": "EUNL (real)",
        "categories": ["Lump Sum", 1, 0, n, 0],
        "values": ["Lump Sum", 1, 7, n, 7],
        "line": {"color": COLORS["eunl"], "width": 2.5},
    })
    chart2.add_series({
        "name": "Savings Account (real)",
        "categories": ["Lump Sum", 1, 0, n, 0],
        "values": ["Lump Sum", 1, 8, n, 8],
        "line": {"color": COLORS["account"], "width": 2.5},
    })
    ws2.insert_chart("L26", chart2)

    # Chart 3: Drawdown
    chart3 = wb.add_chart({"type": "area"})
    chart3.set_title({"name": "EUNL Drawdown from Peak (ISK Terms)"})
    chart3.set_x_axis({"name": "Date", "date_axis": True, "num_format": "yyyy"})
    chart3.set_y_axis({"name": "Drawdown", "num_format": "0%"})
    chart3.set_size({"width": 800, "height": 350})
    chart3.add_series({
        "name": "Drawdown",
        "categories": ["Lump Sum", 1, 0, n, 0],
        "values": ["Lump Sum", 1, 9, n, 9],
        "fill": {"color": COLORS["drawdown"], "transparency": 60},
        "line": {"color": COLORS["drawdown"], "width": 1.5},
    })
    chart3.set_legend({"none": True})
    ws2.insert_chart("L50", chart3)

    # Chart 4: Monthly DCA Real Wealth
    chart4 = wb.add_chart({"type": "line"})
    chart4.set_title({"name": "Monthly DCA — Real Purchasing Power (ISK)"})
    chart4.set_x_axis({"name": "Date", "date_axis": True, "num_format": "yyyy"})
    chart4.set_y_axis({"name": "ISK (real)", "num_format": "#,##0"})
    chart4.set_size({"width": 800, "height": 450})
    chart4.add_series({
        "name": "EUNL Portfolio (real)",
        "categories": ["Monthly DCA", 1, 0, n, 0],
        "values": ["Monthly DCA", 1, 4, n, 4],
        "line": {"color": COLORS["eunl"], "width": 2.5},
    })
    chart4.add_series({
        "name": "Savings Account (real)",
        "categories": ["Monthly DCA", 1, 0, n, 0],
        "values": ["Monthly DCA", 1, 5, n, 5],
        "line": {"color": COLORS["account"], "width": 2.5},
    })
    chart4.add_series({
        "name": "Total Contributed (real)",
        "categories": ["Monthly DCA", 1, 0, n, 0],
        "values": ["Monthly DCA", 1, 6, n, 6],
        "line": {"color": COLORS["contributed"], "width": 1.5, "dash_type": "dash"},
    })
    ws3.insert_chart("K2", chart4)

    wb.close()


# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------

def fmt_isk(value: float) -> str:
    """Format ISK amount with thousands separator."""
    return f"{value:>14,.0f}"


def print_summary(s: dict):
    """Print compact summary to stdout."""
    print()
    print(f"  EUNL vs Icelandic Savings — {s['period_start']} to {s['period_end']}")
    print(f"  {s['n_months']} months ({s['years']:.1f} years)")
    print(f"  Lump: {s['lump']:,.0f} ISK | Monthly: {s['monthly']:,.0f} ISK | Savings rate: {s['savings_rate']:.1f}%")
    print()
    print(f"  {'':30s} {'EUNL (ISK)':>14s}   {'Savings Acct':>14s}")
    print(f"  {'-'*62}")
    print(f"  {'Lump → Nominal':30s} {fmt_isk(s['ls_eunl_nominal'])}   {fmt_isk(s['ls_account_nominal'])}")
    print(f"  {'Lump → Real (today ISK)':30s} {fmt_isk(s['ls_eunl_real'])}   {fmt_isk(s['ls_account_real'])}")
    print(f"  {'Lump CAGR nominal':30s} {s['ls_eunl_cagr_nom']:>13.1f}%   {s['ls_acct_cagr_nom']:>13.1f}%")
    print(f"  {'Lump CAGR real':30s} {s['ls_eunl_cagr_real']:>13.1f}%   {s['ls_acct_cagr_real']:>13.1f}%")
    print(f"  {'-'*62}")
    print(f"  {'DCA → Total contributed':30s} {fmt_isk(s['dca_contributed'])}   {fmt_isk(s['dca_contributed'])}")
    print(f"  {'DCA → Nominal':30s} {fmt_isk(s['dca_eunl_nominal'])}   {fmt_isk(s['dca_account_nominal'])}")
    print(f"  {'DCA → Real (today ISK)':30s} {fmt_isk(s['dca_eunl_real'])}   {fmt_isk(s['dca_account_real'])}")
    print(f"  {'-'*62}")
    print(f"  {'Max drawdown (EUNL)':30s} {s['max_drawdown']:>13.1f}%")
    print(f"  {'Worst 12-month return (EUNL)':30s} {s['worst_12m_return']:>13.1f}%")
    print(f"  {'Total Icelandic CPI inflation':30s} {s['total_cpi_inflation']:>13.1f}%")
    print()
    print(f"  WHEN DOES EUNL WIN? (real ISK, any entry month)")
    print(f"  {'-'*62}")
    print(f"  {'Holding period':20s} {'Beat savings':>14s}   {'Avg real gain':>14s}   {'Worst case':>12s}")
    for h in [3, 5, 7, 10]:
        wr = s["win_rates"].get(h)
        if not wr or wr["win_rate"] is None:
            print(f"  {f'{h} years':20s} {'(not enough data)':>14s}")
            continue
        print(f"  {f'{h} years':20s} {wr['win_rate']:>13.0f}%   {wr['avg_eunl_gain']:>13.1f}%   {wr['worst_eunl_real']:>11.1f}%")
    print()
    we = s["worst_entry"]
    print(f"  WORST POSSIBLE ENTRY: {we['worst_entry_date']}")
    if we["months_to_beat_savings"] is not None:
        print(f"  Even buying at the worst moment, EUNL overtook savings after {we['years_to_beat_savings']:.1f} years")
    else:
        print(f"  EUNL has not yet overtaken savings from this entry (still recovering)")
    print(f"  From that worst entry: EUNL real {we['eunl_real_return_now']:+.1f}%  vs  Savings real {we['acct_real_return_now']:+.1f}%")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="EUNL vs Icelandic Savings — Real Purchasing-Power Comparison"
    )
    parser.add_argument("--lump", type=float, default=1_000_000,
                        help="Lump sum in ISK (default: 1,000,000)")
    parser.add_argument("--monthly", type=float, default=50_000,
                        help="Monthly DCA contribution in ISK (default: 50,000)")
    parser.add_argument("--savings-rate", type=float, default=5.0,
                        help="Annual savings account interest rate %% (default: 5.0)")
    parser.add_argument("--start", type=str, default=None,
                        help="Start month YYYY-MM (default: earliest available)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output Excel path (default: research-material/eunl-comparison.xlsx)")
    args = parser.parse_args()

    # Output path
    if args.output:
        out_path = Path(args.output)
    else:
        out_dir = Path(__file__).resolve().parent.parent / "output"
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / "eunl-comparison.xlsx"

    print("Fetching EUNL price history...")
    eunl = fetch_eunl_monthly()
    print(f"  → {len(eunl)} months ({eunl.index[0].strftime('%b %Y')} – {eunl.index[-1].strftime('%b %Y')})")

    print("Fetching EUR/ISK exchange rate...")
    eurisk = fetch_eurisk_monthly()
    print(f"  → {len(eurisk)} months ({eurisk.index[0].strftime('%b %Y')} – {eurisk.index[-1].strftime('%b %Y')})")

    print("Fetching Icelandic CPI...")
    cpi = fetch_icelandic_cpi()
    print(f"  → {len(cpi)} months ({cpi.index[0].strftime('%b %Y')} – {cpi.index[-1].strftime('%b %Y')})")

    print("Aligning data and computing scenarios...")
    df = build_dataframe(eunl, eurisk, cpi, args.start)
    print(f"  → {len(df)} overlapping months ({df.index[0].strftime('%b %Y')} – {df.index[-1].strftime('%b %Y')})")

    ls = compute_lump_sum(df, args.lump, args.savings_rate)
    dca = compute_dca(df, args.monthly, args.savings_rate)
    summary = compute_summary(df, ls, dca, args.lump, args.monthly, args.savings_rate)

    print(f"Writing Excel → {out_path}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_excel(out_path, df, ls, dca, summary)

    print_summary(summary)
    print(f"  Output: {out_path}")


if __name__ == "__main__":
    main()
