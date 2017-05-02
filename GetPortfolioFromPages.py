# -*- coding: utf-8 -*-
#! python3
#Date: 2017-04-27

from FetchPortfolio import request, GetHeader
import re, json

def GetPortfolioFromPage(url):
    Header = GetHeader()
    try:
        resp, cont = request(url, header=Header)
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except:
        raise Exception('无法获取页面信息！')

    c = re.compile('(<!-- 文章标题-->.*<!-- pdf-->)')
    page = c.findall(cont.decode('utf-8'))[0]
    c = re.compile('(ZH\d{6,7})')
    ori = c.findall(page)
    List = []
    for symbol in ori:
        if symbol not in List:
            List.append(symbol)
    return List

# 返回一个储存用户的所有帖子中所有匹配regx的地址, 可直接用于GetPortfolioFromPage
def GetPagesUrl(regx = ''):
    base = 'https://xueqiu.com/v4/statuses/user_timeline.json?user_id=5171159182&page='
    if regx == '':
        regx = '最受关注 & 优质组合调仓路线'

    c = re.compile(regx)

    Header = GetHeader()
    try:
        resp, cont = request(base + '0', header = Header)
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except:
        raise Exception('无法获取用户帖子信息！')

    Data = json.loads(cont)
    max = Data['maxPage']
    List = []

    for i in range(0, max + 1):
        try:
            resp, cont = request(base + str(i), header=Header)
        except KeyboardInterrupt:
            print('\nUser Interrupt!\n')
            break
        except:
            raise Exception('无法获取用户帖子信息！')

        try:
            Data = json.loads(cont)
            for post in Data['statuses']:
                if len(c.findall(post['title'])) != 0:
                    print(post['title'] + ':' + post['target'])
                    List.append('https://xueqiu.com' + post['target'])
        except KeyboardInterrupt:
            print('\nUser Interrupt!\n')
            break

    return List


if __name__ == '__main__':
    print('For Test')
