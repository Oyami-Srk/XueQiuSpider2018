# -*- coding: utf-8 -*-
#! python3

""" WebAT Interface for Python """

from abc import ABCMeta, abstractmethod

# class IWebAT(object):
#     __metaclass__ = ABCMeta
# class IWebAT(object, metaclass=ABCMeta):
# py3中的类默认继承object
class IWebAT(metaclass=ABCMeta):
    """ Interface for WebAT """
    
    def __init__(self, agent='', timeout=None, proxies=None):
        self.__agent__ = agent
        self.__method__ = "None"
        self.__version__ = 1
        self.__timeout__ = timeout
        self.__proxies__ = proxies

    def __str__(self):
        return "WebAT( V%(version)d ) with %(method)s\nAgent: %(agent)s" % \
               {'version': self.__version__, 'method':self.__method__, 'agent':self.__agent__}

    @abstractmethod
    def GetCookies(self):
        "Get Cookies from WebAT"
        pass

    @abstractmethod
    def GetHeaders(self):
        "Get Headers from WebAT"
        pass

    @abstractmethod
    def SetCookies(self, cookies):
        "Set Cookies for WebAT"
        pass

    @abstractmethod
    def SetHeader(self, key, value):
        "Set Header for WebAT"
        pass

    @abstractmethod
    def SetHeaders(self, headers):
        "Set Headers for WebAT"
        pass

    @abstractmethod
    def Post(self, url, Body=None):
        "Post Method"
        pass

    @abstractmethod
    def Get(self, url):
        "Get Method"
        pass