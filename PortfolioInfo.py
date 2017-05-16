# -*- coding: utf-8 -*-
#! python3

from FetchPortfolio import request, GetHeader
import re, json, time
import numpy as np

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
            # secid = stocks['stock_symbol'][2:] + '.' + stocks['stock_symbol'][:2]
            secid = (stocks['stock_symbol'][2:] + '.' + stocks['stock_symbol'][:2]) if stocks['stock_symbol'][0] == 'S' else stocks['stock_symbol']
            Stocks_List.append({'Symbol': secid,
                                # 'Symbol': stocks['stock_symbol'],
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

# # An example:
# Symbol = 'ZH542513'
# test = GetPortfolioDetails(Symbol)
# pos = test['Stocks']
# pos.append({'Symbol': 'CNY',
#             'Name': '现金',
#             'Weight': float('%.6f' % (test['cash_ratio'] / 100)),
#             'Segment': np.nan})
# pos = DataFrame(pos)[['Symbol', 'Name', 'Weight', 'Segment']]
# pos = pos.rename(columns={'Symbol': '证券代码', 'Name': '证券简称', 'Weight': '权重', 'Segment': '雪球分类'})


def GetPortfolioHistories(Symbol):
    # if CheckLogin() == False:
    #     try:
    #         AutoLogin()
    #     except KeyboardInterrupt:
    #         raise KeyboardInterrupt()
    #     except:
    #         raise Exception("登陆错误!")
    Header = GetHeader(login=True)
    try:
        resp, cont = request('https://xueqiu.com/cubes/rebalancing/history.json?count=50&page=%d&cube_symbol=%s'
                             % (1, Symbol), header=Header)
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except:
        raise Exception('网络错误！')

    data = json.loads(cont.decode('utf-8'))
    DataList = data['list']
    totalCount = data['totalCount']
    PageCount = 1
    for i in range(50, totalCount, 50):
        PageCount = PageCount + 1
        try:
            resp, cont = request('https://xueqiu.com/cubes/rebalancing/history.json?count=50&page=%d&cube_symbol=%s'
                                 % (PageCount, Symbol), header=Header)
        except KeyboardInterrupt:
            raise KeyboardInterrupt()
        except:
            raise Exception('网络错误！')
        data = json.loads(cont.decode('utf-8'))
        DataList.extend(data['list'])

    Histories = []
    for item in DataList:
        # 这里加一个判断item['status'] == 'success'可以剔除已取消的调仓
        # 这里通过item['category']可以判断是系统自动分红送配(sys_rebalancing)还是用户自己调仓(user_rebalancing)
        # 通过item['created_at']可以获知调仓创建日期
        # 而item['updated_at']里面则是调仓执行日期(可能因为不是交易日而延迟？) 改值为Unix时间戳(ms)
        # 遍历rebalancing_histories以获得调仓
        if item['status'] == 'canceled' or item['status'] == 'failed':
        # if item['status'] == 'failed':
            continue

        for i in item['rebalancing_histories']:
            if i['prev_weight_adjusted'] == None:
                i['prev_weight_adjusted'] = 0
            if i['target_weight'] == None:
                i['target_weight'] = 0

            Histories.append(
                {
                    'Name': i['stock_name'],
                    # 'Symbol': i['stock_symbol'],
                    'Symbol': (i['stock_symbol'][2:] + '.' + i['stock_symbol'][:2]) if i['stock_symbol'][0] == 'S' else i['stock_symbol'],
                    'Prev': i['prev_weight_adjusted'],
                    'Target': i['target_weight'],
                    'Date': i['updated_at'],
                    'Category': item['category'],
                    'Price': i['price']
                }
            )

    return Histories
    # Having a nice day......

def ShowHistories(Histories):
    for item in Histories:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['Date'] / 1000)) + '  ', end='')
        print(item['Name'] + ' ' + item['Symbol'] + '   ', end='')
        print(('%.2f' % item['Prev']) + '% --> ' + ('%.2f' % item['Target']) + '%   ', end='')
        if item['Price'] == None:
            print('成交价 NaN' + '   ', end='')
        else:
            print('成交价 ' + ('%.2f' % item['Price']) + '   ', end='')
        if item['Category'] == 'user_rebalancing':
            print('用户调仓')
        elif item['Category'] == 'sys_rebalancing':
            print('系统调仓(分红送配)')
        else:
            print('未知调仓: ' + item['Category'])
