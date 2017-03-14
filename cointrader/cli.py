# -*- coding: utf-8 -*-
import click
import sys
import datetime
import logging
from cointrader import db, STRATEGIES
from cointrader.config import Config, get_path_to_config
from cointrader.exchange import Poloniex
from cointrader.bot import init_db, get_bot
from cointrader.strategy import InteractivStrategyWrapper
from cointrader.helpers import render_bot_statistic, render_bot_tradelog

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
    init_db()
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
@click.option("--start", help="Datetime to begin trading", default=None)
@click.option("--end", help="Datetime to end trading", default=None)
@click.option("--automatic", help="Start cointrader in automatic mode.", is_flag=True)
@click.option("--backtest", help="Just backtest the strategy on the chart.", is_flag=True)
@click.option("--papertrade", help="Just simulate the trading.", is_flag=True)
@click.option("--strategy", help="Stratgegy used for trading.", default="Wait", type=click.Choice(STRATEGIES.keys()))
@click.option("--btc", help="Set initial amount of BTC the bot will use for trading.", type=float)
@click.option("--coins", help="Set initial amount of coint the bot will use for trading.", type=float)
@pass_context
def start(ctx, market, resolution, start, end, automatic, backtest, papertrade, strategy, btc, coins):
    """Start a new bot on the given market and the given amount of BTC"""
    market = ctx.exchange.get_market(market, backtest, papertrade)
    strategy = STRATEGIES[strategy]()

    if start:
        start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    if end:
        end = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

    if not automatic:
        interval = 0  # Disable waiting in interactive mode
        strategy = InteractivStrategyWrapper(strategy)
    elif backtest:
        if start is None or end is None:
            click.echo("Error! For backtests you must provide a timeframe by setting start and end!")
            sys.exit(1)
        interval = 0  # Disable waiting in backtest mode
    else:
        interval = ctx.exchange.resolution2seconds(resolution)

    bot = get_bot(market, strategy, resolution, start, end, btc, coins)
    bot.start(interval, backtest)

    if backtest:
        click.echo(render_bot_tradelog(bot.trades))
        click.echo(render_bot_statistic(bot.stat(backtest)))
        db.delete(bot)
        db.commit()


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
