# -*- coding: utf-8 -*-

# 执行具体回测逻辑的类

from util.logger import log
from util.const import INTEREST_TYPE


class Backtest(object):
    HedgeSymbolCol = '000300.SH'             # String 基准指数代码
    sell_cost = 0.003                        # float 卖出成本
    buy_cost = 0.003                         # float 买入成本
    interest_type = INTEREST_TYPE.COMPOUND   # ENUM  计算方式，默认复利 ，单利interest_type = INTEREST_TYPE.SIMPLE

    def __init__(self, portfolioNo, portfolio, backtest_day_list, pct_chg):
        self.portfolioNo = portfolioNo
        self.portfolio = portfolio                                  # OrderedDic 每日持仓组合的，date: portfolio
        self.backtest_day_list = backtest_day_list                  # list 记录执行回测的具体交易日
        self.pct_chg = pct_chg                                      # defaultdict(dict) 每个回测日个股票/指数的pct_chg, use as: pct_chg['000001.SH'][datetime]
        self.netvalue = [1] * (len(self.backtest_day_list)+1)       # list 记录每个回测日的净值（从开仓日开始算起）
        self.daliy_return = [0] * (len(self.backtest_day_list)+1)   # list 每日收益

    def run_as_compound(self):
        # 如果第一天就建仓
        first_day = self.backtest_day_list[0]

        if self.portfolio[first_day].trade_direction == 1:
            daliy_pct_chg = [self.pct_chg[code][first_day] for code in self.portfolio[first_day].stocks]
            self.daliy_return[1] = self.__multiply_and_sum(self.portfolio[first_day].positions, daliy_pct_chg) \
                                      - self.pct_chg[self.HedgeSymbolCol][first_day]
            self.netvalue[1] = self.netvalue[0] * (1 + self.daliy_return[1]) * (1 - self.buy_cost)
        # 从第二天开始
        for (iDay,current_date) in enumerate(self.backtest_day_list[1:],start=1):
            # 当前持仓不为空时，计算当日组合收益和净值
            before_day = self.backtest_day_list[iDay - 1]  # 前日
            if self.portfolio[current_date].stocks:
                daliy_pct_chg = [self.pct_chg[code][current_date] for code in self.portfolio[current_date].stocks]

                self.daliy_return[iDay + 1] = self.__multiply_and_sum(self.portfolio[current_date].positions,
                                                                 daliy_pct_chg) \
                                          - self.pct_chg[self.HedgeSymbolCol][current_date]
            else:
                self.daliy_return[iDay + 1] = 0
            # 前日有持仓
            if self.portfolio[before_day].stocks:
                # 前日有持仓、当日调仓
                if self.portfolio[current_date].trade_direction == 1:
                    self.netvalue[iDay] *= 1 - self.sell_cost  # 先全卖，再全买
                    self.netvalue[iDay + 1] = self.netvalue[iDay] * (1 + self.daliy_return[iDay + 1]) * (1 - self.buy_cost)
                # 前日有持仓、当日持仓
                elif self.portfolio[current_date].trade_direction == 0:
                    self.netvalue[iDay + 1] = self.netvalue[iDay] * (1 + self.daliy_return[iDay + 1])

                # 前日有持仓、当日平仓
                else:
                    self.netvalue[iDay] *= 1 - self.sell_cost
                    self.netvalue[iDay + 1] = self.netvalue[iDay]
            # 前日无持仓
            else:
                # 前日无持仓、当日建仓
                if self.portfolio[current_date].trade_direction == 1:
                    self.netvalue[iDay + 1] = self.netvalue[iDay] * (1 + self.daliy_return[iDay + 1]) * (1 - self.buy_cost)
                # 前日无持仓、当日仓位不变
                elif self.portfolio[current_date].trade_direction == 0:
                    self.netvalue[iDay + 1] = self.netvalue[iDay]
                else:
                    continue



    def run_as_simple(self):
        # 如果第一天就建仓
        first_day = self.backtest_day_list[0]

        if self.portfolio[first_day].trade_direction == 1:
            daliy_pct_chg = [self.pct_chg[code][first_day] for code in self.portfolio[first_day].stocks]
            self.daliy_return[1] = self.__multiply_and_sum(self.portfolio[first_day].positions, daliy_pct_chg) \
                                   - self.pct_chg[self.HedgeSymbolCol][first_day]
            self.netvalue[1] = (self.netvalue[0] + self.daliy_return[1]) * (1 - self.buy_cost)

        # 从第二天开始
        for (iDay, current_date) in enumerate(self.backtest_day_list[1:], start=1):
            # 当前持仓不为空时，计算当日组合收益和净值
            before_day = self.backtest_day_list[iDay - 1]  # 前日
            if self.portfolio[current_date].stocks:
                daliy_pct_chg = [self.pct_chg[code][current_date] for code in self.portfolio[current_date].stocks]
                self.daliy_return[iDay + 1] = self.__multipy_and_sum(self.portfolio[current_date].positions,
                                                                 daliy_pct_chg) \
                                          - self.pct_chg[self.HedgeSymbolCol][current_date]
            else:
                self.daliy_return[iDay + 1] = 0
            # 前日有持仓
            if self.portfolio[before_day].positions:
                # 前日有持仓、当日调仓
                if self.portfolio[current_date].trade_direction == 1:
                    self.netvalue[iDay] *= 1 - self.sell_cost
                    self.netvalue[iDay + 1] = (self.netvalue[iDay] + self.daliy_return[iDay + 1]) * (1 - self.buy_cost)
                # 前日有持仓、当日仓位不变
                elif self.portfolio[current_date].trade_direction == 0:
                    self.netvalue[iDay + 1] = self.netvalue[iDay] + self.daliy_return[iDay + 1]
                # 前日有持仓、当日平仓
                else:
                    self.netvalue[iDay] *= 1 - self.sell_cost
                    self.netvalue[iDay + 1] = self.netvalue[iDay]
            else:
                # 前日无持仓、当日建仓
                if self.portfolio[current_date].trade_direction == 1:
                    self.netvalue[iDay + 1] = (self.netvalue[iDay] + self.daliy_return[iDay + 1]) * (1 - self.buy_cost)
                # 前日无持仓、当日仓位不变
                elif self.portfolio[current_date].trade_direction == 0:
                    self.netvalue[iDay + 1] = self.netvalue[iDay]
                else:
                    continue

    def run(self):
        if self.interest_type == INTEREST_TYPE.COMPOUND:
            log.info(("组合:{portfolioNo}, {message}").format(
                portfolioNo=self.portfolioNo,
                message='使用复利方式开始回测 ...',
            ))
            self.run_as_compound()
            log.info(("组合:{portfolioNo}, {message}").format(
                portfolioNo=self.portfolioNo,
                message='回测结束!',
            ))

        if self.interest_type == INTEREST_TYPE.SIMPLE:
            log.info(("组合:{portfolioNo}, {message}").format(
                portfolioNo=self.portfolioNo,
                message='使用单利利方式开始回测 ...',
            ))
            self.run_as_simple()
            log.info(("组合:{portfolioNo}, {message}").format(
                portfolioNo=self.portfolioNo,
                message='回测结束!',
            ))

    def __multiply_and_sum(self, list_a, list_b):
        return sum(list(map(lambda x, y: x * y, list_a, list_b)))

if __name__ == '__main__':

    from analyser.strategy import Strategy
    from datetime import datetime
    from data.data_accessor import LoaderFromHdf5
    from util.const import POSISION_STRATEGY

    start_at = datetime(2009, 1, 1)
    end_at = datetime(2009, 6, 1)
    data = LoaderFromHdf5(start_at, end_at)
    backtest_day_list = data.backtest_day_list
    # factor = 'mkt_cap_ard'
    factor = 'turn'
    strategy = Strategy(data.all_stock_df, backtest_day_list, factor)
    # 按照市值设置仓位比例
    # strategy.position_strategy = POSISION_STRATEGY.BY_MKT_CAP
    # strategy.mkt_cap = data.mkt_cap
    portfolios = strategy.get_all_portfolio_group()


    #generator.mkt_cap = data.mkt_cap
    # generator.position_strategy = POSISION_STRATEGY.BY_MKT_CAP
    backtest = Backtest(0, portfolios[0], data.backtest_day_list, data.pct_chg)
    backtest.run()
    print(backtest.netvalue)
    # plt.figure()
    # x = np.linspace(0,len(backtest.netvalue))
    # plt.plot(x,backtest.netvalue)