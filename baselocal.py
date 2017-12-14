# coding=utf-8

from config import agent, host
import os
import requests
import sqlite3
from win32.win32crypt import CryptUnprotectData

Logined = False
baseHeader = {
    'Host': host,
    'User-Agent': agent,
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cache-Control': 'max-age=0',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': '',
    # 'Cookie': '',   # must be filled
    'Connection': 'keep-alive',
}
cookies = {}


def GetCookieFromChrome(host='.' + host):
    cookiepath = os.environ['LOCALAPPDATA'] + '/Google/Chrome/User Data/Default/Cookies'
    sql = "select host_key, name, encrypted_value from cookies where host_key='%s'" % host
    with sqlite3.connect(cookiepath) as conn:
        cu = conn.cursor()
        cookies = {name: CryptUnprotectData(encrypted_value)[1].decode() for host_key, name, encrypted_value \
                   in cu.execute(sql).fetchall()}
        # print(cookies)
        return cookies


def request_logined(url, body = None, method = 'GET'):
    global baseHeader
    global cookies
    if not cookies:
        cookies = GetCookieFromChrome()
    try:
        if method.upper() == 'GET':
            resp = requests.get(url, headers=baseHeader, cookies=cookies, allow_redirects=1)
        elif method.upper() == 'POST':
            resp = requests.post(url, body, headers=baseHeader, cookies=cookies, allow_redirects=1)
        r = resp.headers
        c = resp.content
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except:
        raise Exception('Connect Error!')
    return r, c
