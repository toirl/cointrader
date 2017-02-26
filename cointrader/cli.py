# -*- coding: utf-8 -*-
import click
import logging
from .config import Config, get_path_to_config
from .exchange import Poloniex
from .cointrader import Cointrader
from .strategy import InteractivStrategyWrapper
from .strategies.trend import Followtrend

log = logging.getLogger(__name__)


class Context(object):

    """Docstring for Context. """

    def __init__(self):
        self.exchange = None


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
@click.option("--config", help="Configuration File for cointrader.", type=click.File("r"))
@pass_context
def main(ctx, config):
    """Console script for cointrader on the Poloniex exchange"""
    if config:
        config = Config(config)
    else:
        config = Config(open(get_path_to_config(), "r"))
    ctx.exchange = Poloniex(config)


@click.command()
@click.option("--order-by-volume", help="Order markets by their trading volume", is_flag=True)
@click.option("--order-by-profit", help="Order markets by their current profit", is_flag=True)
@click.option("--limit", help="Limit output to NUM markets", default=3)
@pass_context
def explore(ctx, order_by_volume, order_by_profit, limit):
    """List top markets. On default list markets which are profitable and has a high volume."""
    markets = ctx.exchange.markets
    if not order_by_volume and not order_by_profit:
        markets = ctx.exchange.get_top_markets(markets, limit)
        for market in markets:
            url = "https://poloniex.com/exchange#{}".format(market[0].lower())
            click.echo("{:<10} {:>6}% {:>10} {:>20}".format(market[0], market[1]["change"], market[1]["volume"], url))
    elif order_by_volume:
        markets = ctx.exchange.get_top_volume_markets(markets, limit)
        for market in markets:
            url = "https://poloniex.com/exchange#{}".format(market[0].lower())
            click.echo("{:<10} {:>10} {:>6}% {:>20}".format(market[0], market[1]["volume"], market[1]["change"], url))
    elif order_by_profit:
        markets = ctx.exchange.get_top_profit_markets(markets, limit)
        for market in markets:
            url = "https://poloniex.com/exchange#{}".format(market[0].lower())
            click.echo("{:<10} {:>6}% {:>10} {:>20}".format(market[0], market[1]["change"], market[1]["volume"], url))


@click.command()
@pass_context
def balance(ctx):
    """Overview of your balances on the market."""
    click.echo("{:<4}  {:>12} {:>12}".format("CUR", "total", "btc_value"))
    click.echo("{}".format("-" * 31))
    coins = ctx.exchange.coins
    for currency in coins:
        click.echo("{:<4}: {:>12} {:>12}".format(currency, coins[currency].quantity, coins[currency].value))
    click.echo("{}".format("-" * 31))
    click.echo("{:<9}: {:>20}".format("TOTAL BTC", ctx.exchange.total_btc_value))
    click.echo("{:<9}: {:>20}".format("TOTAL USD", ctx.exchange.total_euro_value))


@click.command()
@click.argument("market")
@click.option("--resolution", help="Resolution of the chart which is used for trend analysis", default="30m")
@click.option("--timeframe", help="Timeframe of the chart which is used for trend analysis", default="1d")
@click.option("--automatic", help="Start cointrader in automatic mode.", is_flag=True)
@pass_context
def start(ctx, market, resolution, timeframe, automatic):
    """Start a new bot on the given market"""
    # balance = ctx.exchange.get_balance("BTC")
    # btc = balance["btc_value"]

    # # Calculate position to trade:
    # trade_btc = btc * position
    # trade_dollar = ctx.exchange.btc2dollar(trade_btc)
    # log.debug("Will trade {}BTC / {}$ ({}%) out of total {}BTC".format(trade_btc, trade_dollar, position, btc))

    market = ctx.exchange.get_market(market)
    strategy = Followtrend()
    if not automatic:
        interval = 0  # Disable waiting in interactive mode
        strategy = InteractivStrategyWrapper(strategy)
    else:
        interval = ctx.exchange.resolution2seconds(resolution)
    bot = Cointrader(market, strategy, resolution, timeframe)
    bot.start(interval)


main.add_command(explore)
main.add_command(balance)
main.add_command(start)

if __name__ == "__main__":
    main()
