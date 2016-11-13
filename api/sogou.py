# -*- coding: utf-8 -*-

import re
import json
import requests
from pyquery import PyQuery as pq

host_sogou = 'http://weixin.sogou.com'
host_mp = 'http://mp.weixin.qq.com'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/41.0.2272.118 Safari/537.36'
}
idx_category = {
    0: '热门', 1: '推荐', 2: '段子手', 3: '养生堂', 4: '私房话', 5: '八卦精', 6: '爱生活',
    7: '财经迷', 8: '汽车迷', 9: '科技咖', 10: '潮人帮', 11: '辣妈帮', 12: '点赞党', 13: '旅行家',
    14: '职场人', 15: '美食家', 16: '古今通', 17: '学霸族', 18: '星座控', 19: '体育迷'
}


class Crawler(object):
    def __init__(self):
        self.session = requests.session()

    def search_wechat_id(self, wechat_id_src):
        """
        :func: 通过搜索微信号抓取公众号基本信息及最近的文章、发布时间
        :param wechat_id_src: 公众号的微信号
        :return: 基本信息、最近文章
        """
        resp = self.session.get('http://weixin.sogou.com/weixin?type=1&query={wid}'.format(wid=wechat_id_src),
                                headers=headers, timeout=5)
        r = pq(resp.text)
        results = r.find('div.results>div')
        rtn_data = {}
        if not results:
            return rtn_data
        for item in results:
            r_item = pq(item)
            name = r_item.find('h3').text()
            wechat_id = r_item.find('label[name="em_weixinhao"]').text()
            profile_url = r_item.attr('href')
            if wechat_id == wechat_id_src:
                rtn_data['name'] = name
                rtn_data['wechat_id'] = wechat_id
                rtn_data['profile_url'] = profile_url
                p_res = r_item.find('p.s-p3')
                for p_item in p_res:
                    p = pq(p_item)
                    tit = p.find('span.sp-tit').text()
                    txt = p.find('span.sp-txt')
                    if tit.endswith(u'介绍：'):
                        rtn_data['brief'] = txt.text()
                    elif tit.endswith(u'认证：'):
                        rtn_data['identify'] = txt.text()
                    elif tit.endswith(u'文章：'):
                        mp_item = pq(txt)
                        href = mp_item.find('a').attr('href')
                        if href:
                            if not href.startswith('http'):
                                href = host_sogou + href
                            title = mp_item.find('a').text()
                            post_time = mp_item.find('span.hui').text()
                            post_time = int(post_time.split('\'')[1]) if post_time else 0
                            rtn_data['href'] = href
                            rtn_data['title'] = title
                            rtn_data['post_time'] = post_time
                break
        return rtn_data

    def get_comment_with_url(self, _url):
        """
        :func: 通过文章链接抓取评论及阅读数、点赞数
        :param _url: 图文链接
        :return: 评论、阅读数、点赞数
        """
        if 'signature' not in _url:
            return {}
        _url = _url.replace('http://mp.weixin.qq.com/s', 'http://mp.weixin.qq.com/mp/getcomment')
        resp = self.session.get(_url, headers=headers, timeout=5)
        rtn_data = resp.json()
        if 'elected_comment_total_cnt' in rtn_data:
            rtn_data['comment_num'] = rtn_data.pop('elected_comment_total_cnt')
        if 'base_resp' in rtn_data:
            rtn_data.pop('base_resp')
        return rtn_data

    def crawl_with_url(self, _url, upload_pic=False, content=False):
        """
        :func: 通过图文链接抓取公众号详细信息及图文信息
        :param _url: 图文链接
        :param upload_pic: 是否上传图片到七牛
        :param content: 是否抓正文
        :return: 详细信息、图文信息
        """
        # print 'crawl:', _url

        resp = self.session.get(_url, headers=headers, timeout=5)
        str_script = resp.text
        r = pq(str_script)

        # 获取数据
        rtn_data = {}

        # str_script = r.find('script').text()
        if content:
            str_content = r.find('#js_content').text()
            # 图文内容（仅文本）
            rtn_data['content'] = str_content if str_content else ''

        # 自媒体name
        lis_name = re.findall('var nickname = "(.*?)";', str_script)
        rtn_data['name'] = lis_name[0] if lis_name else ''

        # 自媒体用户名
        lis_gh_id = re.findall('var user_name = "(.*?)";', str_script)
        rtn_data['gh_id'] = lis_gh_id[0] if lis_gh_id else ''

        # biz
        lis_biz = re.findall('var appuin = "(.*?)";', str_script)
        if lis_biz:
            str_biz = lis_biz[0].replace(' ', '') if lis_biz[0] else ''
            s = str_biz.split('"||"')
            s.sort(reverse=True)
            rtn_data['biz'] = s[0]
        else:
            rtn_data['biz'] = ''

        # 图文url
        lis_url = re.findall('var msg_link = "(.*?)";', str_script)
        rtn_data['url'] = lis_url[0] if lis_url else ''

        # 图文标题
        lis_title = re.findall('var msg_title = "(.*?)";', str_script)
        rtn_data['title'] = lis_title[0] if lis_title else ''

        # 原创
        lis_original = re.findall('var _copyright_stat = "(.*?)";', str_script)
        rtn_data['original'] = lis_original[0] if lis_original else '0'

        # 图文发布时间
        lis_post_time = re.findall('var ct = "(.*?)";', str_script)
        rtn_data['post_time'] = int(lis_post_time[0]) if lis_post_time else 0

        # 微信号和功能介绍
        rtn_data['wechat_id'] = ''
        rtn_data['brief'] = ''
        lis_data = r.find('p.profile_meta span')
        if lis_data:
            for k, item in enumerate(lis_data):
                if k == 0:
                    rtn_data['wechat_id'] = pq(item).text()
                if k == 1:
                    rtn_data['brief'] = pq(item).text()
        if not rtn_data['wechat_id']:
            rtn_data['wechat_id'] = rtn_data['gh_id']

        if upload_pic:
            # 大头像
            lis_big_avatar = re.findall('hd_head_img : "(.*?)"\|\|', str_script)
            rtn_data['big_avatar'] = lis_big_avatar[0] if lis_big_avatar else ''

            import upload
            # 小头像
            rtn_data['avatar'] = ''
            if rtn_data['big_avatar'].startswith('http'):
                dic_pic = upload.upload(requests.get(rtn_data['big_avatar'], timeout=5).content)
                if dic_pic:
                    rtn_data['avatar'] = dic_pic['key']

            # 二维码
            rtn_data['qrcode'] = ''
            str_qrcode = 'http://mp.weixin.qq.com/mp/qrcode?scene=10000005&size=102&__biz=%s' % rtn_data['biz']
            dic_pic = upload.upload(requests.get(str_qrcode, timeout=5).content)
            if dic_pic:
                rtn_data['qrcode'] = dic_pic['key']

        # 返回数据
        return rtn_data

    def get_msg_with_profile_url(self, profile_url):
        """
        :func: 通过公众号链接获取最近10条图文链接（如果公众号一天可发多篇，则大于10条）
        :param profile_url: 公众号链接
        :return: 按日期分组的图文链接列表
        """
        resp = self.session.get(profile_url, headers=headers, timeout=5)
        str_script = resp.text
        trans = {'&quot;': '"', '&nbsp;': ' ', '&amp;': '&', r'\\/': '/'}
        for key in trans:
            while str_script.find(key) != -1:
                str_script = str_script.replace(key, trans[key])
        lis_msg = re.findall('var msgList = \'(.*?)\';', str_script)
        msg_str = lis_msg[0] if lis_msg else ''
        try:
            msg_data = json.loads(msg_str).get('list', [])
            msgs = {}
            for item in msg_data:
                datetime = item['comm_msg_info']['datetime']
                app_msg_ext_info = item['app_msg_ext_info']
                msgs.setdefault(datetime, [])
                msg_item_list = msgs[datetime]
                multi_app_msg_item_list = app_msg_ext_info.pop('multi_app_msg_item_list')
                msg_item_list.append(host_mp + app_msg_ext_info['content_url'])
                msg_item_list.extend([host_mp + i['content_url'] for i in multi_app_msg_item_list])
            rtn_data = {'msg': msgs}
        except Exception, e:
            print e
            rtn_data = {}
        return rtn_data

    def get_msg_with_wechat_id(self, wechat_id_src):
        """
        :func: 通过搜索公众号的微信号获取最近10条图文链接（如果公众号一天可发多篇，则大于10条）
        :param wechat_id_src: 微信号
        :return: 按日期分组的图文链接列表
        """
        resp = self.search_wechat_id(wechat_id_src)
        profile_url = resp.get('profile_url')
        if not profile_url:
            return {}
        return self.get_msg_with_profile_url(profile_url)

    def crawl_with_wechat_id(self, wechat_id_src, upload_pic=False, content=False, comment=False):
        """
        :func: 搜索微信号获取公众号详细信息及图文信息
        :param wechat_id_src: 微信号
        :param upload_pic: 是否上传图片到七牛
        :param content: 是否抓正文
        :param comment: 是否抓评论
        :return: 详细信息及图文信息
        """
        resp = self.search_wechat_id(wechat_id_src)
        href = resp.get('href')
        if not href:
            return resp
        resp_by_href = self.crawl_with_url(href, upload_pic, content)
        resp.update(resp_by_href)
        if comment:
            resp_comment = self.get_comment_with_url(href)
            resp.update(resp_comment)
        return resp

    def gen_index_wechat_url(self):
        """
        :func: 获取搜狗微信首页的公众号链接及分类
        """
        for idx in range(20):
            link = 'http://weixin.sogou.com/pcindex/pc/pc_{idx}/pc_{idx}.html'.format(idx=idx)
            # print link
            resp = self.session.get(link, headers=headers, timeout=5)
            r = pq(resp.text)
            _items = r.find('ul#pc_{idx}_subd>li'.format(idx=idx))
            for item in _items:
                r_item = pq(item)
                _url = r_item.find('h4>a').attr('href')
                # print url.encode('u8')
                yield _url, idx_category.get(idx, '')

    def gen_index_wechat_info(self):
        """
        :func: 获取搜狗微信首页的公众号详细信息及图文信息
        """
        for item in self.gen_index_wechat_url():
            resp = self.crawl_with_url(item[0])
            resp['idx_category'] = item[1]
            yield resp


