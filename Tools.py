# -*- coding: utf-8 -*-
#! python3

import Page
import time
from config import delay_time
import numpy as py
from pandas import Series, DataFrame


def ConvertToDataframe(Data, noPercent = True):
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
    return ConvertToDataframe(Page.GetRateChart(Symbol), noPercent)

def GetRateChartsAsDataframe(Symbols, noPercent = True, ErrorSymbol = []):
    Charts = []
    for Symbol in Symbols:
        try:
            Charts.append(GetRateChartAsDataframe(Symbol, noPercent))
        except KeyboardInterrupt:
            print('\nUser Interrupt!\n')
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
    n = len(Symbols)
    for Symbol in Symbols:
        print('%d/%d - %.2f' % (Symbols.index(Symbol), n, (Symbols.index(Symbol) / n) * 100) + '%')
        time.sleep(delay_time)
        try:
            ifCaptcha = Page.CheckifCaptcha()
            while (ifCaptcha == True):
                print('Please Enter the CAPTCHA of XUEQIU in your local browser and '
                      'input anything to continue if you make sure XUEQIU is available. '
                      '(Please open http://xueqiu.com/ manually after enter the CAPTCHA)')
                key = input()
                ifCaptcha = Page.CheckifCaptcha()
            SaveRateChartToHDF5(Symbol, Path, noPercent)
            print(' [Done]')
        except KeyboardInterrupt:
            print('\nUser Interrupt!\n')
            break
        except:
            ErrorSymbol.append(Symbol)

# 保存在市场上获取的组合的信息
def SaveMarketListInfo(market = 'cn',
                       profit = 'monthly_gain',
                       sort = 'best_benefit',
                       sale_flag = '0',
                       stock_positions = '0',
                       filename = 'portfolio_summary.h5'):
    Page.GetMarketListInfo(market, profit, sort, sale_flag, stock_positions).to_hdf(filename, 'summary')



# ！危险！容易被封！
# market标明要获取的List位于何市场, 若为空则不限市场
# closed表明是否获取已关停的组合
# Min为穷举下限
# Max为穷举上限
def GetAllPortfolio(market = 'cn', closed = False, Min = 0, Max = 1300000, ErrorSymbol = []):
    Tsil = []
    for neko in range(Min, Max + 1):
        print('%d/%d - %.2f' % (neko, Max, ((neko - Min) / (Max - Min)) * 100) + '%', end='')
        SecretCode = 'ZH' + '%.6d' % neko
        time.sleep(delay_time)
        try:
            ifCaptcha = Page.CheckifCaptcha()
            while (ifCaptcha == True):
                print('Please Enter the CAPTCHA of XUEQIU in your local browser and '
                      'input anything to continue if you make sure XUEQIU is available. '
                      '(Please open http://xueqiu.com/ manually after enter the CAPTCHA)')
                key = input()
                ifCaptcha = Page.CheckifCaptcha()
            pmarket = Page.GetPortfolioMarket(SecretCode)
            print(' ' + SecretCode + ':' + pmarket, end='')
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
                        if Page.CheckPortfolioClosed(SecretCode) == False:
                            Tsil.append(SecretCode)
                    else:
                        print(' [Done]')
                        continue
            else:
                if closed == True:
                    Tsil.append(SecretCode)
                else:
                    if Page.CheckPortfolioClosed(SecretCode) == False:
                        Tsil.append(SecretCode)
        except Exception:
            ErrorSymbol.append(SecretCode)
        except KeyboardInterrupt:
            print('\nUser Interrupt!\n')
            break
        print(' [Done]')

    return Tsil


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
        time.sleep(delay_time)
        try:
            ifCaptcha = Page.CheckifCaptcha()
            while (ifCaptcha == True):
                print('Please Enter the CAPTCHA of XUEQIU in your local browser and '
                      'input anything to continue if you make sure XUEQIU is available. '
                      '(Please open http://xueqiu.com/ manually after enter the CAPTCHA)')
                key = input()
                ifCaptcha = Page.CheckifCaptcha()
            df[Symbols[i]] = Page.GetPortfolioInfo(Symbols[i])
            print(' [Done]')
        except KeyboardInterrupt:
            print('User Interrupt!')
            break
        except:
            ErrorSymbol.append(Symbols[i])
    return df

def ShowHistories(Histories):
    ret = ''
    for item in Histories:
        str1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['Date'] / 1000)) + '  '
        str2 = item['Name'] + ' ' + item['Symbol'] + '   '
        str3 = ('%.2f' % item['Prev']) + '% --> ' + ('%.2f' % item['Target']) + '%   '
        if item['Price'] == None:
            str4 = '成交价 NaN' + '   '
        else:
            str4 = '成交价 ' + ('%.2f' % item['Price']) + '   '

        if item['Category'] == 'user_rebalancing':
            str5 = '用户调仓'
        elif item['Category'] == 'sys_rebalancing':
            str5 = '系统调仓(分红送配)'
        else:
            str5 = '未知调仓: ' + item['Category']
        print(str1 + str2 + str3 + str4 + str5)
        ret = ret + str1 + str2 + str3 + str4 + str5 + '\n'
    return ret

def CheckStockCN(Symbol):
    return len(re.findall('(S.\d{6})', Symbol)) > 0

def GetPortfoliosFromPages(Symbols):
    PF_List = []
    n = len(Symbols)
    for Symbol in Symbols:
        print('%d/%d - %.2f' % (Symbols.index(Symbol), n, (Symbols.index(Symbol) / n) * 100) + '%')
        try:
            PF_List.append(Page.GetPortfolioFromPage(Symbol))
            print(' [Done]')
        except:
            raise Exception('无法获取信息！')
    return PF_List

