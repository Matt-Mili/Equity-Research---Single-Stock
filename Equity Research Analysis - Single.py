import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ------------------------------------------
# Function: Get Fundamental Metrics for a Stock (Using Yahoo Finance)
# ------------------------------------------
def get_stock_fundamentals(ticker):
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
    except Exception as e:
        print(f"Error fetching info for {ticker}: {e}")
        return None
    
    operating_cash_flow = info.get("operatingCashflow", np.nan)
    capex = info.get("capitalExpenditures", np.nan)
    
    if not np.isnan(operating_cash_flow) and not np.isnan(capex):
        unlevered_fcf = operating_cash_flow - capex
    else:
        unlevered_fcf = np.nan

    fundamentals = {
        'Ticker': ticker,
        'Name': info.get("shortName", ""),
        'P/E': info.get("trailingPE", np.nan),
        'P/B': info.get("priceToBook", np.nan),
        'ROE': info.get("returnOnEquity", np.nan),
        'Debt/Equity': info.get("debtToEquity", np.nan),
        'Operating Cash Flow': operating_cash_flow,
        'Capital Expenditures': capex,
        'Unlevered Free Cash Flow': unlevered_fcf,
        'Dividend Rate': info.get("dividendRate", np.nan),
        'Trailing EPS': info.get("trailingEps", np.nan),
        'Book Value': info.get("bookValue", np.nan),
        'Market Cap': info.get("marketCap", np.nan)
    }
    return fundamentals

# ------------------------------------------
# Function: Dividend Discount Model (DDM) Analysis
# ------------------------------------------
def ddm_analysis(ticker, dividend_growth_rate=0.03, discount_rate=0.08, forecast_years=5):
    fundamentals = get_stock_fundamentals(ticker)
    if fundamentals is None:
        return None
    dividend_rate = fundamentals['Dividend Rate']
    if np.isnan(dividend_rate) or dividend_rate <= 0:
        print(f"No valid Dividend Rate available for {ticker} for DDM analysis.")
        return None

    projected_dividends = []
    discounted_dividends = []
    for year in range(1, forecast_years + 1):
        projected_div = dividend_rate * ((1 + dividend_growth_rate) ** year)
        discounted_div = projected_div / ((1 + discount_rate) ** year)
        projected_dividends.append(projected_div)
        discounted_dividends.append(discounted_div)
    
    last_dividend = dividend_rate * ((1 + dividend_growth_rate) ** forecast_years)
    terminal_value = last_dividend * (1 + dividend_growth_rate) / (discount_rate - dividend_growth_rate)
    discounted_terminal_value = terminal_value / ((1 + discount_rate) ** forecast_years)
    intrinsic_value = sum(discounted_dividends) + discounted_terminal_value

    ddm_results = {
        'Projected Dividends': projected_dividends,
        'Discounted Dividends': discounted_dividends,
        'Terminal Value': terminal_value,
        'Discounted Terminal Value': discounted_terminal_value,
        'Intrinsic Value': intrinsic_value
    }
    return ddm_results

def plot_ddm_analysis(ddm_results, forecast_years):
    years = list(range(1, forecast_years + 1))
    projected_dividends = ddm_results['Projected Dividends']
    discounted_dividends = ddm_results['Discounted Dividends']
    discounted_terminal_value = ddm_results['Discounted Terminal Value']

    df = pd.DataFrame({
        'Year': years,
        'Projected Dividend': projected_dividends,
        'Discounted Dividend': discounted_dividends
    })

    plt.figure(figsize=(12, 6))
    bar_width = 0.35
    plt.bar(np.array(years) - bar_width/2, projected_dividends, width=bar_width, alpha=0.6, label="Projected Dividend")
    plt.bar(np.array(years) + bar_width/2, discounted_dividends, width=bar_width, alpha=0.6, label="Discounted Dividend")
    plt.axhline(y=discounted_terminal_value, color='red', linestyle='--', label="Discounted Terminal Value")
    plt.title("DDM Analysis - Projected and Discounted Dividends")
    plt.xlabel("Forecast Year")
    plt.ylabel("Dividend (USD)")
    plt.xticks(years)
    plt.legend()
    plt.grid(True)
    plt.show()

# ------------------------------------------
# Function: Earnings Based Valuation
# ------------------------------------------
def earnings_based_valuation(ticker, assumed_pe=12):
    fundamentals = get_stock_fundamentals(ticker)
    if fundamentals is None:
        return None
    trailing_eps = fundamentals['Trailing EPS']
    if np.isnan(trailing_eps) or trailing_eps <= 0:
        print(f"No valid Trailing EPS available for {ticker} for Earnings Based Valuation.")
        return None
    intrinsic_value = trailing_eps * assumed_pe
    return intrinsic_value

# ------------------------------------------
# Function: Price-to-Book Valuation
# ------------------------------------------
def price_to_book_valuation(ticker, target_pb=1.0):
    fundamentals = get_stock_fundamentals(ticker)
    if fundamentals is None:
        return None
    book_value = fundamentals['Book Value']
    if np.isnan(book_value) or book_value <= 0:
        print(f"No valid Book Value available for {ticker} for Price-to-Book Valuation.")
        return None
    intrinsic_value = book_value * target_pb
    return intrinsic_value

# ------------------------------------------
# Function: Plot Historical Stock Price
# ------------------------------------------
def plot_historical_price(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    if hist.empty:
        print(f"No historical data available for {ticker}.")
        return
    plt.figure(figsize=(12, 6))
    plt.plot(hist.index, hist['Close'], label=f"{ticker} Close Price", linewidth=2)
    plt.title(f"{ticker} Historical Stock Price (1 Year)")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.show()

# ------------------------------------------
# Function: Print Fundamental Summary
# ------------------------------------------
def print_fundamental_summary(fundamentals):
    print("=== Fundamental Summary ===")
    for key, value in fundamentals.items():
        if key not in ['Ticker', 'Name']:
            print(f"{key}: {value}")
    print("===========================")

# ------------------------------------------
# Main Execution
# ------------------------------------------
if __name__ == "__main__":
    ticker = "PRU"  # Change this to analyze a different stock
    print(f"Analyzing stock: {ticker}")
    
    # Get and display fundamental metrics
    fundamentals = get_stock_fundamentals(ticker)
    if fundamentals:
        print("\nFundamental Metrics:")
        print_fundamental_summary(fundamentals)
    
    # Run and Visualize DDM Analysis
    ddm_results = ddm_analysis(ticker, dividend_growth_rate=0.03, discount_rate=0.08, forecast_years=5)
    if ddm_results:
        print("\n=== DDM Analysis Results ===")
        print(f"Intrinsic Value (DDM): ${ddm_results['Intrinsic Value']:.2f}")
        plot_ddm_analysis(ddm_results, forecast_years=5)
    
    # Earnings Based Valuation
    earnings_value = earnings_based_valuation(ticker, assumed_pe=12)
    if earnings_value:
        print(f"\nEarnings Based Valuation (Assumed P/E of 12): ${earnings_value:.2f}")
    
    # Price-to-Book Valuation
    pb_value = price_to_book_valuation(ticker, target_pb=1.0)
    if pb_value:
        print(f"\nPrice-to-Book Valuation (Target P/B of 1.0): ${pb_value:.2f}")
    
    # Plot Historical Stock Price
    plot_historical_price(ticker)




