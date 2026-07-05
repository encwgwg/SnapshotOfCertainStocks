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
            "general_performance": "To be updated with recent performance details.",
            "latest_news": "To be updated with the latest relevant news.",
            "recommendation": "Hold",
        },
        {
            "symbol": "ZSP.TO",
            "anchor": "stock-zsp-to",
            "name": "BMO S&P 500 Index ETF",
            "current_price": "CA$117.32 (last close, Jul 3, 2026)",
            "general_performance": "To be updated with recent performance details.",
            "latest_news": "To be updated with the latest relevant news.",
            "recommendation": "Buy",
        },
        {
            "symbol": "ASTS",
            "anchor": "stock-asts",
            "name": "AST SpaceMobile",
            "current_price": "US$85.13 (last close, Jul 2, 2026)",
            "general_performance": "To be updated with recent performance details.",
            "latest_news": "To be updated with the latest relevant news.",
            "recommendation": "Sell",
        },
        {
            "symbol": "SPCX.TO",
            "anchor": "stock-spcx-to",
            "name": "SPAC and New Issue ETF",
            "current_price": "CA$27.34 (last close, Jul 3, 2026)",
            "general_performance": "To be updated with recent performance details.",
            "latest_news": "To be updated with the latest relevant news.",
            "recommendation": "Buy",
        },
    ]
    return render_template("index.html", stocks=stocks)


if __name__ == "__main__":
    app.run(debug=True)
