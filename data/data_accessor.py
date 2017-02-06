# load data from mongo to memory as pandas.dataframe so as to reduce IO frequency

import pandas as pd
from collections import defaultdict
from util.mongoUtils import mongoUtils
from util.confRead import Config
from util.logger import log


from util.tools import time_me

'''hdf5 data loader'''
class LoaderFromHdf5(object):
    pct_chg = defaultdict(dict)
    mkt_cap = defaultdict(dict)

    def __init__(self, start_at, end_at):
        log.info('开始加载数据 ...')
        self.__load_all()
        self.__load_stockdata_by_date(start_at, end_at)
        self.__load_indexdata_by_date(start_at, end_at)  # load all index data fields
        self.__load_backtest_day_list()
        self.__load_stock_pct_chg()
        self.__load_index_pct_chg()
        self.__load_stock_mkt_cap()
        log.info('数据加载完毕!')

    # load all data from local hdf5
    def __load_all(self):
        config_file_path = '../conf/config.ini'
        config = Config(config_file_path)
        file_h5_index = config.get('HDF5', 'index_h5').strip()
        file_h5_stock = config.get('HDF5', 'stock_h5').strip()
        all_stock_hdf = pd.read_hdf(file_h5_stock)
        all_index_hdf = pd.read_hdf(file_h5_index)
        self.all_stock_df = pd.DataFrame.from_records(all_stock_hdf)
        self.all_index_df = pd.DataFrame.from_records(all_index_hdf)

    # load all stock data from (start_at , end_at) as pandas.dataframe
    def __load_stockdata_by_date(self, start_at, end_at):
        log.info('加载股票数据 ...')
        self.stock_data = self.all_stock_df.loc[
            (self.all_stock_df['date'] >= start_at) & (self.all_stock_df['date'] <= end_at)]
        self.stock_data.fillna(0, inplace=True)

    # load all index data from (start_at , end_at) as pandas.dataframe
    def __load_indexdata_by_date(self, start_at, end_at):
        log.info('加载指数数据 ...')
        self.index_data = self.all_index_df.loc[
            (self.all_index_df['date'] >= start_at) & (self.all_index_df['date'] <= end_at)]
        self.index_data.fillna(0, inplace=True)

    # load backtest day list
    def __load_backtest_day_list(self):
        log.info('加载回测交易日数据 ...')
        self.backtest_day_list = [pd.Timestamp(x) for x in list(self.index_data.date.unique())]  # 为了和pct_chg统一格式?

    # load pct_chg from stock_data
    # dictionary , { iCode : [pct_chg at backtest day 1 ,pct_chg at backtest day 2, ... ,pct_chg at backtest day i] }
    # use: pct_chg['000001.SH'][date]
    def __load_stock_pct_chg(self):
        log.info('加载股票涨跌幅数据 ...')
        pct_chg_df = self.stock_data.loc[:, ['code', 'date', 'pct_chg']].groupby(['code'])
        for key, values in pct_chg_df:
            self.pct_chg[key]  = values.set_index('date')['pct_chg'].to_dict()
            # self.pct_chg[key] = dict(zip(values['date'], values['pct_chg']))



    # load pct_chg from all index data
    def __load_index_pct_chg(self):
        log.info('开始加载指数涨跌幅数据 ...')
        pct_chg_df = self.index_data.loc[:, ['code', 'date', 'pct_chg']].groupby(['code'])
        for key, values in pct_chg_df:
            self.pct_chg[key] = values.set_index('date')['pct_chg'].to_dict()
            # self.pct_chg[key] = dict(zip(values['date'], values['pct_chg']))


    # load mkt_cap from all stock data
    # dictionary , { iCode : [mkt_cap at backtest day 1 ,mkt_cap at backtest day 2, ... ,mkt_cap at backtest day i] }
    # use: mkt_cap['000001.SH'][date]
    def __load_stock_mkt_cap(self):
        mkt_cap_df = self.stock_data.loc[:, ['code', 'date', 'mkt_cap_ard']].groupby(['code'])
        for key, values in mkt_cap_df:
            self.mkt_cap[key] = values.set_index('date')['mkt_cap_ard'].to_dict()
            # self.mkt_cap[key] = dict(zip(values['date'], values['mkt_cap_ard']))



