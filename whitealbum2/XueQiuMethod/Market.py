import json
import numpy as np
import time
from pandas import DataFrame


def GetMarketList(XueQiu,
                  market='cn',
                  profit='monthly_gain',
                  sort='best_benefit',
                  sale_flag='0',
                  stock_positions='0'):
    baseUrl = 'https://xueqiu.com/cubes/discover/rank/cube/list.json' \
              '?market=%s&sale_flag=%s&stock_positions=%s&sort=%s&' \
              'category=12&profit=%s'
    postUrl = baseUrl % (market, sale_flag,
                         stock_positions, sort, profit) + '&count=%d'
    TotalCount = 0
    # Get TotlCount
    TotalCount = json.loads(XueQiu.Fetch(postUrl % 1))['totalCount']
    List = []
    cont = XueQiu.Fetch(postUrl % TotalCount)
    for item in json.loads(cont)['list']:
        List.append(item['symbol'])
    return List


def GetMarketList_details(XueQiu,
                          market='cn',
                          profit='monthly_gain',
                          sort='best_benefit',
                          sale_flag='0',
                          stock_positions='0'):
    baseUrl = 'https://xueqiu.com/cubes/discover/rank/cube/list.json?' \
              'market=%s&sale_flag=%s&stock_positions=%s&sort=%s' \
              '&category=12&profit=%s'
    postUrl = baseUrl % (market, sale_flag, stock_positions, sort, profit)
    postUrl = postUrl + '&count=%d'
    TotalCount = 0
    # Get TotlCount
    TotalCount = json.loads(XueQiu.Fetch(postUrl % 1))['totalCount']
    cont = XueQiu.Fetch(postUrl % TotalCount)
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
                     index=Symbol_list)


def GetMarketListInfo(XueQiu,
                      market='cn',
                      profit='monthly_gain',
                      sort='best_benefit',
                      sale_flag='0',
                      stock_positions='0'):
    oridata = XueQiu.GetMarketList_details(market,
                                           profit,
                                           sort,
                                           sale_flag,
                                           stock_positions)
    baseUrl = 'https://xueqiu.com/cubes/analyst/histo/stat.json?'
    baseUrl = baseUrl + 'cube_symbol=%s&type=%s'
    turnover_3m_list = []
    turnover_12m_list = []
    liquidity_3m_list = []
    liquidity_12m_list = []
    for i in list(oridata.index):
        postUrl = baseUrl % (i, 'turnover')
        try:
            cont = XueQiu.Fetch(postUrl)
        except Exception as e:
            if not XueQiu.Except(str(e), e):
                break
        rj = json.loads(cont)
        turnover_3m_list.append(rj['values'][0]['value'])
        if len(rj['values']) < 5:
            turnover_12m_list.append(np.nan)
        else:
            turnover_12m_list.append(rj['values'][2]['value'])

        postUrl = baseUrl % (i, 'liquidity')
        try:
            cont = XueQiu.Fetch(postUrl)
        except Exception as e:
            if not XueQiu.Except(str(e), e):
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


def GetPortfolioMarket(XueQiu, Symbol):
    postUrl = 'https://xueqiu.com/cubes/nav_daily/all.json?'
    cont = XueQiu.Fetch(postUrl + 'cube_symbol=' + Symbol + '&until=' +
                        str(int(time.time()) * 1000), failed_msg='无法获取组合信息')
    try:
        Data = json.loads(cont)[1]
    except:
        return 'no_portfolio'

    if Data['symbol'] == 'SH000300':
        return 'cn'
    elif Data['symbol'] == 'HKHSI':
        return 'hk'
    elif Data['symbol'] == 'SP500':
        return 'us'
    return 'undefined'
