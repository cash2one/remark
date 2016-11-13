# -*- coding:utf-8 -*-
import urllib
import requests
import re
import lxml.html.soupparser as soupparser
import lxml.etree as etree
from pyquery import PyQuery as pq
__demoUrl__ = "http://mp.weixin.qq.com/s?__biz=OTE4MzAyODYx&mid=400183897&idx=1&sn=56e62f1bf0c15669e67264494485c1a0&3rd=MzA3MDU4NTYzMw==&scene=6#rd"
class Eric_crawler(object):
    def crawler(self,url):
        sock = urllib.urlopen(url)
        htmlSource = sock.read()
        sock.close()
        dom = soupparser.fromstring(htmlSource)
        etree.tostring(dom)
        return dom
    def origin(self,url):
        dom = self.crawler(url)
        #print htmlSource
        origin_flag = dom.xpath('//*[@id="copyright_logo"]')
        #print origin_flag[0].text
        if origin_flag:
            status = 200
        else:
            status = 201
        #print status
        return status

    def biz(self,url):
        r = pq(requests.get(url).text)
        strScript =  r.find('script').text()
        biz = re.findall('var appuin = "(.*?)";',strScript)
        return biz
