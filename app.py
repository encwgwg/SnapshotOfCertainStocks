from copy import deepcopy
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json
from json import JSONDecodeError
from pathlib import Path
from xml.etree import ElementTree

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0"}
REQUEST_TIMEOUT = 8
WATCHLIST_FILE = Path(__file__).with_name("watchlist_data.json")


STOCKS = [
    {
        "symbol": "AC.TO",
        "anchor": "stock-ac-to",
        "name": "Air Canada",
        "current_price": "CA$24.61 (last close, Jul 3, 2026)",
        "general_performance": "Short term is improving: AC is up about 14% over the past month and slightly positive over the past week. Longer term, it is up about 15% year over year, but the price is near analyst fair-value targets. Business momentum is mixed: Air Canada reported record Q1 2026 revenue and strong cash flow, but suspended full-year guidance, so demand looks healthy while outlook risk remains.",
        "latest_news": [
            "Q1 2026 revenue hit a record CA$5.8B, up more than 11% year over year, with operating income improving to CA$117M.",
            "Air Canada suspended full-year 2026 guidance because fuel-price and macro volatility made the outlook less certain.",
            "Management highlighted board renewal and recovery progress at the 2026 annual shareholder meeting.",
        ],
        "recommendation": "Hold",
    },
    {
        "symbol": "ZSP.TO",
        "anchor": "stock-zsp-to",
        "name": "BMO S&P 500 Index ETF",
        "current_price": "CA$117.32 (last close, Jul 3, 2026)",
        "general_performance": "ZSP has positive short, mid and long-term momentum: recent data shows gains of about 1.9% over one month, 17.0% over three months and 25.9% over 52 weeks. Because it tracks the S&P 500, business performance depends on broad U.S. large-cap earnings rather than one company. Recent market strength and tech-heavy holdings have supported results, though valuation and FX/market swings remain risks.",
        "latest_news": [
            "Recent ETF news flow is mostly market/portfolio driven rather than issuer-specific; ZSP continues to track the S&P 500.",
            "Yahoo Finance showed strong recent fund returns and technology as the largest sector weight, led by Nvidia, Apple and Microsoft.",
            "Recent Canadian investing articles continue to feature broad-market ETFs like ZSP for TFSA/long-term portfolio exposure.",
        ],
        "recommendation": "Buy",
    },
    {
        "symbol": "ASTS",
        "anchor": "stock-asts",
        "name": "AST SpaceMobile",
        "current_price": "US$85.13 (last close, Jul 2, 2026)",
        "general_performance": "ASTS has very strong long-term momentum but high volatility: it hit an all-time high near US$133.86 in late May 2026, far above its 2024 lows, but has pulled back sharply since. Recent business is mixed: partnerships, satellite launches and regulatory wins support the growth story, while Q1 earnings/revenue missed estimates and launch setbacks show execution risk remains high.",
        "latest_news": [
            "AST SpaceMobile scheduled BlueBird 8-10 activity in June 2026 and announced BlueBirds 11, 12 and 13 for launch in early August.",
            "Q1 2026 update showed CA/US revenue growth but a large net loss, while management targeted about 45 BlueBird satellites in orbit during 2026.",
            "Shares fell after recent BlueBird launch news as investors weighed execution risk against the direct-to-device opportunity.",
        ],
        "recommendation": "Sell",
    },
    {
        "symbol": "SPCX.TO",
        "anchor": "stock-spcx-to",
        "name": "SpaceX CDR (CAD Hedged)",
        "current_price": "CA$27.34 (last close, Jul 3, 2026)",
        "general_performance": "SPCX.TO is newly listed, so long-term public history is limited. Short-term trading has been volatile: it recently closed at CA$27.34, above the CA$24.67 52-week low but below the CA$38.00 high. Business momentum is tied to SpaceX, whose launch, Starlink and AI/connectivity growth story remains strong, but the post-IPO/CDR price action has been choppy and retail-driven.",
        "latest_news": [
            "SpaceX completed Starship Flight 12 on May 22, 2026, testing V3 vehicles, Raptor 3 engines, Pad 2 and Starlink deployment work.",
            "SpaceX launched SiriusXM's SXM-11 satellite on June 28, 2026, adding another successful Falcon 9 commercial mission.",
            "Recent analyst coverage highlighted SpaceX growth across launches, Starlink and AI/data-center opportunities.",
        ],
        "recommendation": "Buy",
    },
]


