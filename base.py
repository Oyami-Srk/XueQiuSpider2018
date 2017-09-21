# -*- coding: utf-8 -*-
#! python3

from config import *
from WebAT_Requests import WebAT
import hashlib, re

WAT = WebAT(agent, 20, proxies)
WAT.Get('https://xueqiu.com/')
XQ_Logined = False

def xueqiu_login():
    def get_md5(text):
        md5 = hashlib.md5()
        md5.update(text.encode())
        return md5.hexdigest().upper()

    global XQ_Logined
    if XQ_Logined:
        return ''

    try:
        WAT.Get('https://xueqiu.com/service/csrf?api=%2Fuser%2Flogin')
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except:
        raise Exception('Network Unreliable')

    post_data = {
        'areacode': login_areacode,
        'password': get_md5(login_password),
        'remember_me': 'on',
        'telephone': login_telephone
    }
    try:
        r, c = WAT.Post('https://xueqiu.com/user/login', post_data)
        XQ_Logined = True
        return r['Set-Cookie']
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except:
        raise Exception('Network Unreliable')

def xueqiu_login_check(echo = True):
    def Echo(flag):
        if(echo):
            print("已登录" if flag else "未登录")

    if not XQ_Logined:
        Echo(False)
        return False
    try:
        r, c = WAT.Get('https://xueqiu.com/setting/user')
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

def FetchPage(url, need_login = False, failed_msg = ''):
    if need_login == True and XQ_Logined == False:
        xueqiu_login()
        if xueqiu_login_check() == False:
            raise Exception("Login Failed")

    try:
        r, c = WAT.Get(url)
        return c.decode('utf-8')
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except:
        if failed_msg == '':
            raise Exception("Network Unreliable")
        else:
            raise Exception(failed_msg)
