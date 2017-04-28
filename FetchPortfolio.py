# -*- coding: utf-8 -*-
#! python3
#Date: 2017-04-19
#You need HDF5 support to run this script
#Follow the installation guide in https://github.com/PyTables/PyTables/ may help you a lot

import urllib, httplib2
import time
import json, re
# import pandas as pd
import numpy as np
from pandas import Series, DataFrame

Cookie_glo = ''  # 节约资源而来的保存第一次获取的cookie

baseHeader = {
    'Host': 'xueqiu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': '',
    'Cookie': '',   # must be filled
    'Connection': 'keep-alive'
}

# 祖传request, 从py2升级而来
def request(url, body = '', header = '', method = 'GET'):
    try:
        resp, content = httplib2.Http(timeout=20).request(url, method=method, headers=header,
                                                          body=urllib.parse.urlencode(body))
        return resp, content
    except KeyboardInterrupt:
        print('User Interrupt!')
    except KeyError:
        raise('Request Failed!')

def GetHeader():
    global baseHeader
    global Cookie_glo
    Header = baseHeader
    if Cookie_glo == '':
        try:
            resp, cont = request('https://xueqiu.com/', header=Header)
        except KeyboardInterrupt:
            print('User Interrupt!')
        except:
            raise Exception('无法连接！')
        Header['Cookie'] = resp['set-cookie']
        Cookie_glo = resp['set-cookie']
    else:
        Header['Cookie'] = Cookie_glo
    return Header

# e.g. https://xueqiu.com/cubes/nav_daily/all.json?cube_symbol=ZH958027
def __GetRateChart__(Symbol):
    postUrl = 'https://xueqiu.com/cubes/nav_daily/all.json?'
    Header = GetHeader()
    try:
        resp, cont = request(postUrl + 'cube_symbol=' + Symbol + '&until='
                             + str(int(time.time()) * 1000), header=Header)
    except KeyboardInterrupt:
        print('User Interrupt!')
    except:
        raise Exception('无法获取组合信息！')
    Data = json.loads(cont)[0]
    return Data

def __SaveAsDataframe__(Data, noPercent = True):
    if(Data == [] or len(Data['list']) == 0):
        raise Exception('数据错误！')
    DateList = []
    ValueList = []
    if not noPercent:
        PercentList = []
    for i in Data['list']:
        DateList.append(i['date'])
        ValueList.append(i['value'])
        if not noPercent:
            PercentList.append(i['percent'])
    if not noPercent:
        dataframe = DataFrame({'Value': ValueList, 'Percent': PercentList}, index=DateList)
    else:
        dataframe = DataFrame({'Value': ValueList}, index=DateList)
    # 画图时用plt.plot(pd.to_datetime(Series(df.index)), df.Value)
    return dataframe

def GetRateChartAsDataframe(Symbol, noPercent = True):
    return __SaveAsDataframe__(__GetRateChart__(Symbol), noPercent)

def GetRateChartsAsDataframe(Symbols, noPercent = True, ErrorSymbol = []):
    Charts = []
    for Symbol in Symbols:
        try:
            Charts.append(GetRateChartAsDataframe(Symbol, noPercent))
        except KeyboardInterrupt:
            print('User Interrupt!')
            break
        except:
            ErrorSymbol.append(Symbol)
    return Charts

def SaveRateChartToHDF5(Symbol, Path = 'RateChart.h5', noPercent = True):
    dataframe = GetRateChartAsDataframe(Symbol, noPercent)
    if Path.strip() == '':
        raise Exception('路径不能为空！')
    dataframe.to_hdf(Path, Symbol)

def SaveRateChartsToHDF5(Symbols = [], Path = 'RateChart.h5', noPercent = True, ErrorSymbol = []):
    for Symbol in Symbols:
        try:
            SaveRateChartToHDF5(Symbol, Path, noPercent)
        except KeyboardInterrupt:
            print('User Interrupt!')
            break
        except:
            ErrorSymbol.append(Symbol)

# # 读数据的一种方式
# ZH002001 = pd.read_hdf('monthly_gain.h5', 'ZH002001')
# # 读数据的另一种方式
# alldf = pd.HDFStore('RateChart.h5')
# ZHid = alldf.keys()
# df = {}
# for i in range(len(alldf)):
#     df[alldf.keys()[i]] = alldf[ZHid[i]]

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
    Header = GetHeader()
    TotalCount = 0
    # Get TotlCount
    try:
        resp, cont = request(postUrl % 1, header = Header)
    except KeyboardInterrupt:
        print('User Interrupt!')
    except:
        raise Exception('网络错误！')
    TotalCount = json.loads(cont)['totalCount']
    List = []
    try:
        resp, cont = request(postUrl % TotalCount, header = Header)
    except KeyboardInterrupt:
        print('User Interrupt!')
    except:
        raise Exception('网络错误！')
    for item in json.loads(cont)['list']:
        List.append(item['symbol']) 
    return List

