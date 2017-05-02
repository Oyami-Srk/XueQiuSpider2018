# -*- coding: utf-8 -*-
#! python3
#Date: 2017-04-27

from FetchPortfolio import request, GetHeader
import re

def GetPortfolioFromPage(url):
    Header = GetHeader()
    try:
        resp, cont = request(url, header=Header)
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except:
        raise Exception('无法获取组合信息！')

    c = re.compile('(<!-- 文章标题-->.*<!-- pdf-->)')
    page = c.findall(cont.decode('utf-8'))[0]
    c = re.compile('(ZH\d{6,7})')
    ori = c.findall(page)
    List = []
    for symbol in ori:
        if symbol not in List:
            List.append(symbol)
    return List


if __name__ == '__main__':
    print('For Test')
    