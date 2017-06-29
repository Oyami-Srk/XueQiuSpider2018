from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import *
from private_data import proxies, agent, login_telephone, login_password, login_areacode
import time

def request_js(url, body = {}, header = {}, method = 'GET'):
    dcap = dict(DesiredCapabilities.PHANTOMJS) 
    dcap["phantomjs.page.settings.userAgent"] = ( agent )

    for key, value in enumerate(header):
        capability_key = 'phantomjs.page.customHeaders.{}'.format(key)
        dcap[capability_key] = value

    if 'http' in proxies or 'https' in proxies:
        proxy=webdriver.Proxy()
        proxy.proxy_type=ProxyType.MANUAL
        if 'http' in proxies:
            proxy.http_proxy=proxies['http']
        if 'https' in proxies:
            proxy.https_proxy=proxies['https']
        proxy.add_to_capabilities(dcap)
    bro = webdriver.PhantomJS(desired_capabilities=dcap)
    #bro.start_session(webdriver.DesiredCapabilities.PHANTOMJS)
    bro.get(url)
    time.sleep(1)
    r = {}
    html = bro.execute_script("return document.documentElement.outerHTML")
    bro.quit()
    return r, html
