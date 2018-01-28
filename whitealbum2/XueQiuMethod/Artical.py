import re
import json


def GetPortfolioFromPage(XueQiu, url):
    cont = XueQiu.Fetch(url, failed_msg='无法获取页面信息')
    c = re.compile('(<!-- 文章标题-->.*<!-- pdf-->)')
    page = c.findall(cont)[0]
    c = re.compile('(ZH\d{6,7})')
    ori = c.findall(page)
    List = []
    for symbol in ori:
        if symbol not in List:
            List.append(symbol)
    return List


def GetPagesUrl(XueQiu, regx=''):
    base = 'https://xueqiu.com/v4/statuses/user_timeline.json?'
    base = base + 'user_id=5171159182&page='

    if regx == '':
        regx = '最受关注 & 优质组合调仓路线'
    c = re.compile(regx)
    Data = json.loads(XueQiu.Fetch(base + '0', failed_msg='无法获取用户帖子信息'))
    maxPage = Data['maxPage']
    List = []

    for i in range(0, maxPage + 1):
        cont = XueQiu.Fetch(base + str(i), failed_msg='无法获取用户帖子信息')
        try:
            Data = json.loads(cont)
            for post in Data['statuses']:
                if len(c.findall(post['title'])) != 0:
                    print(post['title'] + ':' + post['target'])
                    List.append('https://xueqiu.com' + post['target'])
        except Exception as e:
            if not XueQiu.Except(str(e), e):
                break
    return List
