from copy import deepcopy
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template

app = Flask(__name__)


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


def gather_stock_information():
    """Return the latest maintained stock snapshot data for page refreshes."""
    refreshed_stocks = deepcopy(STOCKS)
    refreshed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    for stock in refreshed_stocks:
        stock["last_refreshed"] = refreshed_at

    return refreshed_stocks, refreshed_at


@app.route("/")
def stock_snapshot():
    """Render a simple stock snapshot page with manually maintained data."""
    stocks, refreshed_at = gather_stock_information()
    return render_template("index.html", stocks=stocks, refreshed_at=refreshed_at)


@app.post("/refresh")
def refresh_stock_snapshot():
    """Provide refreshed stock data for the dashboard refresh button."""
    stocks, refreshed_at = gather_stock_information()
    return jsonify({"stocks": stocks, "refreshed_at": refreshed_at})


if __name__ == "__main__":
    app.run(debug=True)