STOCK_REFRESH_DATA = {
    stock["symbol"]: {
        "name": stock["name"],
        "current_price": stock["current_price"],
        "general_performance": stock["general_performance"],
        "latest_news": stock["latest_news"],
        "recommendation": stock["recommendation"],
    }
    for stock in STOCKS
}

STOCK_REFRESH_DATA["RCI-B.TO"] = {
    "name": "Rogers Communications Inc.",
    "current_price": "CA$45.08 (last close, Jul 3, 2026)",
    "general_performance": "Short term has been weak: RCI.B is down about 14% over the past month and down about 13% year to date, while the one-year return is only slightly positive. Mid/long term remains pressured versus prior highs, but analysts still see upside. Business momentum is mixed: Q1 2026 showed service revenue and EBITDA growth plus lower capex/free-cash-flow improvement, but telecom pricing pressure and debt remain concerns.",
    "latest_news": [
        "Rogers plans to release Q2 2026 results on July 22, 2026, before North American markets open.",
        "Q1 2026 commentary highlighted service revenue and EBITDA growth, reduced capex and improved free cash flow.",
        "Rogers donated CA$1M to the 2026 Rogers Charity Classic in June to support children's charities across Alberta.",
    ],
    "recommendation": "Buy",
}


def format_price(price, currency):
    """Format a fetched price with its currency code."""
    if price is None:
        return None
    try:
        numeric_price = float(price)
    except (TypeError, ValueError):
        return None

    currency_prefix = {"CAD": "CA$", "USD": "US$"}.get(currency, f"{currency or ''} ")
    return f"{currency_prefix}{numeric_price:.2f}"


def fetch_yahoo_chart(symbol):
    """Fetch Yahoo chart data for price and historical performance."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    chart_data = response.json()["chart"]["result"][0]
    return chart_data


def format_market_time(timestamp):
    """Format Yahoo's market timestamp in Eastern time for clear price timing."""
    if not timestamp:
        return "latest available market price"

    market_time = datetime.fromtimestamp(timestamp, ZoneInfo("America/New_York"))
    return market_time.strftime("%b %-d, %Y %-I:%M %p ET")


def fetch_current_price(symbol):
    """Fetch the latest regular-market price from Yahoo Finance chart data."""
    chart_data = fetch_yahoo_chart(symbol)
    metadata = chart_data.get("meta", {})
    price = metadata.get("regularMarketPrice") or metadata.get("previousClose")
    formatted_price = format_price(price, metadata.get("currency"))
    if formatted_price:
        market_time = format_market_time(metadata.get("regularMarketTime"))
        return f"{formatted_price} ({market_time})"
    return None


def calculate_percent_change(current_price, old_price):
    """Calculate percent change, guarding against missing or zero values."""
    if current_price is None or old_price in (None, 0):
        return None
    return ((current_price - old_price) / old_price) * 100


