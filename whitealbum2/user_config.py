# -*- coding: utf-8 -*-
# !python3

"""             User's configuration files
    If you don't understand what it is, just guess it! """
from IWebAT import IWebAT


def test_login_method(web_autool: IWebAT):
    """
    Function requires a WebAT class which is used in XueQiu Class.
    You can modifiy it to login. Throw any exception you want
    if any error occurs.
    Function return cookies or nothing. if it returns cookies,
    then WebAT will load it automaticly. Remember, cookies must be
    acceptable by WebAT for function `IWebAT.SetCookies(cookie)`.
    """
    pass


config: dict = {
    # Label for spider, used in log/display/exception(default).
    'label': "XS-no1",
    # Comment for spider, uesd by nothing for now.
    'comment': "Common XueqiuSpider for testing, or normal use.",
    # ID for spider, used in log/display/exception(default).
    # [if label is '', ID will be used]
    'id': 0,

    # User Agent
    'agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
    AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/63.0.3239.84 Safari/537.36',
    # Cookies
    'cookie': None,
    # Timeout
    'timeout': None,
    # Proxies
    'proxies': None,
    # Login Flag
    'login': False,
    # Login Method
    # [if login is not False, it will be used]
    'login_method': test_login_method,
    # Parser method for parsing html page, used by nothing for now.
    'parser_method': 'regex',
    # Log method for way to output log message.
    # [
    #     normal: Output to file and Display on screen.
    #     log: Only Output to file
    #     disp: Only Display on screen
    #     slient: Do nothing for logging
    # ]
    'log_method': 'normal',
    # Log file path
    'log_file': 'Log.txt'
}

# Default value for config:
"""

label and id will be 0 if they are both unset.
agent: default to be ''
cookie,timeout,proxies: None
login:False
login_method: default is function `login_method` in default_settings.py
parser_method: regex
log_method: normal
log_file: Log.txt

exception_handler: default is function `exception_handler`
                                  in default_settings.py
^ this function is used to manipulate error message.
^ You can use it to bind different handle methods to every XueQiu Spider.
"""
