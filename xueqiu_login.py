# -*- coding: utf-8 -*-
#! python3

from FetchPortfolio import request, GetHeader
import re, hashlib

def get_md5(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    return md5.hexdigest().upper()

def login(telephone, password):
    url = 'https://xueqiu.com/'
    headers = GetHeader()
    headers['Referer'] = "https://xueqiu.com/"
    login_url_api = "https://xueqiu.com/service/csrf?api=%2Fuser%2Flogin"
    try:
        request(login_url_api, header=headers)
    except:
        print('Error1')
        raise Exception("网络错误!")
    login_url = "https://xueqiu.com/user/login"
    postdata = {
        "areacode": "86",
        "password": get_md5(password),
        "remember_me": "on",
        "telephone": telephone
    }
    try:
        resp, cont = request(login_url, body=postdata, header=headers, method='POST')
        headers['Cookie'] = resp['Set-Cookie']
        res_, cont = request("https://xueqiu.com/setting/user", header=headers)
    except:
        raise Exception("网络错误!")

    res = re.findall(r'"profile":"/(.*?)","screen_name":"(.*?)"', cont.decode('utf-8'))
    if res == []:
        print("登录失败，请检查你的手机号和密码输入是否正确")
        return ''
    else:
        print('登录成功，你的用户 id 是：%s, 你的用户名是：%s' % (res[0]))
        return resp['Set-Cookie']


if __name__ == '__main__':
    telephone = ""
    password = ""
    login(telephone, password)
