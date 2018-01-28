import time
import re
import json
import numpy as np


def GetPortfolioInfo(XueQiu, Symbol):
    postUrl = 'https://xueqiu.com/P/'
    baseUrl = 'https://xueqiu.com/cubes/analyst/histo/stat.json'
    baseUrl = baseUrl + '?cube_symbol=%s&type=%s'
    cont = XueQiu.Fetch(postUrl + Symbol, failed_msg='无法获取组合信息')
    c = re.compile('(<div (style="border:0;padding-left:0" |)'
                   'class="cube-profit-day '
                   'cube-profit">.+?</div>.+?</div>)')
    data = c.findall(cont)
    day_return = float(data[0][0].split('>')[4].split('%')[0]) / 100
    month_return = float(data[1][0].split('>')[4].split('%')[0]) / 100
    nav = float(data[2][0].split('>')[4].split('<')[0])  # 净值
    total_return = float(nav - 1)
    # 获取组合创建日
    c = re.compile('"created_date_format":"\d{4}-\d{2}-\d{2}')
    date = c.findall(cont)[0]
    date = date.split('"')[3]
    # 获取最新调仓时间
    c = re.compile('\d{4}\.\d{1,2}\.\d{1,2}\s\d{2}:\d{2}')
    LastUpdate = c.findall(cont)[0]
    LastUpdate = LastUpdate.split(' ')[0]
    # 获取组合名称
    c = re.compile('"name":"\S{2,}","symbol"')
    name = c.findall(cont)[0]
    name = name.split(',')[0].split(':')[1].split('"')[1]
    # 获取现金比例
    c = re.compile('"name":"现金","weight":\S{3,},')
    cash_ratio = c.findall(cont)
    if cash_ratio == []:
        cash_ratio = 0
    else:
        cash_ratio = float(cash_ratio[0].split(',')[1].split(':')[1]) / 100
    try:
        postUrl = baseUrl % (Symbol, 'turnover')
        cont = XueQiu.Fetch(postUrl)
        rj = json.loads(cont)
        turnover_3m = rj['values'][0]['value']
        if len(rj['values']) < 5:
            turnover_12m = np.nan
        else:
            turnover_12m = rj['values'][2]['value']

        postUrl = baseUrl % (Symbol, 'liquidity')
        cont = XueQiu.Fetch(postUrl)
        rj = json.loads(cont)
        liquidity_3m = rj['values'][0]['value']
        if len(rj['values']) < 5:
            liquidity_12m = np.nan
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
            'market': XueQiu.GetPortfolioMarket(Symbol),
            'closed': XueQiu.CheckPortfolioClosed(Symbol),
            'turnover_3m': turnover_3m,
            'turnover_12m': turnover_12m,
            'liquidity_3m': liquidity_3m,
            'liquidity_12m': liquidity_12m,
            'LastUpdate': LastUpdate,
            'name': name,
            'cash_ratio': cash_ratio}


def GetPortfolioDetails(XueQiu, Symbol):
    postUrl = 'https://xueqiu.com/P/'
    data = XueQiu.Fetch(postUrl + Symbol, failed_msg='u无法获取组合信息')

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
                                'Name': stocks['stock_name'],
                                'Weight': float('%.6f' %
                                                (stocks['weight'] / 100)),
                                'Segment': stocks['segment_name']})

    if Obj_Info['close_date'] == '':
        endtime = np.nan
    else:
        endtime = time.strftime('%Y-%m-%d', time.localtime(
            Obj_Info['close_date'] / 1000))

    Info = {
        'Symbol': Obj_Info['symbol'],
        'Name': Obj_Info['name'],
        'Market': Obj_Info['market'],
        'begin': time.strftime('%Y-%m-%d', time.localtime(
            Obj_Info['created_at'] / 1000)),
        'update': time.strftime('%Y-%m-%d', time.localtime(
            Obj_Info['sell_rebalancing']['updated_at'] / 1000)),
        'end': endtime,
        'gain': {
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


def GetPortfolioHistories(XueQiu, Symbol):
    url = 'https://xueqiu.com/cubes/rebalancing/history.json'
    url = url + '?count=50&page=%d&cube_symbol=%s'
    cont = XueQiu.Fetch(url % (1, Symbol))
    data = json.loads(cont)
    DataList = data['list']
    totalCount = data['totalCount']
    PageCount = 1
    for i in range(50, totalCount, 50):
        PageCount = PageCount + 1
        cont = XueQiu.Fetch(url % (PageCount, Symbol))
        data = json.loads(cont)
        DataList.extend(data['list'])

    Histories = []
    for item in DataList:
        if item['status'] == 'canceled' \
           or item['status'] == 'failed' \
           or item['status'] == 'pending':
            continue

        for i in item['rebalancing_histories']:
            if i['prev_weight_adjusted'] is None:
                i['prev_weight_adjusted'] = 0
            if i['target_weight'] is None:
                i['target_weight'] = 0

            Histories.append(
                {
                    'Name': i['stock_name'],
                    'Symbol': i['stock_symbol'],
                    'Prev': i['prev_weight_adjusted'],
                    'Target': i['target_weight'],
                    'Date': i['updated_at'],
                    'Category': item['category'],
                    'Price': i['price']
                }
            )
    return Histories


def GetRateChart(XueQiu, Symbol):
    postUrl = 'https://xueqiu.com/cubes/nav_daily/all.json?' + \
              'cube_symbol=' + Symbol + '&until=' + \
              str(int(time.time()) * 1000)
    return json.loads(XueQiu.Fetch(postUrl, failed_msg='无法获取组合信息'))


def CheckPortfolioClosed(XueQiu, Symbol):
    imgurl = 'https://assets.imedao.com/images/cube-closed.png'
    if str(XueQiu.Fetch('https://xueqiu.com/P/' + Symbol,
                        failed_msg='无法获取组合信息')).find(imgurl) >= 0:
        return True
    return False
