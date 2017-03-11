# -*- coding: utf-8 -*-
import click
import logging
from cointrader.config import Config, get_path_to_config
from cointrader.exchange import Poloniex
from cointrader.bot import Cointrader
from cointrader.strategy import InteractivStrategyWrapper
from cointrader.strategies.trend import Followtrend

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
@click.argument("btc", type=float)
@click.option("--resolution", help="Resolution of the chart which is used for trend analysis", default="30m", type=click.Choice(Poloniex.resolutions.keys()))
@click.option("--timeframe", help="Timeframe of the chart which is used for trend analysis", default="1d", type=click.Choice(Poloniex.timeframes.keys()))
@click.option("--automatic", help="Start cointrader in automatic mode.", is_flag=True)
@click.option("--backtest", help="Just backtest the strategy on the chart.", is_flag=True)
@pass_context
def start(ctx, btc, market, resolution, timeframe, automatic, backtest):
    """Start a new bot on the given market and the given amount of BTC"""
    market = ctx.exchange.get_market(market, backtest)
    strategy = Followtrend()
    if not automatic:
        interval = 0  # Disable waiting in interactive mode
        strategy = InteractivStrategyWrapper(strategy)
    elif backtest:
        interval = 0  # Wait 1 second until to the next signal
    else:
        interval = ctx.exchange.resolution2seconds(resolution)
    bot = Cointrader(market, strategy, resolution, timeframe)
    stat = bot.start(btc, interval, backtest)

    click.echo("Traded from {} until {}".format(stat["start"], stat["end"]))
    click.echo("Trading started with a rate of {} BTC and ended at {} BTC".format(stat["start_price"], stat["end_price"]))
    if stat["profit_cointrader"] < stat["profit_chart"]:
        click.echo("Your strategy was less profitable than the market :(")
    elif stat["profit_cointrader"] < stat["start_btc"]:
        click.echo("Your strategy has lost money :(")
    click.echo("Statistic:")
    click.echo("Started with {} BTC".format(stat["start_btc"]))
    click.echo("Ended with {} BTC".format(stat["end_btc"]))
    click.echo("Cointrader makes: {}%".format(round(stat["profit_cointrader"], 2)))
    click.echo("Market makes: {}%".format(round(stat["profit_chart"], 2)))


@click.command()
@click.argument("dollar", type=float)
@pass_context
def exchange(ctx, dollar):
    """Will return how many BTC you get for the given amount of dollar"""
    btc = ctx.exchange.dollar2btc(dollar)
    click.echo("{}$ ~ {}BTC".format(dollar, btc))


main.add_command(explore)
main.add_command(balance)
main.add_command(exchange)
main.add_command(start)