def print_res(result):
    """
    :func: 结果格式化打印
    :param result: 字典结果
    """
    for key in result:
        val = result[key]
        if isinstance(val, basestring):
            print key, val.encode('u8')
        else:
            print key, val


if __name__ == '__main__':
    c = Crawler()
    # print_res(c.search_wechat_id('huayinguoji'))
    # print c.crawl_with_url('http://mp.weixin.qq.com/s?__biz=MzI0OTA3ODUzOA==&mid=413063691&idx=1'
    #                        '&sn=1e370f660c2b32d7345ee38e50138acd&3rd=MzA3MDU4NTYzMw==&scene=6#rd')
    # print_res(c.crawl_with_wechat_id('thepapernews', upload_pic=False, content=True, comment=True))
    # for i in c.gen_index_wechat_info():
    #     print i
    # res = c.get_msg_with_profile_url(
    #     'http://mp.weixin.qq.com/profile?src=3&timestamp=1461636916&ver=1&signature='
    #     'V73l*s2tTdJBPht90ThR2vHNSWPGPnWxeOa8XQ5aTXBI4fTl6Bd*kGFtsINSxj7po-kRiSG7U7xCy5FksttT7Q==')
    res = c.get_msg_with_wechat_id('d1comchina')
    if res:
        msg = res['msg']
        for d in msg:
            items = msg[d]
            # print "-" * 10, d, "-" * 10
            for url in items:
                print url.encode('u8')

