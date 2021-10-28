# -*- coding: utf-8 -*-
# @Time : 2021/10/28 16:05
# @Author : Lucio
# @Site : 
# @File : choose_finance.py
# @Software: PyCharm

import pandas as pd
import time
import tqdm
import numpy as np
import os
import tushare as ts

pro = ts.pro_api()
total = pd.read_excel('D:/大学/Jupyter/A研一/量化金融/total.xls')
a = total.groupby('code').mean()[['roeAvg', 'npMargin', 'epsTTM']]
a = a.apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
a['score'] = a['roeAvg'] + a['npMargin'] + a['epsTTM']
last = a.sort_values(by='score', ascending=False)[:int(len(a)*0.2)]
last_list = last.index
code_list = [s[3:]+s[2]+s[:2] for s in last_list]
startdate = '20160501'
enddate = '20211028'
save_path = 'F:\Quant\数据\量化金融'

def getnormaldata(list,startdate,enddate):
    for i in list:
        path = os.path.join(save_path, i+'_NormalData.csv')
        df = pro.daily(ts_code=i,
                       start_date=startdate,
                       end_date=enddate,
                       fields='ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount')
        df = df.sort_values('trade_date', ascending=True).reset_index(drop=True)
        df.to_csv(path, index=False,encoding='utf-8_sig')

getnormaldata(code_list,startdate,enddate)
