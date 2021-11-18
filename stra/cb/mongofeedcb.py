# -*- coding: utf-8 -*-
# @Time : 2021/11/16 20:27
# @Author : Lucio
# @Site : 
# @File : mongofeed.py
# @Software: PyCharm
import backtrader as bt
import pymongo



class MongoData(bt.feed.DataBase):
    lines = ('transprice',)

    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        # name of the table is indicated by dataname
        # data is fetch between fromdate and todate
        assert (self.p.fromdate is not None)
        assert (self.p.todate is not None)

        # name of db
        self.db = db

        # iterator 4 data in the list
        self.iter = None
        self.data = None

    def start(self):
        super().start()
        if self.data is None:
            # connect to mongo db local default config
            client = pymongo.MongoClient('mongodb://localhost:27017/')
            db = client[self.db]
            collection = db[self.p.dataname]
            self.data = list(collection.find({'交易日期_TrdDt': {'$gte': self.p.fromdate, '$lte': self.p.todate}}))
            client.close()
        # set the iterator anyway
        self.iter = iter(self.data)

    def stop(self):
        pass

    def _load(self):
        if self.iter is None:
            # if no data ... no parsing
            return False

        # try to get 1 row of data from iterator
        try:
            row = next(self.iter)
        except StopIteration:
            # end of the list
            return False

        # fill the lines
        self.lines.datetime[0] = self.date2num(row['交易日期_TrdDt'])
        self.lines.open[0] = row['开盘价(元)_OpPr']
        self.lines.high[0] = row['最高价(元)_HiPr']
        self.lines.low[0] = row['最低价(元)_LoPr']
        self.lines.close[0] = row['收盘价(元)_ClPr']
        self.lines.volume[0] = row['成交量(股)_TrdVol']
        self.lines.openinterest[0] = -1
        # 需要加入数据需要在init上添加 并在此处添加
        self.lines.transprice[0] = row['转股溢价率(%)_ConvPreRt']

        # Say success
        return True