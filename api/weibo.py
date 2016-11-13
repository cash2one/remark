# -*- coding: utf-8 -*-

import json
import base64
import requests
from lxml import etree

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/41.0.2272.118 Safari/537.36'
}


class Crawler(object):
    def __init__(self):
        self.session = requests.session()
        self.login('yzwbj2008@gmail.com', 'range1234')

    def login(self, username, password):
        username = base64.b64encode(username.encode('utf-8')).decode('utf-8')
        postData = {
            "entry": "sso",
            "gateway": "1",
            "from": "null",
            "savestate": "30",
            "useticket": "0",
            "pagerefer": "",
            "vsnf": "1",
            "su": username,
            "service": "sso",
            "sp": password,
            "sr": "1440*900",
            "encoding": "UTF-8",
            "cdult": "3",
            "domain": "sina.com.cn",
            "prelt": "0",
            "returntype": "TEXT",
        }
        loginURL = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        resp = self.session.post(loginURL, data=postData)
        jsonStr = resp.content.decode('gbk')
        info = json.loads(jsonStr)
        if info["retcode"] == "0":
            print("login sucess")
            # 把cookies添加到headers中，必须写这一步，否则后面调用API失败
            cookies = self.session.cookies.get_dict()
            cookies = [key + "=" + value for key, value in cookies.items()]
            cookies = "; ".join(cookies)
            self.session.headers["cookie"] = cookies
        else:
            print("login failed, %s" % info["reason"])

    def crawl_with_url(self, url, upload_pic=True):
        """通过图文链接抓取公众号基本信息及图文信息"""
        # 使用cn域名抓取
        rtn_data = {}

        url = url.split('?')[0]
        rtn_data['url'] = url

        url = url.replace('.com', '.cn')
        print 'crawl:', url

        resp = self.session.get(url, headers=headers, timeout=5)
        # print resp.content
        r = etree.HTML(resp.content)

        # 头像
        try:
            src = r.xpath("//img[@class='por']")[0].attrib.get('src', '')
            big_avatar = src.replace('/50/', '/180/')
        except IndexError:
            big_avatar = ''
        rtn_data['big_avatar'] = big_avatar
        if upload_pic:
            import upload
            # 小头像
            rtn_data['avatar'] = ''
            if rtn_data['big_avatar'].startswith('http'):
                dic_pic = upload.upload(requests.get(rtn_data['big_avatar']).content)
                if dic_pic:
                    rtn_data['avatar'] = dic_pic['key']

        spans = r.xpath("//span[@class='ctt']")
        # 名称
        try:
            name = spans[0].text
        except IndexError:
            name = ''
        rtn_data['name'] = name
        # 认证
        try:
            identify = spans[1].text
            identify = identify[3:] if identify else ''
        except IndexError:
            identify = ''
        rtn_data['identify'] = identify
        # 简介
        try:
            brief = spans[2].text
        except IndexError:
            brief = ''
        rtn_data['brief'] = brief
        # 微博数
        try:
            post_num = r.xpath("//div[@class='tip2']/span")[0].text
            post_num = int(post_num[3:-1]) if post_num else 0
        except IndexError:
            post_num = 0
        rtn_data['post_num'] = post_num

        nums = r.xpath("//div[@class='tip2']/a")
        # 关注数
        try:
            follow_num = nums[0].text
            follow_num = int(follow_num[3:-1]) if follow_num else 0
        except IndexError:
            follow_num = 0
        rtn_data['follow_num'] = follow_num
        # 粉丝数
        try:
            fans_num = nums[1].text
            fans_num = int(fans_num[3:-1]) if fans_num else 0
        except IndexError:
            fans_num = 0
        rtn_data['fans_num'] = fans_num
        # uid
        try:
            uid = nums[2].attrib.get('href', '')
            uid = uid.split('uid=')[1]
        except IndexError:
            uid = ''
        rtn_data['uid'] = uid

        more_info = self.crawl_info_with_uid(uid)
        rtn_data.update(more_info)

        return rtn_data

    def crawl_info_with_uid(self, uid):
        rtn_data = {}
        try:
            url = 'http://weibo.cn/{uid}/info'.format(uid=uid)
            resp = self.session.get(url, headers=headers, timeout=5)
            r = etree.HTML(resp.content.replace('<br/>', '||'))

            items = r.xpath("//div[@class='c']")[2].text.split('||')
            attrs = {u'昵称': 'name', u'认证': 'identify', u'地区': 'area', u'性别': 'gender', u'简介': 'brief', u'标签': 'tags'}
            for item in items:
                key = item.split(':')[0]
                if key in attrs:
                    rtn_data[attrs[key]] = item[3:]
            if 'tags' in rtn_data:
                rtn_data['tags'] = self.crawl_tags_with_uid(uid)
        except Exception, e:
            print e
        return rtn_data

    def crawl_tags_with_uid(self, uid):
        tags = []
        try:
            url = 'http://weibo.cn/account/privacy/tags/?uid={uid}'.format(uid=uid)
            resp = self.session.get(url, headers=headers, timeout=5)
            r = etree.HTML(resp.content)

            items = r.xpath("//div[@class='c'][3]/a")
            tags = [item.text for item in items]
        except Exception, e:
            print e
        return tags


if __name__ == '__main__':
    c = Crawler()
    res = c.crawl_with_url('http://weibo.com/u/5749042654')
    for i in res:
        if isinstance(res[i], basestring):
            print i, '\t', res[i].encode('u8')
        else:
            print i, '\t', res[i]
