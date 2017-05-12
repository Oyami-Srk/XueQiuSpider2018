# -*- coding: utf-8 -*-
#! python3

from FetchPortfolio import request, GetHeader
import re, json, time
import numpy as np

from xueqiu_login import login

def GetPortfolioInfo(Symbol):
    postUrl = 'https://xueqiu.com/P/'
    Header = GetHeader()
    try:
        resp, cont = request(postUrl + Symbol, header=Header)
    except:
        raise Exception('无法获取组合信息！')
    data = cont.decode('utf-8')

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
            Stocks_List.append({'Name': stocks['stock_name'], 'Weight': stocks['weight'], 'Symbol': stocks['stock_symbol'], 'Segment': stocks['segment_name']})


    Info = {
        'Symbol': Obj_Info['symbol'],
        'Name': Obj_Info['name'],
        'Market': Obj_Info['market'],
        'begin': time.strftime('%Y-%m-%d', time.localtime(Obj_Info['created_at']/1000)),
        'update': time.strftime('%Y-%m-%d', time.localtime(Obj_Info['sell_rebalancing']['updated_at']/1000)),
        'end': np.nan if Obj_Info['close_date']=='' else time.strftime('%Y-%m-%d', time.localtime(Obj_Info['close_date']/1000)),
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
