# -*- coding:utf-8 -*-

# 抓取页面

import re
import requests
import pyquery
import json
import base64
from hashlib import md5
from pyquery import PyQuery as pq


UID = 15200
GROUP_ID = 13727
USER = 'p@yidao.info'
APP_ID = '74ab2a1bie16ee0v156'
APP_KEY = '4ke785ad063312ftf325e22'


class crawler(object):
    
    def rq(self, strUrl):
        """ 发起请求

        @params strUrl string 访问地址
        """
        
        try:
            return requests.get(strUrl)
        except Exception, e:
            print e
            return None
    
    def official(self, strUrl, strVerificationCode='', useVerify=True):
        """ 抓取自媒休息信息

        @params strUrl string 验证地址
        @params strVerificationCode string 验证码
        """

        
        request = self.rq(strUrl)
        if not request:
            return {'status': 604}

        strScript = request.text
        r = pq(strScript)

        # strScript =  r.find('script').text()
        if useVerify:
            # 验证是否用户
            strContent = r.find('#js_content').text()
            strTitle = r.find('#activity-name').text()
            # print strVerificationCode
            # print strContent
            # print strTitle

            if strVerificationCode not in strContent and strVerificationCode not in strTitle:
                return {'status': 603, 'id': ''}

        # 获取数据
        dicReturnData = {}

        # 自媒体name
        lisName = re.findall('var nickname = "(.*?)";', strScript)
        dicReturnData['name'] = lisName[0] if lisName else ''

        # 自媒体用户名
        lisUserName = re.findall('var user_name = "(.*?)";', strScript)
        dicReturnData['user_name'] = lisUserName[0] if lisUserName else ''

        # biz
        lis_biz = re.findall('var appuin = "(.*?)";', strScript)
        if lis_biz:
            str_biz = lis_biz[0].replace(' ', '') if lis_biz[0] else ''
            s = str_biz.split('"||"')
            s.sort(reverse=True)
            dicReturnData['biz'] = s[0]
        else:
            dicReturnData['biz'] = ''

        # 微信号和功能介绍
        dicReturnData['wechat_id'] = ''
        dicReturnData['features'] = ''
        lisData = r.find('p.profile_meta span')
        if lisData:
            for k, item in enumerate(lisData):
                if k == 0:
                    dicReturnData['wechat_id'] = pq(item).text()
                if k == 1:
                    dicReturnData['features'] = pq(item).text()
        if not dicReturnData['wechat_id']:
            dicReturnData['wechat_id'] = dicReturnData['user_name']

        # 大头像
        lisBigAvatar = re.findall('hd_head_img : "(.*?)"\|\|', strScript)
        dicReturnData['big_avatar'] = lisBigAvatar[0] if lisBigAvatar else ''

        import api.upload as upload
        # 小头像
        dicReturnData['avatar'] = ''
        if dicReturnData['big_avatar'].startswith('http'):
            dicPic =  upload.upload(requests.get(dicReturnData['big_avatar']).content)
            if dicPic:
                dicReturnData['avatar'] = dicPic['key']
        
        # 二维码    
        dicReturnData['qrcode'] = ''
        strQrcode = 'http://mp.weixin.qq.com/mp/qrcode?scene=10000005&size=102&__biz=%s' % dicReturnData['biz']
        dicPic =  upload.upload(requests.get(strQrcode).content)
        if dicPic:
            dicReturnData['qrcode'] = dicPic['key']

        # 返回数据
        return dicReturnData

    def get_features(self, strUrl):
        try:
            r = pq(self.rq(strUrl).text)
            query = r.find('p.profile_meta span')
            if query:
                for k, item in enumerate(query):
                    if k == 1:
                        return pq(item).text()
        except Exception:
            pass
        return ''

    def feedback(self, strUrl):
        """ 反馈数据

        @params strUrl string 反馈地址
        """
        try:
            request = self.rq(strUrl)
            r = pq(request.text)
        except Exception, e:
            print e
            return {'url': strUrl, 'title': '', 'publish_time': ''}
        # 获取数据
        dicReturnData = {
            'url': strUrl
        }

        # 标题
        strTitle = r.find('#activity-name').text()
        dicReturnData['title'] = strTitle
        # 发布时间
        strPublishTime = r.find('#post-date').text()
        dicReturnData['publish_time'] = strPublishTime

        # # 图文类型 分析链接地址
        # lisUrl = re.findall('idx=(\d+?)', strUrl)
        # strIdx = lisUrl[0] if lisUrl else ''
        # if strIdx > 2:
        #     dicReturnData['crawl_type'] = '4'
        # else:
        #     dicReturnData['crawl_type'] = strIdx
        #
        # # 首图
        # dicReturnData['picture'] = ''
        # import api.upload as upload
        # lisImg = r.find('#page-content img')
        # if lisImg:
        #     for item in lisImg:
        #         img = pq(item)
        #         strImgSrc = img.attr('data-src')
        #         if strImgSrc:
        #             dicReturnData['picture']
        #             #dicPic =  upload.upload(requests.get(strImgSrc).content)
        #             #if dicPic:
        #             #    dicReturnData['picture'] = dicPic['key']
        #
        #             break
        #
        # if not dicReturnData['picture']:
        #     strScript =  r.find('script').text()
        #     lisPic = re.findall('var cover = "(.*?)";', strScript)
        #     dicReturnData['picture'] = lisPic[0] if lisPic else ''
        #
        # if dicReturnData['picture']:
        #     dicPic =  upload.upload(requests.get(dicReturnData['picture']).content)
        #     if dicPic:
        #         dicReturnData['picture'] = dicPic['key']

        ## 请求API获取阅读数
        #dicSendData = {
        #    'appid': '74ab2a1bie16ee0v156',
        #    'signature': '4ke785ad063312ftf325e22',
        #    'url': strUrl
        #}
        #response = requests.post('http://index.gsdata.cn/api/data/getWxNumsByApi', data = json.dumps(dicSendData))

        # 返回数据
        return dicReturnData

    def add_to_group(self, article_link):
        # url = 'http://index.gsdata.cn/api/data/addWxToGroup'
        url = 'http://open.gsdata.cn/api/wx/wxapi/add_wx_to_group'
        data = {
            'appid': APP_ID,
            # 'uid': UID,
            'appkey': APP_KEY,
            'groupid': GROUP_ID,
            'wxJson': json.dumps([{'wx_url': article_link}])
        }
        return self.get_api_data(url, data)

    def get_num_real_time(self, link):
        # 获取实时阅读数
        url = 'http://open.gsdata.cn/api/wx/wxapi/wx_nums_monitor'
        data = {'url': link, 'appid': APP_ID, 'appkey': APP_KEY}
        res = self.get_api_data(url, data)
        return res

    @staticmethod
    def make_signature(data):
        """
        生成请求签名
        :param data: 请求参数
        :return: 签名
        """
        json_data = json.dumps(data, sort_keys=True, separators=(',', ':'), ).lower()
        signature = md5(json_data + APP_KEY).hexdigest()
        return signature

    @staticmethod
    def urlsafe_encode(data):
        """
        进行url安全编码
        :param data: 请求参数
        :return: 编码后的请求参数
        """
        urlsafe_data = base64.urlsafe_b64encode(json.dumps(data))
        return urlsafe_data

    def get_api_data(self, url, data):
        """
        通过api获取数据
        :param url: api的url
        :param data: 请求参数
        """
        headers = {'Content-Type': 'application/json'}
        try:
            data['signature'] = self.make_signature(data)
            r = requests.post(url, data=self.urlsafe_encode(data), headers=headers)
            res = r.json()
            return res.get('returnData', {})
        except Exception, e:
            print e
            return {}

if __name__ == '__main__':
    c = crawler()
    # res = c.add_to_group('http://mp.weixin.qq.com/s?__biz=MjM5MTMwMTg2Mw==&mid=401425759&idx=1&sn=54fb882913e1cfa9fc4ab27d9b98358f&scene=4#wechat_redirect')
    # res = c.add_to_group('http://mp.weixin.qq.com/s?__biz=MzIwMDIwODc0OA==&mid=208636057&idx=1&sn=1d416834738995e4c5e96e1db8666596&3rd=MzA3MDU4NTYzMw==&scene=6#rd')
    res = c.get_num_real_time('http://mp.weixin.qq.com/s?__biz=MzA4OTY4MDIyMg==&mid=401655317&idx=1&sn=c21d2334bfbf6847eb3ad8279e0cbb88&3rd=MzA3MDU4NTYzMw==&scene=6#rd')
    print res
