# -*- coding: utf-8 -*-
#! python3

import time, json, re
from base import *
import numpy as np
from pandas import Series, DataFrame

# e.g. https://xueqiu.com/cubes/nav_daily/all.json?cube_symbol=ZH958027
def GetRateChart(Symbol):
    postUrl = 'https://xueqiu.com/cubes/nav_daily/all.json?' + 'cube_symbol=' + Symbol + '&until=' + str(int(time.time()) * 1000)
    return json.loads(FetchPage(postUrl, failed_msg = '无法获取组合信息'))[0]

## Param "market": 选择市场, cn为沪深, us为美股, hk为港股
## Param "profit": 收益排序类型, 分为monthly_gain/daily_gain/annualized_gain_rate
## Param "sort": 收益排序方法, 分为 best_benefit/grow_fast/win_market
## Param "sale_flag": 是否包创业板, 0为包括, 1为不包括
## Param "stock_positions": 是否过滤单只股票组合, 1为过滤, 0为不过滤

# e.g. https://xueqiu.com/cubes/discover/rank/cube/list.json
# ?market=cn&sale_flag=0&stock_positions=0&sort=best_benefit&category=12&profit=monthly_gain
def GetMarketList(market = 'cn',
                  profit = 'monthly_gain',
                  sort = 'best_benefit',
                  sale_flag = '0',
                  stock_positions = '0'):
    baseUrl = 'https://xueqiu.com/cubes/discover/rank/cube/list.json' \
              '?market=%s&sale_flag=%s&stock_positions=%s&sort=%s&category=12&profit=%s'
    postUrl = baseUrl %(market, sale_flag, stock_positions, sort, profit) + '&count=%d'
    TotalCount = 0
    # Get TotlCount
    TotalCount = json.loads(FetchPage(postUrl % 1))['totalCount']
    List = []
    cont = FetchPage(postUrl % TotalCount)
    for item in json.loads(cont)['list']:
        List.append(item['symbol']) 
    return List

# 返回通过All.json得到的一些信息
# def __GetMarketListInfoViaMarketListsOriginDataWrittenInJsonAndReturnADataframeIndexedBySymbolWith6Columns__\
def GetMarketList(market = 'cn',
                  profit = 'monthly_gain',
                  sort = 'best_benefit',
                  sale_flag = '0',
                  stock_positions = '0'):
    baseUrl = 'https://xueqiu.com/cubes/discover/rank/cube/list.json?' \
              'market=%s&sale_flag=%s&stock_positions=%s&sort=%s&category=12&profit=%s'
    postUrl = baseUrl %(market, sale_flag, stock_positions, sort, profit) + '&count=%d'
    TotalCount = 0
    # Get TotlCount
    TotalCount = json.loads(cont = FetchPage(postUrl % 1))['totalCount']
    cont = FetchPage(postUrl % TotalCount)
    Symbol_list = []
    DailyGain_list = []
    MonthlyGain_list = []
    TotalGain_list = []
    NetValue_list = []
    AnnualizedGainRate_list = []
    BBRate_list = []
    for item in json.loads(cont)['list']:
        Symbol_list.append(item['symbol'])
        DailyGain_list.append(item['daily_gain'])
        MonthlyGain_list.append(item['monthly_gain'])
        TotalGain_list.append(item['total_gain'])
        NetValue_list.append(item['net_value'])
        AnnualizedGainRate_list.append(item['annualized_gain_rate'])
        BBRate_list.append(item['bb_rate'])
    return DataFrame({'daily_gain': DailyGain_list,
                      'monthly_gain': MonthlyGain_list,
                      'total_gain': TotalGain_list,
                      'net_value': NetValue_list,
                      'annualized_gain_rate': AnnualizedGainRate_list,
                      'bb_rate': BBRate_list},
                     index = Symbol_list)

