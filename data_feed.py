# -*- coding: utf-8 -*-
# @Time : 2021/10/10 13:58
# @Author : Lucio
# @Site :
# @File : sample_strategy.py
# @Software: PyCharm
import tushare as ts
import pandas as pd

pro = ts.pro_api()
def get_data_fromloc(filedir):
    # 未复权 复权需要重新下载pro_bar
    # 读取数据库 未复权
    data = pd.read_csv(filedir)
    data.index = pd.to_datetime(data.trade_date.astype(str))
    data = data.sort_index()
    data['volume'] = data.vol
    data['openinterest'] = 0
    data['datetime'] = pd.to_datetime(data.trade_date)
    data = data[['datetime', 'open', 'high', 'low', 'close', 'volume', 'openinterest']]
    data = data.fillna(0)
    return data

#直接下载
def get_data_fromts(code,date='20150101'):
    '''
    :param code: 下载股票代码
    :param date: 下载开始日期到今天
    :return:
    '''
    data=ts.pro_bar(ts_code=code, adj='qfq', start_date=date)
    data.index=pd.to_datetime(data.trade_date)
    data=data.sort_index()
    data['volume']=data.vol
    data['openinterest']=0
    data['datetime']=pd.to_datetime(data.trade_date)
    data=data[['datetime','open','high','low','close','volume','openinterest']]
    data=data.fillna(0)
    return data

#导入本地的
# data = bt.feeds.GenericCSVData(
#         dataname=filedir,
#         datetime=1,
#         open=2,
#         high=3,
#         low=4,
#         close=5,
#         volume=9,
#         dtformat=('%Y%m%d'),
#         fromdate=datetime(1998, 10, 22),
#         todate=datetime(2021, 9, 30))

#################################3
#直接从tushare获取
# pro=ts.pro_api()
# def get_data2(code,date='20150101'):
#     data=ts.pro_bar(ts_code=code, adj='qfq', start_date=date)
#     data.index=pd.to_datetime(data.trade_date)
#     data=data.sort_index()
#     data['volume']=data.vol
#     data['openinterest']=0
#     data['datetime']=pd.to_datetime(data.trade_date)
#     data=data[['datetime','open','high','low','close','volume','openinterest']]
#     data=data.fillna(0)
#     return data


##########################################33
#读取数据库 未复权 时间待处理
#     filedir = 'D:/大学/量化投资/数据/OldData/000001.SZ_NormalData.csv'
#     data = pd.read_csv(filedir)
#     data.index = pd.to_datetime(data.trade_date)
#     data = data.sort_index()
#     data['volume'] = data.vol
#     data['openinterest'] = 0
#     data['datetime'] = pd.to_datetime(data.trade_date)
#     data = data[['datetime', 'open', 'high', 'low', 'close', 'volume', 'openinterest']]
#     data = data.fillna(0)