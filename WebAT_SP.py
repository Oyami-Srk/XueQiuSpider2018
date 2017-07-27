# -*- coding: utf-8 -*-
#! python3

""" WebAT with Selenium+PhantomJS for Python """

from IWebAT import IWebAT
# import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support import ui as UI
import time


class WebAT(IWebAT):
    """ WebAT with Selenium+PhantomJS """

    def __init__(self, agent='', timeout=None, proxies=None):
        IWebAT.__init__(self, agent, timeout)
        self.__method__ = "Selenium+PhantomJS"
        self.__dcap__ = dict(DesiredCapabilities.PHANTOMJS)
        self.__dcap__["phantomjs.page.settings.userAgent"] = (agent)
        if proxies:
            if 'http' in proxies or 'https' in proxies:
                proxy = webdriver.Proxy()
                proxy.proxy_type = ProxyType.MANUAL
                if 'http' in proxies:
                    proxy.http_proxy = proxies['http']
                if 'https' in proxies:
                    proxy.https_proxy = proxies['https']
                proxy.add_to_capabilities(self.__dcap__)

        self.__session__ = webdriver.PhantomJS(
            desired_capabilities=self.__dcap__)

    def GetCookies(self):
        "Get Cookies from WebAT"
        c = self.__session__.get_cookies()
        dt = {}
        for i in c:
            dt[i['name']] = i['value']
        return dt

    def GetHeaders(self):
        "Get Headers from WebAT"
        pass

    def SetCookies(self, cookies):
        "Set Cookies for WebAT"
        self.__session__.delete_all_cookies()
        for cookie in cookies:
            self.__session__.add_cookie({k: cookie[k] for k in (
                'name', 'value', 'domain', 'path', 'expiry')})

    def SetHeader(self, key, value):
        "Set Header for WebAT"
        capability_key = 'phantomjs.page.customHeaders.{}'.format(key)
        self.__dcap__[capability_key] = value
        self.__session__.capabilities = self.__dcap__
        return 'using GetHeaders plz'

    def SetHeaders(self, headers):
        "Set Headers for WebAT"
        self.__dcap__.clear()
        for key, value in enumerate(headers):
            capability_key = 'phantomjs.page.customHeaders.{}'.format(key)
            self.__dcap__[capability_key] = value
        self.__session__.capabilities = self.__dcap__
        return 'using GetHeaders plz'

    def Post(self, url, Body=None):
        "Post Method"
        raise Exception("Wrong Invoke")

    def Get(self, url):
        "Get Method"
        self.__session__.get(url)
        return '', self.__session__.page_source

    def get_element(self, by, i):
        "Just For SP"
        if by == "id":
            return self.__session__.find_element_by_id(i)
        elif by == "class_name":
            return self.__session__.find_element_by_class_name(i)
        elif by == "name":
            return self.__session__.find_element_by_name(i)
        else:
            raise Exception("No!")
    
    def select_element(self, by, i, v):
        "For sp only"
        if by == "value":
            UI.Select(i).select_by_value(v)
        elif by == "index":
            UI.Select(i).select_by_index(v)
        elif by == "visible_text":
            UI.Select(i).select_by_visible_text(v)
        else:
            raise Exception("No!")