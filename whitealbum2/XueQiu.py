# -*- coding: utf-8 -*-
# !python3

""" XueQiu Class """
import time
import re
import json
from IWebAT import IWebAT
import numpy as np
from pandas import Series, DataFrame

class XueQiu:
    """ General System Functions """

    def __init__(self, web_autool: IWebAT, config: dict):
        self.RawConfig = config
        try:
            self._ExceptionHandler = config['exception_handler']
        except:
            try:
                from default_settings import exception_handler
                self._ExceptionHandler = exception_handler
            except:
                raise Exception("No handler!!!")

        keys = config.keys()
        if 'label' in keys and config['label'] is "":
            self.Label = config['label']
        elif 'id' in keys:
            self.Label = str(config['id'])
        else:
            self.Label = str(0)

        try:
            self.webat = web_autool(
                agent=config['agent'] if 'agent' in keys else '',
                cookie=config['cookie'] if 'cookie' in keys else None,
                timeout=config['timeout'] if 'timeout' in keys else None,
                proxies=config['proxies'] if 'proxies' in keys else None
            )
        except:
            self.Except("Cannot Initialize WebAT", msg_level=1)

        self.Fetch('https://xueqiu.com')

        try:
            if config['login'] if 'login' in keys else False:
                if 'login_method' in keys:
                    cookie = config['login_method'](self.webat)
                else:
                    try:
                        from default_settings import login_method
                        cookie = login_method(self.webat)
                    except:
                        cookie = ''
                if cookie:
                    self.webat.SetCookies(cookie)
        except:
            self.Except("Cannot Login", msg_level=2)

        self.parser_method =\
            config['parser_method'] if 'parser_method' in keys else 'regex'
        self.log_method =\
            config['log_method'] if 'log_method' in keys else 'normal'
        self.log_file =\
            config['log_file'] if 'log_file' in keys else 'Log.txt'

        self.isDisp = False
        self.isLog = False
        if self.log_method is 'normal':
            self.isDisp = True
            self.isLog = True
        elif self.log_method is 'log':
            self.isLog = True
        elif self.log_method is 'disp':
            self.isDisp = True
        elif self.log_method is 'slient':
            pass
        else:
            self.Except("Unknown Log method", msg_level=3)

    def log(self, msg, end='\n'):
        if self.isDisp:
            print("<" + self.Label + ">" +
                  time.strftime("[%Y-%m-%d %H:%M:%S]",
                                time.localtime()) + msg, end=end)
        if self.isLog:
            try:
                with open(self.log_file, 'a', encoding='UTF-8') as f:
                    f.write("<" + self.Label + ">" +
                            time.strftime("[%Y-%m-%d %H:%M:%S] ",
                                          time.localtime()) + msg + end)
            except:
                self.Except("I/O Error", type='SYSTEM', level=2)

    def Except(self, msg, excp=None, msg_type='GENERAL', msg_level=0):
        self._ExceptionHandler(msg, excp, msg_type, msg_level, self.Label, self)

    def Fetch(self, url, Body=None, failed_msg=''):
        try:
            r, c = self.webat.Get(url, Body)
            return c.decode('utf-8')
        except KeyboardInterrupt as e:
            self.Except(str(e), e, msg_type='SYSTEM', msg_level=3)
        except Exception as e:
            self.Except(str(e) if failed_msg is ''
                        else failed_msg, e, msg_type='SYSTEM', msg_level=2)

    def CheckLogin(self):
        c = self.Fetch('https://xueqiu.com/setting/user',
                       failed_msg='Unable to fetch user page!')
        parsed_list = re.findall(r'"profile":"/(.*?)","screen_name":"(.*?)"',
                                 c)

        if parsed_list == []:
            self.log('未登录')
            return False
        self.log('登录成功，你的用户 id 是：%s, 你的用户名是：%s' % (parsed_list[0]))
        return True

    def CheckBanished(self):
        c = re.compile('系统检测到您的IP最近访问过于频繁')
        if len(c.findall(self.Fetch('https://xueqiu.com/'))) > 0:
            return True
        return False

    """ Portfolio Functions """

    def GetPortfolioInfo(self, Symbol):
        postUrl = 'https://xueqiu.com/P/'
        baseUrl = 'https://xueqiu.com/cubes/analyst/histo/stat.json'
        baseUrl = baseUrl + '?cube_symbol=%s&type=%s'
        cont = self.Fetch(postUrl + Symbol, failed_msg='无法获取组合信息')
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
            cont = self.Fetch(postUrl)
            rj = json.loads(cont)
            turnover_3m = rj['values'][0]['value']
            if len(rj['values']) < 5:
                turnover_12m = np.nan
            else:
                turnover_12m = rj['values'][2]['value']

            postUrl = baseUrl % (Symbol, 'liquidity')
            cont = self.Fetch(postUrl)
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
                'market': self.GetPortfolioMarket(Symbol),
                'closed': self.CheckPortfolioClosed(Symbol),
                'turnover_3m': turnover_3m,
                'turnover_12m': turnover_12m,
                'liquidity_3m': liquidity_3m,
                'liquidity_12m': liquidity_12m,
                'LastUpdate': LastUpdate,
                'name': name,
                'cash_ratio': cash_ratio}

    def GetPortfolioDetails(self, Symbol):
        postUrl = 'https://xueqiu.com/P/'
        data = self.Fetch(postUrl + Symbol, failed_msg='u无法获取组合信息')

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

    def GetPortfolioHistories(self, Symbol):
        url = 'https://xueqiu.com/cubes/rebalancing/history.json'
        url = url + '?count=50&page=%d&cube_symbol=%s'
        cont = self.Fetch(url % (1, Symbol))
        data = json.loads(cont)
        DataList = data['list']
        totalCount = data['totalCount']
        PageCount = 1
        for i in range(50, totalCount, 50):
            PageCount = PageCount + 1
            cont = self.Fetch(url % (PageCount, Symbol))
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

    def GetRateChart(self, Symbol):
        postUrl = 'https://xueqiu.com/cubes/nav_daily/all.json?' + \
                  'cube_symbol=' + Symbol + '&until=' + \
                  str(int(time.time()) * 1000)
        return json.loads(self.Fetch(postUrl, failed_msg='无法获取组合信息'))

    """ Market Function """

    def GetMarketList(self,
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
        TotalCount = json.loads(self.Fetch(postUrl % 1))['totalCount']
        List = []
        cont = self.Fetch(postUrl % TotalCount)
        for item in json.loads(cont)['list']:
            List.append(item['symbol'])
        return List

    def GetMarketList_details(self,
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
        TotalCount = json.loads(self.Fetch(postUrl % 1))['totalCount']
        cont = self.Fetch(postUrl % TotalCount)
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

    def GetMarketListInfo(self,
                          market='cn',
                          profit='monthly_gain',
                          sort='best_benefit',
                          sale_flag='0',
                          stock_positions='0'):
        oridata = self.GetMarketList_details(market,
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
                cont = self.Fetch(postUrl)
            except Exception as e:
                if not self.Except(str(e), e):
                    break
            rj = json.loads(cont)
            turnover_3m_list.append(rj['values'][0]['value'])
            if len(rj['values']) < 5:
                turnover_12m_list.append(np.nan)
            else:
                turnover_12m_list.append(rj['values'][2]['value'])

            postUrl = baseUrl % (i, 'liquidity')
            try:
                cont = self.Fetch(postUrl)
            except Exception as e:
                if not self.Except(str(e), e):
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

    def GetPortfolioMarket(self, Symbol):
        postUrl = 'https://xueqiu.com/cubes/nav_daily/all.json?'
        cont = self.Fetch(postUrl + 'cube_symbol=' + Symbol + '&until=' +
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

    def CheckPortfolioClosed(self, Symbol):
        imgurl = 'https://assets.imedao.com/images/cube-closed.png'
        if str(self.Fetch('https://xueqiu.com/P/' + Symbol,
                          failed_msg='无法获取组合信息')).find(imgurl) >= 0:
            return True
        return False

    """ Artical Functions """
    def GetPortfolioFromPage(self, url):
        cont = self.Fetch(url, failed_msg='无法获取页面信息')
        c = re.compile('(<!-- 文章标题-->.*<!-- pdf-->)')
        page = c.findall(cont)[0]
        c = re.compile('(ZH\d{6,7})')
        ori = c.findall(page)
        List = []
        for symbol in ori:
            if symbol not in List:
                List.append(symbol)
        return List

    def GetPagesUrl(self, regx=''):
        base = 'https://xueqiu.com/v4/statuses/user_timeline.json?'
        base = base + 'user_id=5171159182&page='

        if regx == '':
            regx = '最受关注 & 优质组合调仓路线'
        c = re.compile(regx)
        Data = json.loads(self.Fetch(base + '0', failed_msg='无法获取用户帖子信息'))
        maxPage = Data['maxPage']
        List = []

        for i in range(0, maxPage + 1):
            cont = self.Fetch(base + str(i), failed_msg='无法获取用户帖子信息')
            try:
                Data = json.loads(cont)
                for post in Data['statuses']:
                    if len(c.findall(post['title'])) != 0:
                        print(post['title'] + ':' + post['target'])
                        List.append('https://xueqiu.com' + post['target'])
            except Exception as e:
                if not self.Except(str(e), e):
                    break
        return List
