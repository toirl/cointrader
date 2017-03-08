import datetime
from termcolor import colored
from terminaltables import AsciiTable


def colorize_value(value):
    if value < 0:
        return colored(value, "red")
    else:
        return colored(value, "green")


def render_bot_title(bot, market, resolution, timeframe):

    out = ["\n"]
    chart = market.get_chart(resolution, timeframe)
    data = chart._data

    if len(data) > 1:
        last = data[-2]
    else:
        last = data[-1]
    current = data[-1]

    values = {}
    values["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if current["close"] > last["close"]:
        values["rate"] = colored(current["close"], "green")
    else:
        values["rate"] = colored(current["close"], "red")
    change_percent = (current["close"] - last["close"]) / current["close"] * 100

    values["change_percent"] = round(change_percent, 4)
    values["url"] = market.url
    values["btc"] = bot.btc
    values["amount"] = bot.amount
    values["currency"] = market.currency
    t = u"{date} [{btc} BTC {amount} {currency}] | {rate} ({change_percent}%) | {url}".format(**values)
    out.append("=" * len(t))
    out.append(t)
    out.append("=" * len(t))

    return "\n".join(out)


def render_bot_statistic(stat):
    out = [["", stat["start"], stat["end"], "CHANGE %"]]
    out.append(["COINTRADER VALUE", stat["start_value"], stat["end_value"], "{}".format(colorize_value(round(stat["profit_cointrader"], 2)))])
    out.append(["MARKET RATE", stat["start_rate"], stat["end_rate"], "{}".format(colorize_value(round(stat["profit_chart"], 2)))])
    table = AsciiTable(out).table
    return "\n".join(["\nStatistic:", table])


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
    table = AsciiTable(out).table

    return "\n".join(["\nTradelog:", table])
