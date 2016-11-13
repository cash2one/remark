# -*- coding: utf-8 -*-


import requests
from pyquery import PyQuery as pq


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/41.0.2272.118 Safari/537.36'
}


class Crawler(object):
    def __init__(self):
        self.session = requests.session()

    def crawl_with_url(self, url, upload_pic=True):
        if not url.endswith('/'):
            url = url + '/'
        rtn_data = {'url': url}

        resp = self.session.get(url, headers=headers, timeout=5)
        r = pq(resp.text)
        #
        name = r.find('h1.profile_name > a').text()
        brief = r.find('h2.media_description').text()
        rtn_data['name'] = name
        rtn_data['brief'] = brief

        # 大头像
        big_avatar = r.find('div.mp-info > img').attr('src')
        rtn_data['big_avatar'] = big_avatar
        if upload_pic:
            import upload
            # 小头像
            rtn_data['avatar'] = ''
            if rtn_data['big_avatar'].startswith('http'):
                dic_pic = upload.upload(requests.get(rtn_data['big_avatar']).content)
                if dic_pic:
                    rtn_data['avatar'] = dic_pic['key']

        return rtn_data


if __name__ == '__main__':
    c = Crawler()
    res = c.crawl_with_url('http://toutiao.com/m4716103991/')
    for i in res:
        if isinstance(res[i], basestring):
            print i, '\t', res[i].encode('u8')
        else:
            print i, '\t', res[i]
