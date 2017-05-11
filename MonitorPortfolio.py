# -*- coding: utf-8 -*-

from FetchPortfolio import request, GetHeader
import re, json
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import datetime as dt

header_login = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Cookie':'balabala'
}

postUrl = 'https://xueqiu.com/P/'
Header = GetHeader()
try:
    resp, cont = request(postUrl + Symbol, header = Header)
except KeyboardInterrupt:
    print('User Interrupt!')
except:
    raise Exception('无法获取组合信息！')
# 获取现金比例
# c = re.compile('"segment-weight weight">\S{5,}</span></div></div><div class="history-list">')
# c = re.compile('\S{5,}</span></div></div><div class="history-list">')
c = re.compile('"name":"现金","weight":\S{3,},')
cash_ratio = c.findall(cont.decode('utf-8'))
if cash_ratio == []:
    cash_ratio = 0
else:
    # c = re.compile('\d{1,}\.\d{2}')
    # cash_ratio = float(c.findall(cash_ratio[0])[0]) / 100
    # cash_ratio = float(cash_ratio[0].split('>')[1].split('%')[0]) / 100
    cash_ratio = float(cash_ratio[0].split(',')[1].split(':')[1]) / 100
# 详细仓位
c = re.compile('cubeTreeData = {\S{1,}}')
pos = c.findall(cont.decode('utf-8'))[0]
pos = pos.split(' ')[2].replace('false', '"false"')
pos = eval(pos)
position = {'CNY': {'证券代码': 'CNY', '证券简称': '现金', '权重': cash_ratio, '雪球分类': np.nan}}
for Symbol in pos.keys():
    for s in pos[Symbol]['stocks']:
        secid = s['stock_symbol'][2:] + '.' + s['stock_symbol'][:2]
        position[secid] = {'证券代码': secid,
                            '证券简称': s['stock_name'],
                            '权重': float('%.6f' % (s['weight'] / 100)),
                            '分类': s['segment_name']}
position = DataFrame(position, index=['证券代码', '证券简称', '权重', '雪球分类']).T


# 调仓历史记录
url_hist = 'https://xueqiu.com/cubes/rebalancing/history.json?cube_symbol='
resp, cont = request(url_hist + 'ZH542513' + '&count=50&page=1', header = header_login)
data = json.loads(cont.decode('utf-8'))
stockdata = data['list']
for i in range(len(stockdata)):
    print('股票名称', end = '：')
    print(stockdata[i]['rebalancing_histories'][0]['stock_name'], end = '  持仓变化  ')
    print(float('%.6f' % (stockdata[i]['rebalancing_histories'][0]['prev_weight_adjusted'] / 100)), end = ' --> ')
    print(float('%.6f' % (stockdata[i]['rebalancing_histories'][0]['target_weight'] / 100)))