# 返回在市场上获取的组合的信息（All.json获取+Market无关的获取）
def GetMarketListInfo(market = 'cn',
                      profit = 'monthly_gain',
                      sort = 'best_benefit',
                      sale_flag = '0',
                      stock_positions = '0'):
    oridata = GetMarketList(market, profit, sort, sale_flag, stock_positions)
    baseUrl = 'https://xueqiu.com/cubes/analyst/histo/stat.json?cube_symbol=%s&type=%s'
    turnover_3m_list = []
    turnover_12m_list = []
    liquidity_3m_list = []
    liquidity_12m_list = []
    for i in list(oridata.index):
        postUrl = baseUrl % (i, 'turnover')
        try:
            cont = FetchPage(postUrl)
        except KeyboardInterrupt:
            print('\nUser Interrupt!\n')
            break
        rj = json.loads(cont)
        turnover_3m_list.append(rj['values'][0]['value'])
        if len(rj['values']) < 5:
            turnover_12m_list.append(np.nan)    # For Unknown reason, some of these may not have regular data
        else:
            turnover_12m_list.append(rj['values'][2]['value'])

        postUrl = baseUrl % (i, 'liquidity')
        try:
            cont = FetchPage(postUrl)
        except KeyboardInterrupt:
            print('\nUser Interrupt!\n')
            break
        rj = json.loads(cont)
        liquidity_3m_list.append(rj['values'][0]['value'])
        if len(rj['values']) < 5:
            liquidity_12m_list.append(np.nan)
        else:
            liquidity_12m_list.append(rj['values'][2]['value'])
    oridata['turnover_3m'] = turnover_3m_list
    oridata['turnover_12m'] = turnover_12m_list
    oridata['liquidity_3m'] = liquidity_3m_list
    oridata['liquidity_12m'] = liquidity_12m_list
    return oridata

# 获取组合所在的市场分类
def GetPortfolioMarket(Symbol):
    postUrl = 'https://xueqiu.com/cubes/nav_daily/all.json?'
    cont = FetchPage(postUrl + 'cube_symbol=' + Symbol + '&until=' + str(int(time.time()) * 1000), failed_msg = '无法获取组合信息')
    try:
        Data = json.loads(cont)[1]
    except:
        return 'no_portfolio'
    # 利用走势图的基准来判断市场类型
    if Data['symbol'] == 'SH000300':
        return 'cn'
    elif Data['symbol'] == 'HKHSI':
        return 'hk'
    elif Data['symbol'] == 'SP500':
        return 'us'
    return 'undefined'

# 检查组合是否被关停
def CheckPortfolioClosed(Symbol):
    if str(FetchPage('https://xueqiu.com/P/'+ Symbol, failed_msg = '无法获取组合信息')).find('https://assets.imedao.com/images/cube-closed.png') >= 0:
        return True
    return False

# 检查是否访问频繁
def CheckifCaptcha():
    c = re.compile('系统检测到您的IP最近访问过于频繁')
    if len(c.findall(FetchPage('https://xueqiu.com/', failed_msg = '无法访问'))) > 0:
        return True
    return False

