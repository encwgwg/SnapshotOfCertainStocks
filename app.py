from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def stock_snapshot():
    """Render a simple stock snapshot page with manually maintained data."""
    stocks = [
        {
            "symbol": "AC.TO",
            "anchor": "stock-ac-to",
            "name": "Air Canada",
            "current_price": "CA$24.61 (last close, Jul 3, 2026)",
            "general_performance": "Short term is improving: AC is up about 14% over the past month and slightly positive over the past week. Longer term, it is up about 15% year over year, but the price is near analyst fair-value targets. Business momentum is mixed: Air Canada reported record Q1 2026 revenue and strong cash flow, but suspended full-year guidance, so demand looks healthy while outlook risk remains.",
            "latest_news": "To be updated with the latest relevant news.",
            "recommendation": "Hold",
        },
        {
            "symbol": "ZSP.TO",
            "anchor": "stock-zsp-to",
            "name": "BMO S&P 500 Index ETF",
            "current_price": "CA$117.32 (last close, Jul 3, 2026)",
            "general_performance": "ZSP has positive short, mid and long-term momentum: recent data shows gains of about 1.9% over one month, 17.0% over three months and 25.9% over 52 weeks. Because it tracks the S&P 500, business performance depends on broad U.S. large-cap earnings rather than one company. Recent market strength and tech-heavy holdings have supported results, though valuation and FX/market swings remain risks.",
            "latest_news": "To be updated with the latest relevant news.",
            "recommendation": "Buy",
        },
        {
            "symbol": "ASTS",
            "anchor": "stock-asts",
            "name": "AST SpaceMobile",
            "current_price": "US$85.13 (last close, Jul 2, 2026)",
            "general_performance": "ASTS has very strong long-term momentum but high volatility: it hit an all-time high near US$133.86 in late May 2026, far above its 2024 lows, but has pulled back sharply since. Recent business is mixed: partnerships, satellite launches and regulatory wins support the growth story, while Q1 earnings/revenue missed estimates and launch setbacks show execution risk remains high.",
            "latest_news": "To be updated with the latest relevant news.",
            "recommendation": "Sell",
        },
        {
            "symbol": "SPCX.TO",
            "anchor": "stock-spcx-to",
            "name": "SpaceX CDR (CAD Hedged)",
            "current_price": "CA$27.34 (last close, Jul 3, 2026)",
            "general_performance": "SPCX.TO is newly listed, so long-term public history is limited. Short-term trading has been volatile: it recently closed at CA$27.34, above the CA$24.67 52-week low but below the CA$38.00 high. Business momentum is tied to SpaceX, whose launch, Starlink and AI/connectivity growth story remains strong, but the post-IPO/CDR price action has been choppy and retail-driven.",
            "latest_news": "To be updated with the latest relevant news.",
            "recommendation": "Buy",
        },
    ]
    return render_template("index.html", stocks=stocks)


if __name__ == "__main__":
    app.run(debug=True)
