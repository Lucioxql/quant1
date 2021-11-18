from mongofeedcb import MongoData
import datetime
import pymongo
import backtrader as bt
from cb_grid import cbGridStrategy
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo

if __name__=='__main__':
    db = 'longcband'
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    code_list = client[db].collection_names()
    # 具象化实例
    cerebro = bt.Cerebro()
    # 手续费千1
    cerebro.broker.setcommission(commission=0.001)
    for code in code_list[:]:
        try:
            feed = MongoData(
                db=db,
                dataname=code,
                fromdate=datetime.datetime(2019, 1, 1),
                todate=datetime.datetime(2021, 11, 17),
            )
            cerebro.adddata(feed, name=code)
        except:
            continue

    cerebro.broker.setcash(1000000.0)
    # 获取账户价值
    print('开始账户价值：{}'.format(cerebro.broker.getvalue()))
    # 计算最优参数 b
    # strats = cerebro.optstrategy(cbGridStrategy, period=range(5, 65, 5), )
    cerebro.addstrategy(cbGridStrategy, poneplot=True)
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