import logging
import os
import argparse

from typing import List, Dict
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import TimeInForce, OrderSide, OrderType
from alpaca.trading.requests import OrderRequest
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data.historical.stock import StockHistoricalDataClient
from markdownify import markdownify as md
from bottle import SimpleTemplate, template
from dotenv import load_dotenv

load_dotenv()

LOG_FORMAT = '%(asctime)s %(name)10.10s %(levelname).7s %(filename)15.15s %(lineno)-4s %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
logger = logging.getLogger('DCA')

alpaca_endpoint = os.getenv("ALPACA_ENPOINT")
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
    positions = alpaca_trading.get_all_positions()
    history = alpaca_trading.get_account()
    logger.info(f"Positions: {positions}")
    template_output = template('readme.tpl', {
        'symbols': symbols,
    })
    readme_md = md(template_output)
    with open('README.md', 'w') as f:
        f.write(readme_md)


if __name__ == "__main__":
    main()

