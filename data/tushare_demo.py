import tushare as ts
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator,DayLocator, MONDAY
from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc,candlestick2_ohlc


stock_code = '601688'
start_at = '2016-01-05'
end_at ='2017-01-01'

stock_df = ts.get_hist_data(stock_code,start=start_at,end=end_at)

#
#
# # # (Year, month, day) tuples suffice as args for quotes_historical_yahoo
date1 = (2016, 1, 5)
date2 = (2017, 1, 1)
#
# #

# #
# quotes = quotes_historical_yahoo_ohlc('INTC', date1, date2)
# print(type(quotes))
# print(quotes)
# #
# # if len(quotes) == 0:
# #     raise SystemExit
# #


fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.2)

mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
alldays = DayLocator()              # minor ticks on the days
weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
dayFormatter = DateFormatter('%d')      # e.g., 12
ax.xaxis.set_major_locator(mondays)
ax.xaxis.set_minor_locator(alldays)
ax.xaxis.set_major_formatter(weekFormatter)
#
# #plot_day_summary(ax, quotes, ticksize=3)
# # candlestick_ohlc(ax, quotes, width=0.6)
opens = list(stock_df.open)
highs = list(stock_df.high)
lows = list(stock_df.low)
closes = list(stock_df.close)
candlestick2_ohlc(ax, opens, highs, lows, closes, width=4, colorup='k', colordown='r', alpha=0.75)


# #ax.xaxis.set_minor_formatter(dayFormatter)
ax.xaxis_date()
ax.autoscale_view()
plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

plt.show()