# -*- coding: utf-8 -*-
#! python3
#Date: 2017-04-27

from FetchPortfolio import request, GetHeader
import re

def GetStock(Symbol):
    postUrl = 'https://xueqiu.com/P/'
    Header = GetHeader()
    try:
        resp, cont = request(postUrl + Symbol, header=Header)
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except:
        raise Exception('无法获取组合信息！')

    c = re.compile('<span class="stock-name"><div class="name">(.+?)</div><div class="price">(.+?)</div></span>')
    data = c.findall(cont.decode('utf-8'))
    return data

if __name__ == '__main__':
    print('For Test')
