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
        rtn_data = {}
        rtn_data['url'] = url

        resp = self.session.get(url, headers=headers, verify=False, timeout=5)
        r = pq(resp.text)
        agree = r.find('span.zm-profile-header-user-agree > strong').text()
        rtn_data['total_like_num'] = agree

        thanks = r.find('span.zm-profile-header-user-thanks > strong').text()
        rtn_data['total_thank_num'] = thanks

        num_items = r.find('span.num')
        nums = [pq(ni).text() for ni in num_items]
        asks, answers, posts, collections, logs = nums
        rtn_data['total_ask_num'] = asks
        rtn_data['total_answer_num'] = answers
        rtn_data['total_post_num'] = posts
        rtn_data['total_favorite_num'] = collections
        rtn_data['total_record_num'] = logs

        name = r.find('div.title-section > span.name').text()
        brief = r.find('div.title-section > span.bio').text()
        rtn_data['name'] = name
        rtn_data['brief'] = brief

        location = r.find('span.location').text()
        business = r.find('span.business').text()
        education = r.find('span.education').text()
        employment = r.find('span.employment').text()
        rtn_data['area'] = location
        rtn_data['business'] = business
        rtn_data['company'] = employment
        rtn_data['education'] = education

        desc = r.find('span.description > span.content').text()
        rtn_data['description'] = desc

        follow_items = r.find('div.zm-profile-side-following strong')
        follows = [pq(fi).text() for fi in follow_items]
        follow, fans = follows
        rtn_data['follow_num'] = follow
        rtn_data['fans_num'] = fans

        view = r.find('span.zg-gray-normal > strong').text()
        rtn_data['total_view_num'] = view if view else 0

        topic_items = r.find('div.skilled-topics a.zg-gray-darker')
        topics = [pq(ti).text() for ti in topic_items]
        rtn_data['topic'] = topics

        # 大头像
        big_avatar = r.find('div.body > img.Avatar').attr('src')
        rtn_data['big_avatar'] = big_avatar
        if upload_pic:
            import upload
            # 小头像
            rtn_data['avatar'] = ''
            if rtn_data['big_avatar'].startswith('http'):
                dic_pic = upload.upload(requests.get(rtn_data['big_avatar'], verify=False).content)
                if dic_pic:
                    rtn_data['avatar'] = dic_pic['key']

        return rtn_data


if __name__ == '__main__':
    c = Crawler()
    # https://www.zhihu.com/people/zhang-san-80-26-47
    res = c.crawl_with_url('https://www.zhihu.com/people/chenbailing')
    for i in res:
        if isinstance(res[i], basestring):
            print i, '\t', res[i].encode('u8')
        else:
            print i, '\t', res[i]