def fetch_general_performance(symbol, name):
    """Summarize short-, mid-, and long-term price performance from history."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1y&interval=1d"
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    result = response.json()["chart"]["result"][0]
    closes = [price for price in result["indicators"]["quote"][0].get("close", []) if price is not None]
    if len(closes) < 2:
        return None

    current_price = closes[-1]
    one_month_change = calculate_percent_change(current_price, closes[-22] if len(closes) > 22 else closes[0])
    three_month_change = calculate_percent_change(current_price, closes[-66] if len(closes) > 66 else closes[0])
    one_year_change = calculate_percent_change(current_price, closes[0])

    performance_parts = []
    for label, change in [("1M", one_month_change), ("3M", three_month_change), ("1Y", one_year_change)]:
        if change is not None:
            performance_parts.append(f"{label} {change:+.1f}%")

    if not performance_parts:
        return None

    return (
        f"{name} recent price performance: {', '.join(performance_parts)}. "
        "This refresh uses available market-history data for the short, mid and long term; review company filings/news for business-specific drivers."
    )[:800]


def yahoo_news_items(symbol):
    """Fetch recent Yahoo Finance headlines for a stock symbol."""
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    root = ElementTree.fromstring(response.content)
    headlines = []
    for item in root.findall("./channel/item")[:3]:
        title = item.findtext("title")
        if title:
            headlines.append(title[:240])
    return headlines


def fetch_analyst_recommendation(symbol):
    """Fetch Yahoo Finance analyst recommendation text when it is available."""
    modules = "financialData,recommendationTrend"
    url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules={modules}"
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    result = response.json()["quoteSummary"]["result"][0]
    recommendation = result.get("financialData", {}).get("recommendationKey")
    if recommendation:
        return recommendation.replace("_", " ").title()

    trends = result.get("recommendationTrend", {}).get("trend", [])
    if trends:
        latest_trend = trends[0]
        ratings = {
            "Buy": latest_trend.get("strongBuy", 0) + latest_trend.get("buy", 0),
            "Hold": latest_trend.get("hold", 0),
            "Sell": latest_trend.get("sell", 0) + latest_trend.get("strongSell", 0),
        }
        return max(ratings, key=ratings.get)
    return None


def recommendation_from_performance(general_performance):
    """Create a simple buy/hold/sell view when analyst consensus is unavailable."""
    if not general_performance:
        return "Hold"
    if "+" in general_performance and "1Y +" in general_performance:
        return "Buy (performance-based)"
    if "1Y -" in general_performance:
        return "Sell (performance-based)"
    return "Hold (performance-based)"


def fetch_market_information(symbol, stock):
    """Best-effort live refresh for every stock symbol in the watchlist."""
    refreshed_stock = deepcopy(stock)

    try:
        price = fetch_current_price(symbol)
        if price:
            refreshed_stock["current_price"] = price
    except requests.RequestException:
        refreshed_stock["current_price"] = "Price refresh unavailable from Yahoo Finance right now."
    except (KeyError, IndexError, TypeError, ValueError):
        refreshed_stock["current_price"] = "Price refresh returned incomplete market data."

    try:
        performance = fetch_general_performance(symbol, refreshed_stock["name"])
        if performance:
            refreshed_stock["general_performance"] = performance
    except requests.RequestException:
        refreshed_stock["general_performance"] = "Performance refresh unavailable from Yahoo Finance right now."
    except (KeyError, IndexError, TypeError, ValueError):
        refreshed_stock["general_performance"] = "Performance refresh returned incomplete market data."

    try:
        headlines = yahoo_news_items(symbol)
        refreshed_stock["latest_news"] = headlines or ["No recent Yahoo Finance headlines were found for this symbol."]
    except requests.RequestException:
        refreshed_stock["latest_news"] = ["Latest-news refresh unavailable from Yahoo Finance right now."]
    except ElementTree.ParseError:
        refreshed_stock["latest_news"] = ["Latest-news refresh returned unreadable feed data."]

    fallback_recommendation = recommendation_from_performance(refreshed_stock.get("general_performance", ""))
    try:
        refreshed_stock["recommendation"] = fetch_analyst_recommendation(symbol) or fallback_recommendation
    except requests.RequestException:
        refreshed_stock["recommendation"] = fallback_recommendation
    except (KeyError, IndexError, TypeError, ValueError):
        refreshed_stock["recommendation"] = fallback_recommendation

    return refreshed_stock


def build_stock_anchor(symbol):
    """Create a safe in-page anchor for a stock symbol."""
    safe_symbol = "".join(character.lower() if character.isalnum() else "-" for character in symbol)
    return f"stock-{safe_symbol.strip('-')}"


def create_placeholder_stock(symbol):
    """Create a new stock entry that can be filled by future refreshes."""
    return {
        "symbol": symbol,
        "anchor": build_stock_anchor(symbol),
        "name": symbol,
        "current_price": "To be updated on refresh",
        "general_performance": "To be updated after market information is gathered.",
        "latest_news": ["To be updated with the latest relevant news."],
        "recommendation": "Hold",
    }


def normalize_stock_symbol(symbol):
    """Normalize symbols so refresh data can match newly added entries."""
    return symbol.strip().upper()


def find_stock(symbol):
    """Find an existing stock entry by symbol, ignoring case."""
    normalized_symbol = normalize_stock_symbol(symbol)
    return next((stock for stock in STOCKS if normalize_stock_symbol(stock["symbol"]) == normalized_symbol), None)


def prepare_saved_stock(stock):
    """Validate and normalize a stock entry loaded from disk."""
    symbol = normalize_stock_symbol(str(stock.get("symbol", "")))
    if not symbol:
        return None

    prepared_stock = create_placeholder_stock(symbol)
    prepared_stock.update(stock)
    prepared_stock["symbol"] = symbol
    prepared_stock["anchor"] = stock.get("anchor") or build_stock_anchor(symbol)
    return prepared_stock


def load_saved_stocks():
    """Load the persisted watchlist so added symbols survive restarts."""
    if not WATCHLIST_FILE.exists():
        return

    try:
        saved_stocks = json.loads(WATCHLIST_FILE.read_text())
    except (OSError, JSONDecodeError):
        return

    if not isinstance(saved_stocks, list):
        return

    loaded_stocks = []
    seen_symbols = set()
    for stock in saved_stocks:
        if not isinstance(stock, dict):
            continue
        prepared_stock = prepare_saved_stock(stock)
        if not prepared_stock or prepared_stock["symbol"] in seen_symbols:
            continue
        loaded_stocks.append(prepared_stock)
        seen_symbols.add(prepared_stock["symbol"])

    if loaded_stocks:
        STOCKS[:] = loaded_stocks


def save_stocks(stocks=None):
    """Persist the current watchlist to disk."""
    stocks_to_save = stocks if stocks is not None else STOCKS
    WATCHLIST_FILE.write_text(json.dumps(stocks_to_save, indent=2))


def replace_stocks(stocks):
    """Replace the in-memory watchlist and persist it."""
    STOCKS[:] = deepcopy(stocks)
    save_stocks()


def delete_stock_by_symbol(symbol):
    """Remove a stock from the watchlist and persist the updated list."""
    normalized_symbol = normalize_stock_symbol(symbol)
    remaining_stocks = [
        stock for stock in STOCKS if normalize_stock_symbol(stock["symbol"]) != normalized_symbol
    ]

    if len(remaining_stocks) == len(STOCKS):
        return None

    replace_stocks(remaining_stocks)
    return normalized_symbol


def apply_refresh_data(stock):
    """Update a stock with refreshed market information."""
    refreshed_stock = fetch_market_information(stock["symbol"], stock)
    stock.update(refreshed_stock)


def gather_stock_information():
    """Return the latest maintained stock snapshot data for page refreshes."""
    refreshed_stocks = deepcopy(STOCKS)
    refreshed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    for stock in refreshed_stocks:
        apply_refresh_data(stock)
        stock["last_refreshed"] = refreshed_at

    return refreshed_stocks, refreshed_at


load_saved_stocks()


@app.route("/")
def stock_snapshot():
    """Render a simple stock snapshot page with manually maintained data."""
    stocks, refreshed_at = gather_stock_information()
    return render_template("index.html", stocks=stocks, refreshed_at=refreshed_at)


@app.post("/refresh")
def refresh_stock_snapshot():
    """Provide refreshed stock data for the dashboard refresh button."""
    stocks, refreshed_at = gather_stock_information()
    replace_stocks(stocks)
    return jsonify({"stocks": stocks, "refreshed_at": refreshed_at})


@app.post("/stocks")
def add_stock():
    """Add a new stock symbol to the in-memory watchlist."""
    request_data = request.get_json(silent=True) if request.is_json else {}
    symbol = request_data.get("symbol", "") if request_data else ""
    normalized_symbol = normalize_stock_symbol(symbol)

    if not normalized_symbol:
        return jsonify({"error": "Stock symbol is required."}), 400

    existing_stock = find_stock(normalized_symbol)
    if existing_stock:
        return jsonify({"stock": existing_stock, "added": False})

    new_stock = create_placeholder_stock(normalized_symbol)
    STOCKS.append(new_stock)
    save_stocks()
    return jsonify({"stock": new_stock, "added": True}), 201


@app.delete("/stocks/<path:symbol>")
def delete_stock(symbol):
    """Delete a stock symbol from the watchlist permanently."""
    deleted_symbol = delete_stock_by_symbol(symbol)

    if not deleted_symbol:
        return jsonify({"error": "Stock symbol was not found."}), 404

    return jsonify({"deleted": True, "symbol": deleted_symbol})


if __name__ == "__main__":
    app.run(debug=True)