# 返回通过All.json得到的一些信息
def __GetMarketListInfoViaMarketListsOriginDataWrittenInJsonAndReturnADataframeIndexedBySymbolWith6Columns__\
                (market = 'cn',
                 profit = 'monthly_gain',
                 sort = 'best_benefit',
                 sale_flag = '0',
                 stock_positions = '0'):
    baseUrl = 'https://xueqiu.com/cubes/discover/rank/cube/list.json?' \
              'market=%s&sale_flag=%s&stock_positions=%s&sort=%s&category=12&profit=%s'
    postUrl = baseUrl %(market, sale_flag, stock_positions, sort, profit) + '&count=%d'
    Header = GetHeader()
    TotalCount = 0
    # Get TotlCount
    try:
        resp, cont = request(postUrl % 1, header = Header)
    except KeyboardInterrupt:
        print('User Interrupt!')
    except:
        raise Exception('网络错误！')
    TotalCount = json.loads(cont)['totalCount']
    try:
        resp, cont = request(postUrl % TotalCount, header = Header)
    except KeyboardInterrupt:
        print('User Interrupt!')
    except:
        raise Exception('网络错误！')
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
    oridata = __GetMarketListInfoViaMarketListsOriginDataWrittenInJsonAndReturnADataframeIndexedBySymbolWith6Columns__\
        (market, profit, sort, sale_flag, stock_positions)
    baseUrl = 'https://xueqiu.com/cubes/analyst/histo/stat.json?cube_symbol=%s&type=%s'
    Header = GetHeader()
    turnover_3m_list = []
    turnover_12m_list = []
    liquidity_3m_list = []
    liquidity_12m_list = []
    for i in list(oridata.index):
        postUrl = baseUrl % (i, 'turnover')
        try:
            resp, cont = request(postUrl, header = Header)
        except KeyboardInterrupt:
            print('User Interrupt!')
        except:
            raise Exception('网络错误！')
        rj = json.loads(cont)
        turnover_3m_list.append(rj['values'][0]['value'])
        if len(rj['values']) < 5:
            turnover_12m_list.append(np.nan)    # For Unknown reason, some of these may not have regular data
        else:
            turnover_12m_list.append(rj['values'][2]['value'])

        postUrl = baseUrl % (i, 'liquidity')
        try:
            resp, cont = request(postUrl, header = Header)
        except KeyboardInterrupt:
            print('User Interrupt!')
        except:
            raise Exception('网络错误！')
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

# 保存在市场上获取的组合的信息
def SaveMarketListInfo(market = 'cn',
                       profit = 'monthly_gain',
                       sort = 'best_benefit',
                       sale_flag = '0',
                       stock_positions = '0',
                       filename = 'portfolio_summary.h5'):
    GetMarketListInfo(market, profit, sort, sale_flag, stock_positions).to_hdf(filename, 'summary')

# 获取组合所在的市场分类
def GetPortfolioMarket(Symbol):
    postUrl = 'https://xueqiu.com/cubes/nav_daily/all.json?'
    Header = GetHeader()
    try:
        resp, cont = request(postUrl + 'cube_symbol=' + Symbol + '&until='
                             + str(int(time.time()) * 1000), header=Header)
    except KeyboardInterrupt:
        print('User Interrupt!')
    except:
        raise Exception('无法获取组合信息！')

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
    postUrl = 'https://xueqiu.com/P/'
    Header = GetHeader()
    try:
        resp, cont = request(postUrl + Symbol, header = Header)
    except KeyboardInterrupt:
        print('User Interrupt!')
    except:
        raise Exception('无法获取组合信息！')

    if str(cont).find('https://assets.imedao.com/images/cube-closed.png') >= 0:
        return True
    return False

