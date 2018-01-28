# -*- coding: utf-8 -*-
# !python3

""" XueQiu Class """
import time
import re
import importlib
from IWebAT import IWebAT


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
        self._ExceptionHandler(msg, excp, msg_type, msg_level, self.Label,
                               self)

    def Fetch(self, url, Body=None, failed_msg=''):
        try:
            r, c = self.webat.Get(url, Body)
            return c.decode('utf-8')
        except KeyboardInterrupt as e:
            self.Except(str(e), e, msg_type='SYSTEM', msg_level=3)
        except Exception as e:
            self.Except(str(e) if failed_msg is ''
                        else failed_msg, e, msg_type='SYSTEM', msg_level=2)

    def __getattr__(self, attrname):
        index = getattr(importlib.reload(__import__('XueQiuMethod')),
                        'Method_Index')
        try:
            sub = index[attrname]
            func = getattr(importlib.reload(
                getattr(__import__('XueQiuMethod.' + sub), sub)),
                           attrname)

            def fn(*arg, **kw):
                return func(self, *arg, **kw)
            return fn
        except Exception as e:
            e = AttributeError(attrname)
            self.Except(str(e), e)

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
