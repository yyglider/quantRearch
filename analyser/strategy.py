# -*- coding: utf-8 -*-

# 按照一定策略生成每日的组合
# TODO 选股时筛掉涨跌停的股票

from analyser.portfolio import Portfolio
from math import floor
from collections import OrderedDict,defaultdict
from util.logger import log
from util.const import POSISION_STRATEGY


class Strategy(object):
    cap_group_num = 10                                                  # 按照市值分10组
    interval = 21                                                       # 调仓间隔，或者叫持仓天数
    open_at =  21                                                       # 默认在第22个回测日建仓（下标从0开始）
    WITHOUT_MKTCAP_EFFECT = True                                        # 分组时是否去除市值影响，默认为True

    def __init__(self, all_stocks_dataframe, backtest_day_list, factor, factor_group_num=10,
                 position_strategy=POSISION_STRATEGY.EQUAL, mkt_cap = None):
        self.factor = factor                                            # 待回测的因子
        self.all_df = all_stocks_dataframe                              # 传入所有股票的dataframe格式的数据，通过data_accessor.LoaderFromHdf5获取
        self.backtest_day_list = backtest_day_list                      # 回测日期列表
        self.factor_group_num = factor_group_num                        # 新因子默认分10组
        self.position_strategy = position_strategy                      # 默认按等额/市值/自定义（TODO 实现自定义仓位分配）
        self.portfolio_group = [OrderedDict() for i in range(self.factor_group_num)]  # { groupNo: {date : portfolio object} }，存放组合数据
        self.mkt_cap = mkt_cap                                          # { code: {date:mkt_cap}}, 存放股票市值历史数据


    def get_all_portfolio_group(self):
        log.info("开始设置回测日的组合...")
        backtest_days = len(self.backtest_day_list)
        self.__portfolio_generator(backtest_days)
        log.info("组合设置执行完毕!")
        return self.portfolio_group

    # 更新每个调仓日的组合
    # TODO 使用传递函数来实现，即在外层定义策略
    def __portfolio_generator(self, backtest_days):
        if backtest_days < self.interval:
            raise Exception('调仓间隔不可大于回测的天数')
        for iDay in range(0, self.open_at):
            self.__not_util_open_day(iDay)
        for iDay in range(self.open_at, backtest_days):
            # 平仓, 在回测日最后一天
            if iDay == backtest_days - 1:
                self.__close(iDay)
            # 调仓
            elif iDay == self.open_at or iDay % self.interval == 0:
                date = self.backtest_day_list[iDay]
                # list of list, 在调仓日筛选符合条件的股票,返回分组后各小组的持仓股票列表
                stocks_list = self.__single_factor_strategy(self.factor, iDay)
                # list of list, 各组合中各股票对应的仓位比例，与stocks_list一一对应
                positions_list = [self.__config_position(stocks,date) for stocks in stocks_list]
                # 生成字典 groupNo : {date:portfolio}
                for groupNo in range(self.factor_group_num):
                    self.portfolio_group[groupNo][date] = Portfolio(date, stocks_list[groupNo], positions_list[groupNo], 1)
            # 持仓
            else:
                self.__hold(iDay)

    # 单因子策略
    def __single_factor_strategy(self, factor, day):
        if self.WITHOUT_MKTCAP_EFFECT:
            # 待买入的股票停牌、变为ST、开盘涨停或开盘跌停，则不买入
            # 开盘价./前收<1.098（开盘未涨停）
            # 开盘价./前收>0.901（开盘未跌停）
            # df2 = self.all_df.loc[(self.all_df['date'] == self.backtest_day_list[day]) & (self.all_df['st'] == False) &
            #                       (self.all_df['volume'] > 1) & (self.all_df['to_ipo_days'] > 180) &
            #                       (self.all_df['open'] / self.all_df['pre_close'] < 1.098) & (self.all_df['open'] / self.all_df['pre_close'] > 0.901),
            #                       ['code', 'mkt_cap_ard', factor]].sort_values(['mkt_cap_ard'], ascending=True)

            df2 = self.all_df.loc[(self.all_df['date'] == self.backtest_day_list[day]) & (self.all_df['st'] == False) &
                                  (self.all_df['volume'] > 1) & (self.all_df['to_ipo_days'] > 180),
                                  ['code', 'mkt_cap_ard', factor]].sort_values(['mkt_cap_ard'], ascending=True)

            # 去除市值影响
            total_stock_num = df2.shape[0]
            # print(self.backtest_day_list[day],'选出来所有的股票',total_stock_num)

            j = floor(total_stock_num / self.cap_group_num)  # 按市值分组，每组的股票个数
            # print(self.backtest_day_list[day],'按市值分组，每组的股票个数',j)
            cap_groups = [df2[i:i + j] for i in range(0, total_stock_num, j) if i + j <= total_stock_num]
            # 每组按照factor_name进行排序,排序后的每组再分组
            # j是按市值分组后每组的股票数，k市值小组再分factor_group_num个组后，每组的股票个数
            k = floor(j / self.factor_group_num)
            # print(self.backtest_day_list[day],'市值小组再分factor_group_num个组后，每组的股票个数',k)

            stocks_list = []
            for n in range(0, self.cap_group_num):
                cap_groups[n] = cap_groups[n].sort_values([factor], ascending=True)
                df3 = cap_groups[n]
                # 每个市值小组内再按factor进行分组，分k组
                factor_groups = [df3[i:i + k] for i in range(0, j, k) if i + k <= j]
                # 将各市值分组中的各factor小组对应组合成新的组
                for i in range(0, self.factor_group_num):
                    if n == 0:
                        stocks_list.insert(i, list(factor_groups[i].code))
                    else:
                        stocks_list[i].extend(list(factor_groups[i].code))
            return stocks_list

        else:
            df2 = self.all_df.loc[(self.all_df['date'] == self.backtest_day_list[day]) & (self.all_df['st'] == False) &
                                  (self.all_df['volume'] > 1) & (self.all_df['to_ipo_days'] > 180) &
                                  (self.all_df['open'] / self.all_df['pre_close'] < 1.098) &
                                  (self.all_df['open'] / self.all_df['pre_close'] > 0.901),
                                  ['code', factor]].sort_values([factor], ascending=True)
            total_stock_num = df2.shape[0]
            j = floor(total_stock_num / self.factor_group_num)  # 按factor分组，每组的股票个数
            stocks_list = [list(df2[i:i + j].code) for i in range(0, total_stock_num, j) if i + j <= total_stock_num]
            return stocks_list

    def __config_position(self, stocks, day):
        # 均等设置仓位
        if self.position_strategy == POSISION_STRATEGY.EQUAL:
            return [1 / len(stocks)] * len(stocks)
        # 按照市值设置仓位 self.mkt_cap['000001.SH'][day]
        if self.position_strategy == POSISION_STRATEGY.BY_MKT_CAP:
            portfolio_mktcap = [self.mkt_cap[code][day] for code in stocks]
            sum_makcap = sum(portfolio_mktcap)
            return [self.mkt_cap[code][day] / sum_makcap for code in stocks]

    def __not_util_open_day(self, day):
        date = self.backtest_day_list[day]
        for groupNo in range(self.factor_group_num):
            self.portfolio_group[groupNo][date] = Portfolio(date,[],[],0)

    def __hold(self, day):
        date_current = self.backtest_day_list[day]
        date_before = self.backtest_day_list[day-1]
        for groupNo in range(self.factor_group_num):
            stocks_before = self.portfolio_group[groupNo][date_before].stocks
            positions_before = self.portfolio_group[groupNo][date_before].positions
            self.portfolio_group[groupNo][date_current] = Portfolio(date_current, stocks_before,positions_before, 0)

    def __close(self, day):
        date_current = self.backtest_day_list[day]
        before_current = self.backtest_day_list[day-1]
        for groupNo in range(self.factor_group_num):
            self.portfolio_group[groupNo][date_current] = Portfolio(date_current,[],[],-1)


if __name__ == '__main__':
    from data.data_accessor import LoaderFromHdf5
    import pandas as pd
    import datetime
    start_at = datetime.datetime(2003, 1, 1)
    end_at = datetime.datetime(2004, 1, 1)
    data = LoaderFromHdf5(start_at, end_at)

    generator = Strategy(data.all_stock_df, data.backtest_day_list,'turn')
    # generator.mkt_cap = data.mkt_cap
    # generator.position_strategy = POSISION_STRATEGY.BY_MKT_CAP

    date = pd.Timestamp(datetime.datetime(2003, 12, 18))
    portfolios = generator.get_all_portfolio_group()
    portfolios = generator.portfolio_group
    #print(portfolios[0][date],portfolios[9][date])
