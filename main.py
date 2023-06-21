import logging
import os
import argparse
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import List, Dict
from alpaca.trading.client import TradingClient
from alpaca.trading.models import PortfolioHistory
from alpaca.trading.enums import TimeInForce, OrderSide, OrderType
from alpaca.trading.requests import OrderRequest
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data.historical.stock import StockHistoricalDataClient
from pydantic import parse_obj_as
from markdownify import markdownify as md
from bottle import SimpleTemplate, template
from dotenv import load_dotenv

load_dotenv()

LOG_FORMAT = '%(asctime)s %(name)10.10s %(levelname).7s %(filename)15.15s %(lineno)-4s %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
logger = logging.getLogger('DCA')

alpaca_endpoint = os.getenv("ALPACA_ENDPOINT")
alpaca_api_key = os.getenv("ALPACA_KEY_ID")
alpaca_secret_key = os.getenv("ALPACA_SECRET")
alpaca_trading = TradingClient(alpaca_api_key, alpaca_secret_key, url_override=alpaca_endpoint)
alpaca_data_historical = StockHistoricalDataClient(alpaca_api_key, alpaca_secret_key, url_override=alpaca_endpoint)

def main() -> None:
    logger.info("Starting DCA")
    parser = argparse.ArgumentParser(description="Automated Dollar Cost Averaging Leveraged & Inverse Funds ")
    parser.add_argument('--symbols', '-s', help='List of symbols and amount', required=True, metavar="KEY=VALUE", nargs='+')
    args = parser.parse_args()
    symbols = get_symbols(args.symbols)

    for symbol in symbols:
        buy_symbol(symbol['symbol'], symbol['quantity'], symbol['notional'])
    update_report([symbol['symbol'] for symbol in symbols])



def get_ask_price(symbol: str) -> float:
    logger.info(f"Getting ask price for {symbol}")
    quote_request = StockLatestQuoteRequest(symbol_or_symbols=symbol, feed=None)
    quote_response = alpaca_data_historical.get_stock_latest_quote(quote_request)
    return quote_response[symbol].ask_price


def buy_symbol(symbol, qty, notional) -> None:
    if notional:
        logger.info(f"Buying ${qty} worth of {symbol}")
        order_request = OrderRequest(symbol=symbol, side=OrderSide.BUY, type=OrderType.MARKET, notional=qty, time_in_force=TimeInForce.DAY) # type: ignore
        alpaca_trading.submit_order(order_request)
    else:
        logger.info(f"Buying {qty} shares of {symbol}")
        order_request = OrderRequest(symbol=symbol, side=OrderSide.BUY, type=OrderType.MARKET, qty=qty, time_in_force=TimeInForce.DAY) # type: ignore
        alpaca_trading.submit_order(order_request)


def get_symbols(items) -> List[Dict]:
    d = []
    if items:
        for item in items:
            symbol = item.split('=')[0]
            quantity = item.split('=')[1]
            logger.info(f"Symbol: {symbol} Quantity: {quantity}")
            notional = True if quantity[0] == '$' else False
            quantity = float(quantity.replace('$', ''))
            d.append({'symbol' : symbol, 'quantity' : quantity, 'notional' : notional})
    return d
    

def update_report(symbols: List[str]) -> None:
    logger.info(f"Updating report with {symbols}")

    # Get positions
    positions = alpaca_trading.get_all_positions()
    total_cost_basis = sum([float(position.cost_basis) for position in positions])  # type: ignore
    total_value = sum([float(position.market_value) for position in positions]) # type: ignore
    total_change_pct = (total_value - total_cost_basis) / total_cost_basis;
    
    # Get portfolio history
    today = datetime.date.today()
    past_date = datetime.date(2023, 6, 19) #first day before starting test
    days_since_start_date = (today - past_date).days
    logger.info(f"Days since start date: {days_since_start_date}")
    portfolio = alpaca_trading.get("/account/portfolio/history", {
        "period": f"{days_since_start_date}D",
        "timeframe": "1D",
    })
    portfolio = parse_obj_as(PortfolioHistory, portfolio)
    
    # Plot graph
    graph_date = portfolio.timestamp
    profit_loss = portfolio.profit_loss
    fig, ax = plt.subplots(figsize=(12, 5), layout="constrained")
    x_values = graph_date[::10]  # Only show every 10th date
    x_labels = [datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d') for x in x_values]
    ax.set_xticks(x_values)
    ax.set_xticklabels(x_labels, rotation=45)
    ax.set_ylabel('PnL', fontweight ='bold')
    ax.set_xlabel('Date', fontweight ='bold')
    ax.set_yticks([0])
    ax.grid(True)
    plt.plot(graph_date, profit_loss)
    plt.axhline(y=0, color='red')
    plt.savefig('history.png')

    # Save readme
    template_output = template('readme.tpl', {
        'symbols': symbols,
        'positions': positions,
        'total_change_pct': total_change_pct,
        'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    readme_md = md(template_output)
    with open('README.md', 'w') as f:
        f.write(readme_md)


if __name__ == "__main__":
    main()

