# -*- coding: utf-8 -*-
#! python3

# from config import agent, baseurl, host
from WebAT_Requests import WebAT
import os
import re
import sqlite3
from win32.win32crypt import CryptUnprotectData


class XUEQIU(WebAT):
    """ Base for XUEQIU """

    def __init__(self, host=None, agent='', login=False, cookie=None, timeout=None, proxies=None):
        if not login:
            WebAT.__init__(self, agent=agent, cookie=None, timeout=timeout, proxies=proxies)
        elif cookie:
            WebAT.__init__(self, agent=agent, cookie=cookie, timeout=timeout, proxies=proxies)
        else:
            WebAT.__init__(self,
                           agent=agent,
                           cookie=self.GetCookieFromChrome(host=('.%s' % host)),
                           timeout=timeout,
                           proxies=proxies)
            self.CheckLogin(login, echo=True)

    def GetCookieFromChrome(self, host=('.%s' % host)):
        cookiepath = os.environ['LOCALAPPDATA'] + '/Google/Chrome/User Data/Default/Cookies'
        sql = "select host_key, name, encrypted_value from cookies where host_key='%s'" % host
        with sqlite3.connect(cookiepath) as conn:
            cu = conn.cursor()
            self.cookies = {name: CryptUnprotectData(encrypted_value)[1].decode()
                            for host_key, name, encrypted_value in cu.execute(sql).fetchall()}
            return self.cookies

    def CheckLogin(self, login, echo=True):
        def Echo(flag):
            if (echo):
                print("已登录" if flag else "未登录")

        if not login:
            Echo(False)
            return False
        try:
            r, c = self.Get('https://xueqiu.com/setting/user')
        except KeyboardInterrupt:
            raise KeyboardInterrupt()
        except:
            raise Exception('Network Unreliable')

        parsed_list = re.findall(r'"profile":"/(.*?)","screen_name":"(.*?)"', c.decode('utf-8'))
        if parsed_list == []:
            Echo(False)
            return False
        Echo(True)
        print('登录成功，你的用户 id 是：%s, 你的用户名是：%s' % (parsed_list[0]))
        return True

    def Fetch(self, url, failed_msg='', Body=None):
        try:
            r, c = self.Get(url, Body)
            return c.decode('utf-8')
        except KeyboardInterrupt:
            raise KeyboardInterrupt()
        except:
            if failed_msg == '':
                raise Exception("Network Unreliable")
            else:
                raise Exception(failed_msg)


# # Example
# XQ = XUEQIU(host=host, agent=agent, login=True, timeout=20, proxies={})
# # WAT = WebAT(agent=agent, cookie=None, timeout=20, proxies={})
# # WAT.Get(baseurl)
# # Logined = False
