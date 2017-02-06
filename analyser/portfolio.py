# -*- coding: utf-8 -*-
from collections import OrderedDict


# TODO make field readonly
# TODO use nametuple to reduce memory

# 持仓组合信息
class Portfolio(object):
    def __init__(self, date, stocks, positions, trade_direction, trade_signal=[]):
        self.date = date  # DateTime	  策略投资组合的回测日期
        self.stocks = stocks  # List       组合包含的股票
        self.positions = positions  # List       组合股票对应的仓位，下标和stocks[]一一对应
        self.trade_direction = trade_direction  # Integer    组合当日的买卖策略，1 建仓  -1 平仓  0 持仓
        self.trade_signal = trade_signal  # list       具体到某一只股票的买卖策略，和stocks下标一一对应 (not use at this version)

    def get_postion_dict(self):
        return OrderedDict(zip(self.stocks, self.positions))

    def get_tradeSignal_dict(self):
        return OrderedDict(zip(self.stocks, self.trade_signal))

    def __repr__(self):
        return "Portfolio at ({0}) ({1})".format(self.date, {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith("_")
            })


if __name__ == '__main__':
    import datetime

    group = [{} for i in range(2)]
    # print(group[0],group[1])
    date = datetime.datetime(2016, 8, 19)
    # portfolio1 = Portfolio(date, ['600000.SH', '000001.SZ'], [0.6, 0.4], 1)
    # portfolio2 = Portfolio(date, ['600001.SH', '000002.SZ'], [0.6, 0.4], 1)
    #
    # print(portfolio1,portfolio2)

    #
    # group[0] = dict()
    # group[1] = dict()
    group[0][date] = Portfolio(date, ['600000.SH', '000001.SZ'], [0.6, 0.4], 1)
    group[1][date] = Portfolio(date, ['600001.SH', '000002.SZ'], [0.6, 0.4], 1)
    print(group)

