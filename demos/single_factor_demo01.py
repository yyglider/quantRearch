from datetime import datetime
from data.data_accessor import LoaderFromHdf5
from analyser.strategy import Strategy
from analyser.backtest import Backtest
from util.const import *
import time


start = time.clock()
start_at = datetime(2006, 1, 1)
end_at = datetime(2008, 1, 1)
data = LoaderFromHdf5(start_at, end_at)
backtest_day_list = data.backtest_day_list
factor = 'turn'
strategy = Strategy(data.all_stock_df, backtest_day_list, factor)
# strategy.WITHOUT_MKTCAP_EFFECT=False
#按照市值设置仓位比例
# strategy.position_strategy = POSISION_STRATEGY.BY_MKT_CAP
# strategy.mkt_cap = data.mkt_cap
portfolios = strategy.get_all_portfolio_group()


netvalues = [[] for i in range(10)]

for i in range(10):
    backtest = Backtest(i, portfolios[i], backtest_day_list, data.pct_chg)
    backtest.run()
    netvalues[i] = backtest.netvalue
# print("cost %s second" % (time.clock() - start))
# # backtest = Backtest(0, portfolios[0], backtest_day_list, data.pct_chg)
# # backtest.run()
# # netvalues[0] = backtest.netvalue
#
import numpy as np
import matplotlib.pyplot as plt
plt.figure(1) # 创建图表1

x = np.linspace(0, 1, len(netvalues[0]))
for i in range(10):
    plt.figure(1)
    plt.plot(x, netvalues[i])

plt.show()