# 返回一个字典
def GetPortfolioInfo(Symbol):
    postUrl = 'https://xueqiu.com/P/'
    baseUrl = 'https://xueqiu.com/cubes/analyst/histo/stat.json?cube_symbol=%s&type=%s'
    cont = FetchPage(postUrl + Symbol, failed_msg = '无法获取组合信息')
    c = re.compile('(<div (style="border:0;padding-left:0" |)'
                   'class="cube-profit-day cube-profit">.+?</div>.+?</div>)')
    data = c.findall(cont)
    day_return = float(data[0][0].split('>')[4].split('%')[0]) / 100
    month_return = float(data[1][0].split('>')[4].split('%')[0]) / 100
    nav = float(data[2][0].split('>')[4].split('<')[0])  # 净值
    total_return = float(nav - 1)
    # 获取组合创建日
    # c = re.compile('\d{4}-\d{2}-\d{2}')
    # date = c.findall(cont)[1]
    c = re.compile('"created_date_format":"\d{4}-\d{2}-\d{2}')
    date = c.findall(cont)[0]
    date = date.split('"')[3]
    # 获取最新调仓时间
    c = re.compile('\d{4}\.\d{1,2}\.\d{1,2}\s\d{2}:\d{2}')
    LastUpdate = c.findall(cont)[0]
    # c = re.compile('\d{4}\.\d{1,2}\.\d{1,2}')
    # LastUpdate = c.findall(LastUpdate)[0]
    LastUpdate = LastUpdate.split(' ')[0]
    # 获取组合名称
    c = re.compile('"name":"\S{2,}","symbol"')
    name = c.findall(cont)[0]
    name = name.split(',')[0].split(':')[1].split('"')[1]
    # 获取现金比例
    # c = re.compile('"segment-weight weight">\S{5,}</span></div></div><div class="history-list">')
    # c = re.compile('\S{5,}</span></div></div><div class="history-list">')
    c = re.compile('"name":"现金","weight":\S{3,},')
    cash_ratio = c.findall(cont)
    if cash_ratio == []:
        cash_ratio = 0
    else:
        # c = re.compile('\d{1,}\.\d{2}')
        # cash_ratio = float(c.findall(cash_ratio[0])[0]) / 100
        # cash_ratio = float(cash_ratio[0].split('>')[1].split('%')[0]) / 100
        cash_ratio = float(cash_ratio[0].split(',')[1].split(':')[1]) / 100
    # # 详细仓位
    # c = re.compile('cubeTreeData = {\S{1,}}')
    # pos = c.findall(cont)[0]
    # pos = pos.split(' ')[2].replace('false', '"false"')
    # pos = eval(pos)
    # # position = DataFrame(['CNY', '现金', cash_ratio, np.nan],
    # #                      index=['stock_symbol', 'stock_name', 'weight', 'segment_name']).T
    # # for Symbol in pos.keys():
    # #     segment = DataFrame(pos[Symbol]['stocks'])[['stock_symbol', 'stock_name', 'weight', 'segment_name']]
    # #     position = pd.concat([position, segment])
    # position = {'CNY': {'证券代码': 'CNY', '证券简称': '现金', '权重': cash_ratio, '雪球分类': np.nan}}
    # for Symbol in pos.keys():
    #     for s in pos[Symbol]['stocks']:
    # #        secid = s['stock_symbol'][2:] + '.' + s['stock_symbol'][:2]
    #         position[secid] = {'证券代码': s['stock_symbol'],
    # #                           '证券代码': secid,
    #                            '证券简称': s['stock_name'],
    #                            '权重': float('%.6f' % (s['weight'] / 100)),
    #                            '分类': s['segment_name']}
    # position = DataFrame(position, index=['证券代码', '证券简称', '权重', '雪球分类']).T
    try:
        postUrl = baseUrl % (Symbol, 'turnover')
        cont = FetchPage(postUrl)
        rj = json.loads(cont)
        turnover_3m = rj['values'][0]['value']
        if len(rj['values']) < 5:
            turnover_12m = np.nan  # For Unknown reason, some of these may not have regular data
        else:
            turnover_12m = rj['values'][2]['value']

        postUrl = baseUrl % (Symbol, 'liquidity')
        cont = FetchPage(postUrl)
        rj = json.loads(cont)
        liquidity_3m = rj['values'][0]['value']
        if len(rj['values']) < 5:
            liquidity_12m  = np.nan
        else:
            liquidity_12m = rj['values'][2]['value']
    except:
        turnover_3m = np.nan
        turnover_12m = np.nan
        liquidity_3m = np.nan
        liquidity_12m = np.nan

    return {'begin': date,
            'day_return': float('%.4f' % day_return),
            'month_return': float('%.4f' % month_return),
            'nav': nav,
            'total_return': float('%.4f' % total_return),
            'market': GetPortfolioMarket(Symbol),
            'closed': CheckPortfolioClosed(Symbol),
            'turnover_3m': turnover_3m,
            'turnover_12m': turnover_12m,
            'liquidity_3m': liquidity_3m,
            'liquidity_12m': liquidity_12m,
            'LastUpdate': LastUpdate,
            'name': name,
            'cash_ratio': cash_ratio,
            }

