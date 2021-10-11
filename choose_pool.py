# -*- coding: utf-8 -*-
# @Time : 2021/10/10 14:00
# @Author : Lucio
# @Site : 
# @File : choose_pool.py
# @Software: PyCharm
import tushare as ts
pro = ts.pro_api()
def get_code_list(date='20150202'):
    #创造股票池
    #默认2010年开始回测
    dd=pro.daily_basic(trade_date=date)
    x1=dd.close<100
    #流通市值低于300亿大于50亿
    x2=dd.circ_mv>500000
    x3=dd.circ_mv<3000000
    #市盈率低于80
    x4=dd.pe_ttm<80
    #股息率大于2%
    x5=dd.dv_ttm>3
    x=x1&x2&x3&x4&x5
    stock_list=dd[x].ts_code.values
    return stock_list