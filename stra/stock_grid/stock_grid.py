# -*- coding: utf-8 -*-
# @Time : 2021/10/10 13:58
# @Author : Lucio
# @Site :
# @File : sample_strategy.py
# @Software: PyCharm


from new_grid2 import multiGridStrategy
from mongofeedgrid import MongoData
import backtrader as bt
import os.path
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo
import datetime
from pymongo import MongoClient


if __name__ == '__main__':
    c = MongoClient('mongodb://localhost:27017/')
    db = 'quantfinance'
    code_list = c[db].collection_names()
    # 具象化实例
    cerebro = bt.Cerebro()
    # 手续费千1
    cerebro.broker.setcommission(commission=0.001)
    for code in code_list[:]:
        data = MongoData(
                db=db,
                dataname=code,
                fromdate=datetime.datetime(2016, 5, 3),
                todate=datetime.datetime(2021, 10, 28))
        cerebro.adddata(data, name=code[:9])
    cerebro.broker.setcash(20000000.0)
    # 获取账户价值
    print('开始账户价值：{}'.format(cerebro.broker.getvalue()))
    # 计算最优参数
    strats = cerebro.optstrategy(multiGridStrategy, period=range(20, 80, 20), count=range(20, 80, 20))
    # cerebro.addstrategy(multiGridStrategy, poneplot=False)
    # 加入分析器
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SP')
    strats = cerebro.run()
    strat = strats[0]
    b = Bokeh(style='bar', plot_mode='single', scheme=Tradimo())
    # 绘图
    cerebro.plot(b)
    print('夏普比率', strat.analyzers.SP.get_analysis())
    print('最大回撤', strat.analyzers.DW.get_analysis())
    print('结束账户价值: {}'.format(cerebro.broker.getvalue()))






    # strat = results[0]
    # pyfoliozer = strat.analyzers.getbyname('pyfolio')
    # returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()

    # import pyfolio as pf

    # pf.create_full_tear_sheet(
    #     returns,
    #     positions=positions,
    #     transactions=transactions,
    #     live_start_date='20170503',  # 指定日期
    #     round_trips=True)

    # 未复权 复权需要重新下载
    # multiply stock
    # os.chdir('D:/大学/量化投资/数据/OldData')
    # stock_list = [o[:9] for o in os.listdir()][20:100]
    # for s in stock_list:
    #     filedir = 'D:/大学/量化投资/数据/OldData/{}_NormalData.csv'.format(s)
    #     feed = bt.feeds.PandasData(dataname = get_data_fromloc(filedir))
    #     cerebro.adddata(feed, name=s)

    #feed = bt.feeds.PandasData(dataname=get_data_fromts(code, start))
    # cerebro.plot(style="candlestick")