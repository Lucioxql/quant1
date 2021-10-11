# -*- coding: utf-8 -*-
# @Time : 2021/10/10 13:58
# @Author : Lucio
# @Site :
# @File : sample_strategy.py
# @Software: PyCharm

from data_feed import *
from stra.sample_strategy import *
from stra.test1zhihu import *
from stra.grid_strategy import *
import backtrader as bt
#import numpy as np
import os.path


if __name__ == '__main__':
    code = '000001.SZ'    # 单股票
    start = '20150101'
    # 具象化实例
    cerebro = bt.Cerebro()
    # 手续费万五
    cerebro.broker.setcommission(0.005)
    feed = bt.feeds.PandasData(dataname=get_data_fromts(code, start))
    cerebro.adddata(feed, name=code)
    cerebro.broker.setcash(100000.0)
    # 获取账户价值
    print('开始账户价值：{}'.format(cerebro.broker.getvalue()))
    cerebro.addstrategy(grid_Strategy)
    cerebro.run()
    cerebro.plot(style="candlestick")  # 绘图
    print('结束账户价值: {}'.format(cerebro.broker.getvalue()))

    # 未复权 复权需要重新下载
    # multiply stock
    # os.chdir('D:/大学/量化投资/数据/OldData')
    # stock_list = [o[:9] for o in os.listdir()][20:100]
    # for s in stock_list:
    #     filedir = 'D:/大学/量化投资/数据/OldData/{}_NormalData.csv'.format(s)
    #     feed = bt.feeds.PandasData(dataname = get_data_fromloc(filedir))
    #     cerebro.adddata(feed, name=s)