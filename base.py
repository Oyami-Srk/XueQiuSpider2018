# -*- coding: utf-8 -*-
#! python3

from config import *
from WebAT_Requests import WebAT
import hashlib
import os
import re
import sqlite3
from win32.win32crypt import CryptUnprotectData


def GetCookieFromChrome(host=('.%s' % host)):
    cookiepath = os.environ['LOCALAPPDATA'] + '/Google/Chrome/User Data/Default/Cookies'
    sql = "select host_key, name, encrypted_value from cookies where host_key='%s'" % host
    with sqlite3.connect(cookiepath) as conn:
        cu = conn.cursor()
        cookies = {name: CryptUnprotectData(encrypted_value)[1].decode()
                   for host_key, name, encrypted_value in cu.execute(sql).fetchall()}
        # print(cookies)
        return cookies


WAT = WebAT(agent=agent, cookie=None, timeout=20, proxies={})
WAT.Get(baseurl)
Logined = False


def login():
    global Logined, WAT
    if not Logined:
        cookie_chrome = GetCookieFromChrome(host=('.%s' % host))
        WAT = WebAT(agent=WAT.__agent__, cookie=cookie_chrome, timeout=WAT.__timeout__, proxies=WAT.__proxies__)
        Logined = True


def login_deprecated():
    def get_md5(text):
        md5 = hashlib.md5()
        md5.update(text.encode())
        return md5.hexdigest().upper()

    global Logined
    if Logined:
        return ''

    # # 验证码
    # try:
    #     # r, c = request('https://xueqiu.com/snowman/service/captcha/img', body=None, header=headers, method='GET')
    #     rr = requests.get('https://xueqiu.com/snowman/service/captcha/img', headers=headers)
    # except KeyboardInterrupt:
    #     raise KeyboardInterrupt()
    # except:
    #     raise Exception('网络错误！')
    # imgdata = json.loads(rr.content.decode('utf-8'))['image_base_64']
    # with open('captcha.png', 'wb') as fimg:
    #     fimg.write(base64.decodebytes(imgdata.encode('utf-8')))

    try:
        WAT.Get('https://xueqiu.com/service/csrf?api=%2Fuser%2Flogin')
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except:
        # raise Exception('Network Unreliable')
        raise Exception('网络错误！')

    post_data = {
        'areacode': login_areacode,
        'password': get_md5(login_password),
        'remember_me': 'on',
        'telephone': login_telephone
    }
    try:
        r, c = WAT.Post('https://xueqiu.com/user/login', post_data)
        Logined = True
        return r['Set-Cookie']
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except:
        # raise Exception('Network Unreliable')
        raise Exception('网络错误！')


def login_check(echo=True):
    def Echo(flag):
        if(echo):
            print("已登录" if flag else "未登录")

    if not Logined:
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


def FetchPage(url, need_login=False, failed_msg=''):
    if need_login is True and Logined is False:
        login()
        if login_check() is False:
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
