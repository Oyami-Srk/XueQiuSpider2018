# -*- coding: utf-8 -*-
#! python3

from FetchPortfolio import request, GetHeader
import re, json, time
import numpy as np

from xueqiu_login import AutoLogin, CheckLogin

def GetPortfolioDetails(Symbol):
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

def GetPortfolioHistories(Symbol):
    if CheckLogin() == False:
        try:
            AutoLogin()
        except KeyboardInterrupt:
            raise KeyboardInterrupt()
        except:
            raise Exception("登陆错误!")
    Header = GetHeader()
    try:
        resp, cont = request('https://xueqiu.com/cubes/rebalancing/history.json?count=50&page=%d&cube_symbol=%s' % (1, Symbol), header=Header)
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except:
        raise Exception("网络错误!")

    data = json.loads(cont.decode('utf-8'))
    DataList = data['list']
    totalCount = data['totalCount']
    PageCount = 1
    for i in range(50, totalCount, 50):
        PageCount = PageCount + 1
        try:
            resp, cont = request(
                'https://xueqiu.com/cubes/rebalancing/history.json?count=50&page=%d&cube_symbol=%s' % (PageCount, Symbol),
                header=Header)
        except KeyboardInterrupt:
            raise KeyboardInterrupt()
        except:
            raise Exception("网络错误!")
        data = json.loads(cont.decode('utf-8'))
        DataList.extend(data['list'])

    Histories = []
    for item in DataList:
        # 这里加一个判断item['status']=='success'可以剔除已取消的调仓
        # 这里通过item['category']可以判断是系统自动分红(sys_rebalancing)还是用户自己调仓(user_rebalancing)
        # 通过item['created_at']可以获知调仓创建日期, 而item['updated_at']里面则是调仓执行日期(可能因为不是交易日而延迟?) 改值为Unix时间戳(ms)
        # 遍历rebalancing_histories以获得调仓
        if item['status'] == 'failed':
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
                    'Prev': i['prev_weight_adjusted'],
                    'Target': i['target_weight'],
                    'Date': i['updated_at'],
                    'Category': item['category']
                }
            )

    return Histories

    # Having a nice day......

def ShowHistories(Histories):
    for item in Histories:
        print(time.strftime('%Y-%m-%d', time.localtime(item['Date']/1000)) + ': ', end='')
        print(item['Name'] + '(' + item['Symbol'] + ')        ', end='')
        print(('%.2f' % item['Prev']) + '%  --->  ' + ('%.2f' % item['Target']) + '%    ', end='')
        if item['Category'] == 'user_rebalancing':
            print('用户调仓')
        elif item['Category'] == 'sys_rebalancing':
            print('系统调仓(分红)')
        else:
            print('未知调仓 ' + item['Category'])