# market标明要获取的List位于何市场, 若为空则不限市场
# closed表明是否获取已关停的组合
# Min 为穷举下限
# Max 为穷举上限
def GetAllPortfolio(market = 'cn', closed = False, Min = 0, Max = 1300000, ErrorSymbol = []):
    Tsil = []
    for neko in range(Min, Max + 1):
        # print('%d/%d - %.2f' % (neko, Max, ((neko - Min) / (Max - Min)) * 100), end='')
        # print('%d/%d - %.2f' % (neko, Max, ((neko - Min) / (Max - Min)) * 100), end='\n')
        print('%d/%d - %.2f' % (neko, Max, ((neko - Min) / (Max - Min)) * 100) + '%', end='')
        SecretCode = 'ZH' + '%.6d' % neko
        try:
            pmarket = GetPortfolioMarket(SecretCode)
            if pmarket == 'no_portfolio' or pmarket == 'undefined':
                print(' [Done]')
                continue
            if market.strip() != '':
                if closed == True:
                    if market == pmarket:
                        Tsil.append(SecretCode)
                    else:
                        print(' [Done]')
                        continue
                else:
                    if market == pmarket:
                        if CheckPortfolioClosed(SecretCode) == False:
                            Tsil.append(SecretCode)
                    else:
                        print(' [Done]')
                        continue
            else:
                if closed == True:
                    Tsil.append(SecretCode)
                else:
                    if CheckPortfolioClosed(SecretCode) == False:
                        Tsil.append(SecretCode)
        except KeyboardInterrupt:
            print('User Interrupt!')
            break
        except:
            ErrorSymbol.append(SecretCode)
        print(' [Done]')

    return Tsil

# 返回一个字典
def GetPortfolioInfo(Symbol):
    postUrl = 'https://xueqiu.com/P/'
    baseUrl = 'https://xueqiu.com/cubes/analyst/histo/stat.json?cube_symbol=%s&type=%s'
    Header = GetHeader()
    try:
        resp, cont = request(postUrl + Symbol, header = Header)
    except KeyboardInterrupt:
        print('User Interrupt!')
    except:
        raise Exception('无法获取组合信息！')
    c = re.compile('(<div (style="border:0;padding-left:0" |)'
                   'class="cube-profit-day cube-profit">.+?</div>.+?</div>)')
    data = c.findall(cont.decode('utf-8'))
    day_return = float(data[0][0].split('>')[4].split('%')[0]) / 100
    month_return = float(data[1][0].split('>')[4].split('%')[0]) / 100
    nav = float(data[2][0].split('>')[4].split('<')[0])  # 净值
    total_return = float(nav - 1)
    # 获取组合创建日
    c = re.compile('\d{4}-\d{2}-\d{2}')
    date = c.findall(cont.decode('utf-8'))[0]
    try:
        postUrl = baseUrl % (Symbol, 'turnover')
        try:
            resp, cont = request(postUrl, header=Header)
        except KeyboardInterrupt:
            print('User Interrupt!')
        except:
            raise Exception('网络错误！')
        rj = json.loads(cont)
        turnover_3m = rj['values'][0]['value']
        if len(rj['values']) < 5:
            turnover_12m = np.nan  # For Unknown reason, some of these may not have regular data
        else:
            turnover_12m = rj['values'][2]['value']

        postUrl = baseUrl % (Symbol, 'liquidity')
        try:
            resp, cont = request(postUrl, header=Header)
        except KeyboardInterrupt:
            print('User Interrupt!')
        except:
            raise Exception('网络错误！')
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
            'liquidity_12m': liquidity_12m
            }

def GetPortfoliosInfo(Symbols, ErrorSymbol = []):
    # col = ['begin', 'day_return', 'month_return', 'nav', 'total_return', 'market', 'closed',
    #        'turnover_3m', 'turnover_12m', 'liquidity_3m', 'liquidity_12m']
    df = {}
    n = len(Symbols)
    # for Symbol in Symbols:
    #     # print('%d/%d - %.2f' % (Symbols.index(Symbol), n, (Symbols.index(Symbol) / n) * 100), end='\n')
    #     print('%d/%d - %.2f' % (Symbols.index(Symbol), n, (Symbols.index(Symbol) / n) * 100) + '%')
    #     df[Symbol] = GetPortfoliosInfo(Symbol)
    for i in range(n):
        print('%d/%d - %.2f' % (i, n, (i / n) * 100) + '%')
        try:
            df[Symbols[i]] = GetPortfoliosInfo(Symbols[i])
            print(' [Done]')
        except KeyboardInterrupt:
            print('User Interrupt!')
            break
        except:
            ErrorSymbol.append(i)
    df = DataFrame(df).T
    # df = DataFrame(df, index=col).T
    return df
