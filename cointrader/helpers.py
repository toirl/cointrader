from termcolor import colored
from terminaltables import AsciiTable


def colorize_value(value):
    if value < 0:
        return colored(value, "red")
    else:
        return colored(value, "green")


def render_bot_statistic(stat):
    out = [["", stat["start"], stat["end"], "CHANGE %"]]
    out.append(["COINTRADER VALUE", stat["start_value"], stat["end_value"], "{}".format(colorize_value(round(stat["profit_cointrader"], 2)))])
    out.append(["MARKET RATE", stat["start_rate"], stat["end_rate"], "{}".format(colorize_value(round(stat["profit_chart"], 2)))])
    return AsciiTable(out).table


def render_bot_tradelog(trades):
    out = [["DATE", "TYPE", "RATE", "COINS", "BTC", "VALUE", "PROFIT"]]
    last_trade = None
    total_profit = 0
    for trade in trades:
        values = []
        values.append(trade.date)
        values.append(trade.order_type)
        values.append(trade.rate)
        values.append(trade.amount)
        values.append(trade.btc)
        values.append(trade.value)
        if last_trade:
            profit = trade.value - last_trade.value
            total_profit += profit
            profit = colorize_value(profit)
            values.append(profit)
        else:
            values.append(0)
        out.append(values)
        last_trade = trade
    total_profit = colorize_value(total_profit)
    out.append(["", "", "", "", "", "", "-" * len(str(trade.value)), "-" * len(str(total_profit))])
    out.append(["", "", "", "", "", "", trade.value, total_profit])
    return AsciiTable(out).table