def GetPortfolioDetails(Symbol):
    postUrl = 'https://xueqiu.com/P/'
    data = FetchPage(postUrl, failed_msg = 'u无法获取组合信息')

    c = re.compile('SNB.cubeInfo = (\{.*\})')
    PortfolioInfo_Json = c.findall(data)[0]
    c = re.compile('SNB.cubeTreeData = (\{.*\})')
    PortfolioStocks_Json = c.findall(data)[0]
    c = re.compile('SNB.cubePieData = (\[.*\])')
    PortfolioPie_Json = c.findall(data)[0]

    Obj_Info = json.loads(PortfolioInfo_Json)
    Obj_Stock = json.loads(PortfolioStocks_Json)
    Obj_Pie = json.loads(PortfolioPie_Json)

    cash_ratio = np.nan

    for item in Obj_Pie:
        if item['name'] == '现金':
            cash_ratio = item['weight']

    Stocks_List = []
    for item in Obj_Stock:
        for stocks in Obj_Stock[item]['stocks']:
            Stocks_List.append({'Symbol': stocks['stock_symbol'],
                                # 'Symbol': secid,
                                'Name': stocks['stock_name'],
                                'Weight': float('%.6f' % (stocks['weight'] / 100)),
                                'Segment': stocks['segment_name']})

    if Obj_Info['close_date'] == '':
        endtime = np.nan
    else:
        endtime = time.strftime('%Y-%m-%d', time.localtime(Obj_Info['close_date'] / 1000))

    Info = {
        'Symbol': Obj_Info['symbol'],
        'Name': Obj_Info['name'],
        'Market': Obj_Info['market'],
        'begin': time.strftime('%Y-%m-%d', time.localtime(Obj_Info['created_at'] / 1000)),
        'update': time.strftime('%Y-%m-%d', time.localtime(Obj_Info['sell_rebalancing']['updated_at'] / 1000)),
        # 'end': np.nan if Obj_Info['close_date'] == ''
        # else time.strftime('%Y-%m-%d', time.localtime(Obj_Info['close_date'] / 1000)),
        'end': endtime,
        'gain':{
            'daily': Obj_Info['daily_gain'],
            'monthly': Obj_Info['monthly_gain'],
            'total': Obj_Info['total_gain']
        },
        'nav': Obj_Info['net_value'],
        'annualized_gain_rate': Obj_Info['annualized_gain_rate'],
        'bb_rate': Obj_Info['bb_rate'],
        'Stocks': Stocks_List,
        'cash_ratio': cash_ratio
    }
    return Info

def GetPortfolioHistories(Symbol):
    cont = FetchPage('https://xueqiu.com/cubes/rebalancing/history.json?count=50&page=%d&cube_symbol=%s' % (1, Symbol), True)
    data = json.loads(cont)
    DataList = data['list']
    totalCount = data['totalCount']
    PageCount = 1
    for i in range(50, totalCount, 50):
        PageCount = PageCount + 1
        cont = FetchPage('https://xueqiu.com/cubes/rebalancing/history.json?count=50&page=%d&cube_symbol=%s' % (PageCount, Symbol), True)
        data = json.loads(cont)
        DataList.extend(data['list'])

    Histories = []
    for item in DataList:
        # 这里加一个判断item['status'] == 'success'可以剔除已取消的调仓
        # 这里通过item['category']可以判断是系统自动分红送配(sys_rebalancing)还是用户自己调仓(user_rebalancing)
        # 通过item['created_at']可以获知调仓创建日期
        # 而item['updated_at']里面则是调仓执行日期(可能因为不是交易日而延迟？) 改值为Unix时间戳(ms)
        # 遍历rebalancing_histories以获得调仓
        if item['status'] == 'canceled' or item['status'] == 'failed' or item['status'] == 'pending':
            continue

        for i in item['rebalancing_histories']:
            if i['prev_weight_adjusted'] == None:
                i['prev_weight_adjusted'] = 0
            if i['target_weight'] == None:
                i['target_weight'] = 0

            Histories.append(
                {
                    'Name': i['stock_name'],
                    'Symbol': i['stock_symbol'],
                    # 'Symbol': secid,
                    'Prev': i['prev_weight_adjusted'],
                    'Target': i['target_weight'],
                    'Date': i['updated_at'],
                    'Category': item['category'],
                    'Price': i['price']
                }
            )

    return Histories


# Artical Part

def GetPortfolioFromPage(url):
    cont = FetchPage(url, failed_msg = '无法获取页面信息')
    c = re.compile('(<!-- 文章标题-->.*<!-- pdf-->)')
    page = c.findall(cont)[0]
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
    Data = json.loads(FetchPage(base + '0', failed_msg = '无法获取用户帖子信息'))
    maxPage = Data['maxPage']
    List = []

    for i in range(0, maxPage + 1):
        cont = FetchPage(base + str(i), failed_msg = '无法获取用户帖子信息')
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

