from RateChart import *

if __name__ == '__main__':
    #raise Exception("该模块不可以单独执行!")
    import imp
    try:
        imp.find_module('httplib2')
        hl2 = True
    except:
        hl2 = False
    try:
        imp.find_module('pandas')
        pd = True
    except:
        pd = False
    try:
        imp.find_module('tables')
        tb = True
    except:
        tb = False

    if not hl2:
        print("httplib2模块未安装!")
    if not pd:
        print("pandas模块未安装!")
    if not tb:
        print("PyTables模块未安装!")
    if not hl2 or not pd or not tb:
        quit()

    print("是否保存百分比? (Y/N) ", end='')
    key = input()
    if key == 'y' or key == 'Y':
        noPercent = False
    else:
        noPercent = True

    print("是否自动下载沪深下的所有组合走势图? (Y/N) ", end='')
    key = input()
    if key == 'y' or key == 'Y':
        print("请输入保存的文件名(默认为RateChart)> ", end='')
        filename = input()
        if filename.strip() == '':
            filename = 'RateChart'
        print("开始下载.")
        SaveRateChartsToHDF5(GetMarketList(), filename + '.h5', noPercent)
        print("下载完毕.")
        quit()
    print("下载单个组合吗? (Y/N) ", end='')
    key = input()
    if key == 'y' or key == 'Y':
        print("请输入组合代码(以ZH开头)> ", end='')
        symbol = input()
        print("请输入保存的文件名(默认为RateChart)> ", end='')
        filename = input()
        print("开始下载.")
        if filename == '':
            SaveRateChartToHDF5(symbol, 'RateChart.h5', noPercent)
        else:
            SaveRateChartToHDF5(symbol, filename + '.h5', noPercent)
        print("下载完毕.")
        quit()
    print("组合列表从市场获取吗? (Y/N) ", end='')
    key = input()
    if key == 'y' or key == 'Y':
        print("选项默认为第一项")
        print("请输入市场区域(cn/hk/us)> ", end='')
        market = input()
        print("请输入收益排序类型(monthly_gain/daily_gain/annualized_gain_rate) >", end='')
        profit = input()
        print("请输入收益排序方法(best_benefit/grow_fast/win_market) >", end='')
        sort = input()
        print("是否包括创业板? (Y/N) ", end='')
        sf = input()
        print("是否过滤单只股票组合? (N/Y) ", end='')
        sp = input()
        print("请输入保存的文件名(默认为RateChart)> ", end='')
        filename = input()

        if market.strip() == '':
            market = 'cn'
        if profit.strip() == '':
            profit = 'monthly_gain'
        if sort.strip() == '':
            sort = 'best_benefit'
        if sf == '':
            sf = 'Y'
        if sp == '':
            sp = 'N'
        if filename == '':
            filename = 'RateChart'

        if sf == 'Y' or sf == 'y':
            sf = '0'
        else:
            sf = '1'
        if sp == 'Y' or sp == 'y':
            sp = '1'
        else:
            sp = '0'

        print("开始下载.")
        SaveRateChartsToHDF5(GetMarketList(market, profit, sort, sf, sp), filename + '.h5', noPercent)
        print("下载完毕.")
        quit()
    print("请输入组合代码列表(以逗号分隔):")
    symbol_list = []
    symbol_list_input = input()
    for symbol in symbol_list_input.split(','):
        symbol_list.append(symbol)
    if symbol_list == [] or symbol_list == ['']:
        print("空输入!")
        quit()
    print("请输入保存的文件名(默认为RateChart)> ", end='')
    filename = input()
    if filename == '':
        filename = 'RateChart'
    print("开始下载.")
    SaveRateChartsToHDF5(symbol_list, filename + '.h5', noPercent)
    print("下载完毕.")
