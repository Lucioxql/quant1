# -*- coding: utf-8 -*-
# @Time : 2021/10/20 21:53
# @Author : Lucio
# @Site : 
# @File : new_grid2.py
# @Software: PyCharm
import backtrader as bt
from pandas import DataFrame
class multiGridStrategy(bt.Strategy):
    """
    继承并构建新的网格策略
    """
    # print('参数设定')
    params = dict(
        poneplot=False,  # 是否打印到同一张图
        # 突破价格初始化
        base_position=0.5,
        buy_lower_limit=1 - 0.03,  # 网格标准下线 买入标准
        sell_upper_limit=1 + 0.05,  # 网格标准上线 卖出标准
        # 可以利用凯利公式调整下仓仓位
        unit_sell=0.1,
        unit_buy=0.1,
        stoploss_bench=1 - 0.2,
        period=60,
        printlog=False)


    def log(self, txt, dt=None, doprint=True):
        """日志函数，输出统一的日志格式 """
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.inds = dict()
        self.date = dict()
        self.order_list = []
        self.trader_list = []
        for i, d in enumerate(self.datas):
            d.plotinfo.plot = False
            self.inds[d] = dict()
            self.inds[d]['sml'] = bt.ind.SMA(d.close, period=self.p.period)
            self.date[d._name] = -1
        self.n = int(len(self.datas)*0.2)
        self.order = None
        self.c = 20
        self.check = []

    def get_check(self):
        # 股票池选择
        tmp_d = dict()
        for i, d in enumerate(self.datas):
            # 计算六十日的股票跌值
            tmp_d[d._name] = (d.close[0]-d.close[1-self.p.period])/d.close[1-self.p.period]
        sort_list = sorted(tmp_d.items(), key=lambda x: x[1])
        down_list = sort_list[:int(len(sort_list)*0.2)]
        check_list = [c[0] for c in down_list]
        self.c = 0
        return check_list

    def next(self):
        if self.c == 20:
            self.check = self.get_check()
        for i, d in enumerate(self.datas):
            if d._name in self.check:
                cash = self.broker.get_cash()
                # 返回现在持有现金和市值
                value = self.broker.get_value()
                self.grid(d, value, cash)
            else:
                self.close(data=d, stock_code=d._name)
                self.date[d._name] = d.datetime.datetime(0)
        self.c += 1

    def grid(self, data, value, cash):
        # if self.order:
        #     return
        acc_avg_cost = self.getposition(data).price
        current_price = data.close[0]
        p_value = value / self.n
        # 判断是否入市
        if not self.getposition(data):
            self.market_in(data, current_price, p_value, cash)
        elif current_price <= acc_avg_cost * self.p.stoploss_bench and \
                (value - cash)/value >= 0.5:  # 总仓位是否超过50%，逻辑有点不通
            self.log('清仓条件：价格低于成本价，仓位高于50%，清仓线{}'.format(acc_avg_cost * self.p.stoploss_bench))
            if self.date[data._name] == -1 or (data.datetime.datetime(0) - self.date[data._name]).days >= 1:
                self.close(data=data, stock_code=data._name)
                self.date[data._name] = data.datetime.datetime(0)
        else:
            # self.log('成本价:{}'.format(acc_avg_cost))
            # 仓位调整
            self.market_add(data, current_price, acc_avg_cost, p_value, cash)
            self.market_sub(data, current_price, acc_avg_cost, p_value, cash)

    # 入市
    def market_in(self, security, current_price, p_value, cash):
        cost_order = p_value * self.p.base_position
        if cost_order > cash:
            cost_order = cash
        # 买多少手
        unit_order = int(cost_order / current_price / 100) * 100
        if self.date[security._name] == -1 or (security.datetime.datetime(0) - self.date[security._name]).days >= 1:
            self.order = self.buy(data=security, size=unit_order, stock_code=security._name)
            self.date[security._name] = security.datetime.datetime(0)
        else:
            return

    def market_add(self, security, current_price, acc_avg_cost, p_value, cash):
        # 突破加仓线
        break_price_add = acc_avg_cost * self.p.buy_lower_limit
        # 购买总价值10%的股票
        cost_order = p_value * self.p.unit_buy
        if cost_order > cash:
            cost_order = cash
        # 买多少手
        unit_order = int(cost_order / current_price / 100) * 100
        # 判断是否执行
        if self.date[security._name] == -1 or (security.datetime.datetime(0) - self.date[security._name]).days >= 1:
            if current_price <= break_price_add:
                # self.log('加仓线：{},买入{}股{},花费{}'.format(break_price_add,
                # unit_order, security._name, current_price * unit_order))
                self.order = self.buy(data=security, size=unit_order, stock_code=security._name)
                self.date[security._name] = security.datetime.datetime(0)
        else:
            return

    def market_sub(self, security, current_price, acc_avg_cost, p_value, cash):
        # 突破减仓线
        break_price_sell = acc_avg_cost * self.p.sell_upper_limit
        # 减仓金额（为什么根据账户价值算？）
        cost_order = p_value * self.p.unit_sell
        if self.date[security._name] == -1 or (security.datetime.datetime(0) - self.date[security._name]).days >= 1:
            if cost_order >= (self.getposition(security).size*current_price):
                self.log('清仓{}'.format(break_price_sell))
                self.close(data=security, stock_code=security._name)
                self.date[security._name] = security.datetime.datetime(0)
            else:
                # 减仓手
                unit_order = int(cost_order / current_price / 100) * 100
                if current_price > break_price_sell or current_price <= acc_avg_cost * 0.8:
                    # 记录这次卖出
                    # self.log('减仓线：{},卖出{}股{},获得{}'.format(break_price_sell, unit_order,
                    # security._name, current_price * unit_order))
                    self.order = self.sell(data=security, size=unit_order, stock_code=security._name)
                    self.date[security._name] = security.datetime.datetime(0)
        else:
            return
    def notify_order(self, order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '买入{}:价格:{:.2f},成本:{:.2f},手续费:{:.2f}'.format(order.info.stock_code, order.executed.price, order.executed.value,
                                                               order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.order_list.append(
                    [self.datas[0].datetime.date(0),
                     bt.num2date(self.datas[0].datetime[0]),
                     order.info.stock_code,
                     order.executed.price,
                     order.executed.value,
                     order.executed.comm,
                     'BUY'
                     ]
                )
            else:
                self.log('卖出{}:价格{:.2f},成本:{:.2f},手续费{:.2f}'.format(order.info.stock_code, order.executed.price, order.executed.value,
                                                                  order.executed.comm))
                self.order_list.append(
                    [self.datas[0].datetime.date(0),
                     bt.num2date(self.datas[0].datetime[0]),
                     order.info.stock_code,
                     order.executed.price,
                     order.executed.value,
                     order.executed.comm,
                     'SELL'
                     ])
            # len(self)表示第几个交易日
            self.bar_executed = len(self)

            # print(self.bar_executed)
            # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('{}交易失败'.format(order.info.stock_code))
        self.order = None

        # 记录交易收益情况（可省略，默认不输出结果）

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('策略收益：毛收益 {}, 净收益 {}'.format(trade.pnl, trade.pnlcomm))
        self.trader_list.append([
            self.datas[0].datetime.date(0),
            trade.pnl, trade.pnlcomm, self.broker.get_cash(),self.broker.get_value()]
        )

    def stop(self):
        # 策略停止后的输出
        self.log('MA Period: {0:8.2f}  Ending Value: {1:8.2f}'.format(
            self.params.period,
            self.broker.getvalue()),
            doprint=True)
        order_p = DataFrame(self.order_list,
                            columns=['datetime', 'time', 'code', 'price', 'value', 'comm', 'signal'])
        trader_p = DataFrame(self.trader_list, columns=['datetime', '毛收益', '净收益', '现金', '总市值'])
        order_p.to_csv('D:/大学/A研一/量化金融/system/history/order_history.csv',index=False)
        trader_p.to_csv('D:/大学/A研一/量化金融/system/history/trader_history.csv', index=False, encoding='utf_8_sig')