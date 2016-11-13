# -*- coding: utf-8 -*-

import pymongo
import MySQLdb
import requests
import json
import base64
from hashlib import md5

GROUP_ID = 13727
APP_ID = '74ab2a1bie16ee0v156'
APP_KEY = '4ke785ad063312ftf325e22'

DB_HOST = 'rdshf7hicnex6yhgi3h8.mysql.rds.aliyuncs.com'
# dev
DB_USER = 'yidao_dev'
DB_PASS = 'byXPqETUBRcBTPJb'
DB_PROF = 'yidao_profile_dev'

strDbHost = '123.57.29.208'
strDbUser = 'yidao_dev'
strDbPass = 'uvT8IohyxkVSJGbO'
intDbPort = 27018
strDbDefault = 'media'
strDbSrc = 'wechat_src'

db_prof = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_PROF, use_unicode=1, charset='utf8')

# 无帐号密码调用
mg = pymongo.MongoClient(strDbHost, intDbPort)
# 认证调用
if strDbUser:
    mg[strDbDefault].authenticate(strDbUser, strDbPass)

db1 = mg[strDbDefault]
db2 = mg[strDbSrc]
gs1 = db1.wechat
gs2 = db2.gsdata


def findMany(db_obj, tbl_name, str_field, str_cond=''):
    data = None
    cursor = db_obj.cursor()
    if not str_cond:
        sql = 'SELECT {col} FROM {tbl}'.format(col=str_field, tbl=tbl_name)
    else:
        sql = 'SELECT {col} FROM {tbl} WHERE {cond}'.format(col=str_field, tbl=tbl_name, cond=str_cond)
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
    except Exception, e:
        print e
    cursor.close()
    return data


def updateNicknameId(db_obj, data):
    cursor = db_obj.cursor()
    set_str = 'nickname_id = %s'
    cond_str = 'biz = %s'
    sql = 'UPDATE media_wechat SET {s} WHERE {c}'.format(s=set_str, c=cond_str)
    # print sql
    try:
        row = cursor.executemany(sql, data)
        print row
        db_obj.commit()
    except Exception, e:
        print e
        db_obj.rollback()
    cursor.close()


def updateOriginal(db_obj, data):
    cursor = db_obj.cursor()
    set_str = 'original = %s'
    cond_str = 'id = %s'
    sql = 'UPDATE media_wechat SET {s} WHERE {c}'.format(s=set_str, c=cond_str)
    # print sql
    try:
        row = cursor.executemany(sql, data)
        print row
        db_obj.commit()
    except Exception, e:
        print e
        db_obj.rollback()
    cursor.close()


def make_signature(data):
    """
    生成请求签名
    :param data: 请求参数
    :return: 签名
    """
    json_data = json.dumps(data, sort_keys=True, separators=(',', ':')).lower()
    signature = md5(json_data + APP_KEY).hexdigest()
    return signature


def urlsafe_encode(data):
    """
    进行url安全编码
    :param data: 请求参数
    :return: 编码后的请求参数
    """
    # print json.dumps(data)
    # urlsafe_data = base64.urlsafe_b64encode(json.dumps(data))
    urlsafe_data = base64.b64encode(json.dumps(data))
    # print urlsafe_data
    return urlsafe_data


def get_api_data(url, data):
    """
    通过api获取数据
    :param url: api的url
    :param data: 请求参数
    """
    headers = {'Content-Type': 'application/json'}
    # print data
    try:
        data['signature'] = make_signature(data)
        r = requests.post(url, data=urlsafe_encode(data), headers=headers)
        res = r.json()
        ret = res.get('returnData', {})
        if not ret:
            print res.get('errmsg', '').encode('u8')
            return {}
        return ret
    except Exception, e:
        print e
        return {}


def get_content_list(wx_name, nickname_id):
    # 获取文章列表，含原创信息
    url = 'http://open.gsdata.cn/api/wx/opensearchapi/content_list'
    data = {'appid': APP_ID, 'appkey': APP_KEY, 'wx_name': wx_name,
            'start': 0, 'num': 1, 'sortname': 'posttime', 'sort': 'desc', 'nickname_id': nickname_id}
    res = get_api_data(url, data)
    return res.get('items', [{}])


def get_nickname_one(nickname_id):
    # 获取一个公众号资料
    url = 'http://open.gsdata.cn/api/wx/wxapi/nickname_one'
    data = {'id': nickname_id, 'appid': APP_ID, 'appkey': APP_KEY}
    return get_api_data(url, data)


def update_nickname_id(gs_obj):
    lst = []
    s = gs_obj.find({})
    for i in s:
        # print i
        lst.append((i['id'], i['wx_biz']))
        # break
    # print lst
    print 'build nickname_id OK.'
    updateNicknameId(db_prof, lst)


def update_original():
    res = findMany(db_prof, 'media_wechat', 'id, wechat_id, nickname_id')
    lst = []
    for idx, i in enumerate(res):
        original = get_content_list(i[1], i[2])[0].get('copyright', 0)
        if not original:
            continue
        lst.append((original, i[0]))
        # if idx == 5: break
    print 'build original OK.'
    updateOriginal(db_prof, lst)


def add_to_group(url_lst):
    url = 'http://open.gsdata.cn/api/wx/wxapi/add_wx_to_group'
    # print json.dumps(url_lst)
    data = {
        'appid': APP_ID,
        'appkey': APP_KEY,
        'groupid': GROUP_ID,
        'wxJson': json.dumps(url_lst)
    }
    ret = get_api_data(url, data)
    if ret:
        print ret.get('errmsg', '').encode('u8')


def add_job():
    s = gs2.find({})
    i, j = 0, 0
    url_lst = []
    for item in s:
        wx_url = item.get('wx_url')
        if not wx_url:
            continue
        url_lst.append({'wx_url': wx_url})
        j += 1
        if j == 100:
            i += 1
            add_to_group(url_lst)
            print 'add group-100 times:', i
            j = 0
            url_lst = []
    if url_lst:
        add_to_group(url_lst)
        print 'add group-last ok.'

def test(s):
    url_lst = []
    for item in s:
        url_lst.append({'wx_url': item})
    add_to_group(url_lst)

s = ['http://mp.weixin.qq.com/s?__biz=MzA5MTQxNzQwMg==&amp;mid=201227446&amp;idx=1&amp;sn=fa5d632ee15f3cd0484ab456d6f3236c&amp;3rd=MzA3MDU4NTYzMw==&amp;scene=6#rd',
     'http://mp.weixin.qq.com/s?__biz=MjM5MDkxNDI0NA==&mid=208209730&idx=1&sn=cbea7a24c7592dacf3dd81a0dd2ab8b4&scene=4#wechat_redirect',
     'http://mp.weixin.qq.com/s?__biz=MjM5MjQxNzk2NQ==&mid=200233624&idx=1&sn=77fdf31104b131a13b24506fd63a34df&scene=4#wechat_redirect',
     'http://mp.weixin.qq.com/s?__biz=MjM5NDE1MjIyMQ==&mid=203617141&idx=1&sn=30d8df6b2bace0bcd58092476470dc6d&scene=4#wechat_redirect',
     'http://mp.weixin.qq.com/s?__biz=MzA3MDA0MTkwMg==&mid=204859018&idx=1&sn=89111521c2fd7943ad7e25303443760a&scene=4#wechat_redirect'
     ]
# update_nickname_id(gs1)
# update_nickname_id(gs2)
# update_original()
add_job()
# test(s)

mg.close()
db_prof.close()
