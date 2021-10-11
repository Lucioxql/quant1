# -*- coding: utf-8 -*-
# @Time : 2021/10/10 18:22
# @Author : Lucio
# @Site : 
# @File : grid_strategy.py
# @Software: PyCharm
import backtrader as bt
class grid_Strategy(bt.Strategy):
    '''
    继承并构建自己的网格策略
    '''
    print('参数设定')
    params = dict(
        # date_in=20,
        # date_add=10,
        data_out=20,
        break_price=0,  # 突破价格初始化
        base_position=0.3,  # ?????????
        buy_lower_limit=1-0.03,  # 网格下线 买入标准
        sell_upper_limit=1+0.05,  # 网格上线 卖出标准
        unit_sell=0.1,
        unit_buy=0.1,
        stoploss_bench=1-0.2)  # 止损线

    def log(self, txt, dt=None, doprint=True):
        """日志函数，输出统一的日志格式 """
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        print('只执行一次')
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

    def next(self):
        # 是否正在下单，如果是的话不能提交第二次订单
        if self.order:
            return
        cash = self.broker.get_cash()
        # 返回现在持有现金和市值
        value = self.broker.get_value()
        acc_avg_cost = self.getposition(self.datas[0]).price
        # 使用上一日收盘价计算
        current_price = self.dataclose[0]
        # 判断是否空仓 入市
        if len(self.getposition(self.datas[0])) <= 0:
            self.market_in(self.datas[0], current_price, value)
        # 非空仓，判断是否止损
        elif current_price <= acc_avg_cost*self.p.stoploss_bench and\
            (value-cash)/value >= 0.5:
            self.log('清仓条件：价格低于成本价，仓位高于50%，清仓线{}'.format(acc_avg_cost*self.p.stoploss_bench))
            self.close(data=self.datas[0])
        else:
            # self.log('成本价:{}'.format(acc_avg_cost))
            # 仓位调整
            self.market_add(self.datas[0], current_price, acc_avg_cost, value, cash)
            self.market_sub(self.datas[0], current_price, acc_avg_cost, value, cash)

    # 入市
    def market_in(self, security, current_price,value):
        # cash = self.broker.get_cash()
        # 返回现在持有现金和市值
        # value = self.broker.get_value()
        cost_order = value * self.p.base_position
        # 买多少手
        unit_order = int(cost_order / current_price / 100) * 100
        self.order = self.buy(data=security,size=unit_order)

    def market_add(self, security, current_price, acc_avg_cost, value, cash):
        # cash = self.broker.get_cash()
        # 返回现在持有现金和市值
        # value = self.broker.get_value()
        # 突破加仓线
        break_price_add = acc_avg_cost * self.p.buy_lower_limit
        # 购买总价值10%的股票
        cost_order = value * self.p.unit_buy
        if cost_order > cash:
            cost_order = cash
        # 买多少手
        unit_order = int(cost_order / current_price / 100) * 100
        # 判断是否执行
        if current_price <= break_price_add:
            # self.log('加仓线：{},买入{}股{},花费{}'.format(break_price_add,
            # unit_order, security._name, current_price * unit_order))
            self.order = self.buy(data=security, size=unit_order)

    def market_sub(self, security, current_price, acc_avg_cost, value, cash):
        # cash = self.broker.get_cash()
        # 返回现在持有现金和市值
        # value = self.broker.get_value()
        # 突破减仓线
        break_price_sell = acc_avg_cost * self.p.sell_upper_limit
        # 减仓金额（为什么根据账户价值算？）
        cost_order = value * self.p.unit_sell
        if cost_order >= (value-cash):
            cost_order = value - cash
        # 减仓手
        unit_order = int(cost_order / current_price / 100) * 100

        if current_price > break_price_sell or current_price <= acc_avg_cost * 0.8:
            # 记录这次卖出
            # self.log('减仓线：{},卖出{}股{},获得{}'.format(break_price_sell, unit_order,
            # security._name, current_price * unit_order))
            self.order = self.sell(data=security,size=unit_order)

    def notify_order(self, order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '买入:价格:{:.2f},成本:{:.2f},手续费:{:.2f}'.format(order.executed.price, order.executed.value, order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('卖出:价格{:.2f},成本:{:.2f},手续费{:.2f}'.format(order.executed.price, order.executed.value, order.executed.comm))
            self.bar_executed = len(self)

            # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')
        self.order = None

        # 记录交易收益情况（可省略，默认不输出结果）

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('策略收益：毛收益 {}, 净收益 {}'.format(trade.pnl, trade.pnlcomm))
