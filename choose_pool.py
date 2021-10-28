# -*- coding: utf-8 -*-
# @Time : 2021/10/10 14:00
# @Author : Lucio
# @Site : 
# @File : choose_pool.py
# @Software: PyCharm
# 导入包
import pandas as pd
import numpy as np
import os
import datetime


# 获取股票数据（2018-now）-> dict

# 计算财务数据指标 -> dict(code df(2019-now)）
def get_stockset(dir,start,end1,end2):
    """
    计算2018 1.4 - 8.31 盈利水平
    计算2018 9.31 - 12.31 亏损水平
    起始日期，截至日期
    """
    stockset = dict()
    stockset['code'] = []
    stockset['ret1'] = []
    stockset['ret2'] = []
    # 更换目录
    os.chdir(dir)
    totalset = os.listdir()
    # 输出所有本地股票收益率及回撤
    for s in totalset:
        try:
            # 计算 1-8月份收益
            temp = pd.read_csv(s)
            temp.index = pd.to_datetime(temp['trade_date'].astype(str))
            temp1 = temp[temp.index > start]
            first1 = temp1[temp1.index < end1].resample('M').first().close[0]
            last1 = temp1[temp1.index < end1].resample('M').last().close[-1]
            ret1 = (last1 - first1)/first1
            # 计算9-12月收益
            temp2 = temp[temp.index > end1]
            temp2 = temp2[temp2.index < end2]
            first2 = temp2.resample('M').first().close[0]
            last2 = temp2.resample('M').last().close[-1]
            ret2 = (last2 - first2)/first2
            if ret1 > 0.2 and ret2 < -0.3:
                stockset['code'].append(s[:9])
                stockset['ret1'].append(ret1)
                stockset['ret2'].append(ret2)
        except Exception as e:
            print(e)
    return stockset


def run_pool(dir):
    start = datetime.datetime(2018, 1, 1)
    end1 = datetime.datetime(2018, 8, 31)
    end2 = datetime.datetime(2018, 12, 31)
    stock = get_stockset(dir, start, end1, end2)
    test = pd.DataFrame(stock)
    last = test.sort_values(by=['ret1'], ascending=False).code
    return last
#
