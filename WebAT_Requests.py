# -*- coding: utf-8 -*-
#! python3

""" WebAT with Requests for Python """

from IWebAT import IWebAT
import requests

class WebAT(IWebAT):
    """ WebAT with Requests """

    def __init__(self, agent='', timeout=None, proxies=None):
        IWebAT.__init__(self, agent, timeout)
        self.__method__ = "Requests"
        self.__session__ = requests.session()
        self.SetHeader('User-Agent', agent)

    def GetCookies(self):
        "Get Cookies from WebAT"
        return self.__session__.cookies

    def GetHeaders(self):
        "Get Headers from WebAT"
        return self.__session__.headers

    def SetCookies(self, cookies):
        "Set Cookies for WebAT"
        self.__session__.cookies = cookies

    def SetHeader(self, key, value):
        "Set Header for WebAT"
        self.__session__.headers[key] = value
        return self.__session__.headers
        
    def SetHeaders(self, headers):
        "Set Headers for WebAT"
        self.__session__.headers = headers
        return self.__session__.headers
        
    def Post(self, url, Body=None):
        "Post Method"
        resp = self.__session__.post(url,Body,proxies=self.__proxies__,timeout=self.__timeout__)
        return resp.headers, resp.content

    def Get(self, url):
        "Get Method"
        resp = self.__session__.get(url, proxies=self.__proxies__,timeout=self.__timeout__)
        return resp.headers, resp.content