'''mongo data loader'''
class LoaderFromMongo(object):
    pct_chg = defaultdict(dict)
    mkt_cap = defaultdict(dict)

    def __init__(self, start_at, end_at, query_stock_fields):
        log.info('连接数据库，开始加载数据 ...')

        self.__db_config()
        self.__load_stockdata_by_date(start_at, end_at, query_stock_fields)
        self.__load_indexdata_by_date(start_at, end_at,
                                      ['date', 'code', 'close', 'pct_chg', 'open', 'high', 'low', 'volume',
                                       'amt'])  # load all index data fields
        self.__load_backtest_day_list()
        self.__load_stock_pct_chg()
        self.__load_index_pct_chg()
        self.__load_stock_mkt_cap()
        log.info('数据加载完毕!')

    # mongo config
    def __db_config(self):
        config_file_path = '../conf/config.ini'
        config = Config(config_file_path)
        host = config.get('Server', 'host').strip()
        port = config.get('Server', 'port').strip()
        db_name = config.get('Database', 'db_name').strip()
        self.stock_collection = config.get('Database', 'stock_collection').strip()
        self.index_collection = config.get('Database', 'index_collection').strip()
        self.mongoClient = mongoUtils(host, port, db_name)

    # load all stock data from (start_at , end_at) as pandas.dataframe
    def __load_stockdata_by_date(self, start_at, end_at, query_fields):
        log.info('开始加载股票数据 ...')
        query_condition = {"date": {"$gte": start_at, "$lte": end_at}}
        query_fields = {field: 1 for field in query_fields}
        self.all_df = self.mongoClient.read_as_dataframe(self.stock_collection, query_condition, query_fields)
        self.all_df.fillna(0, inplace=True)

    # load all index data from (start_at , end_at) as pandas.dataframe
    def __load_indexdata_by_date(self, start_at, end_at, query_fields):
        log.info('开始加载指数数据 ...')
        query_condition = {"date": {"$gte": start_at, "$lte": end_at}}
        query_fields = {field: 1 for field in query_fields}
        self.all_index_df = self.mongoClient.read_as_dataframe(self.index_collection, query_condition, query_fields)

    # load backtest day list
    def __load_backtest_day_list(self):
        log.info('开始加载回测交易日数据 ...')
        self.backtest_day_list = [pd.Timestamp(x) for x in list(self.all_df.date.unique())]  # 为了和pct_chg统一格式

    # load pct_chg from all stock data
    # dictionary , { iCode : [pct_chg at backtest day 1 ,pct_chg at backtest day 2, ... ,pct_chg at backtest day i] }
    # use: pct_chg['000001.SH'][date]
    def __load_stock_pct_chg(self):
        log.info('开始加载股票涨跌幅数据 ...')
        pct_chg_df = self.all_df.loc[:, ['code', 'date', 'pct_chg']].groupby(['code'])
        for key, values in pct_chg_df:
            self.pct_chg[key] = values.set_index('date')['pct_chg'].to_dict()
            # self.pct_chg[key] = dict(zip(values['date'], values['pct_chg']))

    # load pct_chg from all index data
    def __load_index_pct_chg(self):
        log.info('开始加载指数涨跌幅数据 ...')
        pct_chg_df = self.all_index_df.loc[:, ['code', 'date', 'pct_chg']].groupby(['code'])
        for key, values in pct_chg_df:
            self.pct_chg[key] = values.set_index('date')['pct_chg'].to_dict()
            # self.pct_chg[key] = dict(zip(values['date'], values['pct_chg']))

    # load mkt_cap from all stock data
    # dictionary , { iCode : [mkt_cap at backtest day 1 ,mkt_cap at backtest day 2, ... ,mkt_cap at backtest day i] }
    # use: mkt_cap['000001.SH'][date]
    def __load_stock_mkt_cap(self):
        mkt_cap_df = self.all_df.loc[:, ['code', 'date', 'mkt_cap_ard']].groupby(['code'])
        for key, values in mkt_cap_df:
            self.mkt_cap[key] = values.set_index('date')['mkt_cap_ard'].to_dict()
            # self.mkt_cap[key] = dict(zip(values['date'], values['mkt_cap_ard']))





if __name__ == '__main__':
    import datetime
    import time

    start_at = datetime.datetime(2006, 5, 7)
    end_at = datetime.datetime(2015, 6, 7)
    start = time.clock()

    data = LoaderFromHdf5(start_at, end_at)
    df = data.all_stock_df
    #backtest_day = data.backtest_day_list
    print(data.pct_chg['000515.SZ'][pd.Timestamp('2009-05-07 00:00:00')])
    # print(data.backtest_day_list)

    print("cost %s second" % (time.clock() - start))