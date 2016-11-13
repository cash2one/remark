# -*- coding: utf-8 -*-

import requests
import json
import xml.etree.ElementTree as ET
import WXBizMsgCrypt as wxMsg
import upload

COMPONENT_APP_ID = 'wx7610ffd2573875a6'
COMPONENT_APP_SECRET = '2c02a99c9fba39a290fc40e674885447'
MESSAGE_TOKEN = 'OnEzZGlw26wGt3cz'
ENCODING_AES_KEY = 'ijVKaBrf1y9LzQGQEI9I8ze3bSRyYmNa9WR9waV88OE'


def get_component_access_token(strTicket):
    # 1.获取第三方平台access_token
    url = 'https://api.weixin.qq.com/cgi-bin/component/api_component_token'
    r = requests.post(url=url,
                      data=json.dumps({
                          "component_appid": COMPONENT_APP_ID,
                          "component_appsecret": COMPONENT_APP_SECRET,
                          "component_verify_ticket": strTicket
                      }),
                      headers={'content-type': 'application/json'})
    data = r.json()
    if 'errcode' in data:
        print data
    return data

def get_pre_auth_code(component_access_token):
    # 2.获取预授权码
    url = 'https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode?component_access_token={tk}'.format(
        tk=component_access_token
    )
    r = requests.post(url=url,
                      data=json.dumps({"component_appid": COMPONENT_APP_ID}),
                      headers={'content-type': 'application/json'})
    data = r.json()
    # print data
    return data

def get_authorization_info(component_access_token, authorization_code):
    # 3.使用授权码换取公众号的授权信息
    url = 'https://api.weixin.qq.com/cgi-bin/component/api_query_auth?component_access_token={tk}'.format(
        tk=component_access_token
    )
    r = requests.post(url=url,
                      data=json.dumps({
                          "component_appid": COMPONENT_APP_ID,
                          "authorization_code": authorization_code
                      }),
                      headers={'content-type': 'application/json'})
    data = r.json()
    # print data
    return data

def get_authorizer_token(component_access_token, authorizer_appid, authorizer_refresh_token):
    # 4.获取（刷新）授权公众号的令牌
    url = 'https://api.weixin.qq.com/cgi-bin/component/api_query_auth?component_access_token={tk}'.format(
        tk=component_access_token
    )
    r = requests.post(url=url,
                      data=json.dumps({
                          "component_appid": COMPONENT_APP_ID,
                          "authorizer_appid": authorizer_appid,
                          "authorizer_refresh_token": authorizer_refresh_token,
                      }),
                      headers={'content-type': 'application/json'})
    data = r.json()
    # print data
    return data

def get_authorizer_info(component_access_token, authorizer_appid):
    # 5.获取授权方的账户信息
    url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info?component_access_token={tk}'.format(
        tk=component_access_token
    )
    r = requests.post(url=url,
                      data=json.dumps({
                          "component_appid": COMPONENT_APP_ID,
                          "authorizer_appid": authorizer_appid
                      }),
                      headers={'content-type': 'application/json'})
    data = r.json()
    # print data
    return data


def get_login_url(pre_auth_code, redirect_uri):
    url = 'https://mp.weixin.qq.com/cgi-bin/componentloginpage?component_appid={caid}' \
          '&pre_auth_code={pac}&redirect_uri={ru}'.format(caid=COMPONENT_APP_ID, pac=pre_auth_code, ru=redirect_uri)
    return url


def sha1(timestamp, nonce, encrypt):
    return wxMsg.SHA1().getSHA1(MESSAGE_TOKEN, timestamp, nonce, encrypt)[1]


def get_component_verify_ticket(encrypt_xml):
    strEncrypt = ET.fromstring(encrypt_xml).find("Encrypt").text
    # print strEncrypt
    pc = wxMsg.Prpcrypt(ENCODING_AES_KEY)
    status, decrypt_xml = pc.decrypt(strEncrypt, COMPONENT_APP_ID)
    # print status, decrypt_xml
    strTicket = ET.fromstring(decrypt_xml).find("ComponentVerifyTicket").text
    return strTicket


def get_news_url(access_token):
    # 文档 http://mp.weixin.qq.com/wiki/12/2108cd7aafff7f388f41f37efa710204.html
    url = 'https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={tk}'.format(tk=access_token)
    r = requests.post(url=url,
                      data=json.dumps({
                          "type": "news",
                          "offset": 0,
                          "count": 1
                      }),
                      headers={'content-type': 'application/json'})
    data = r.json()
    # print data
    item = data.get('item')
    if item is not None:
        return item[0].get('content', {}).get('news_item', [{}])[0].get('url')
    return ''

def get_ip(access_token):
    url = 'https://api.weixin.qq.com/cgi-bin/getcallbackip?access_token={tk}'.format(tk=access_token)
    r = requests.get(url)
    data = r.json()
    # print data
    return data

def get_biz(link):
    if not link:
        return ''
    return link[link.index('__biz=') + len('__biz='): link.index('&')]


def get_qrcode(biz):
    if not biz:
        return ''
    str_qrcode = 'http://mp.weixin.qq.com/mp/qrcode?scene=10000005&size=102&__biz=%s' % biz
    dicPic =  upload.upload(requests.get(str_qrcode).content)
    if dicPic:
        return dicPic['key']
    return ''

def get_avatar(head_img):
    if not head_img:
        return ''
    dicPic =  upload.upload(requests.get(head_img).content)
    print dicPic
    if dicPic:
        return dicPic['key']
    return ''


def test():
    pass
    # decrypt = wxMsg.WXBizMsgCrypt('OnEzZGlw26wGt3cz',
    #                               'ijVKaBrf1y9LzQGQEI9I8ze3bSRyYmNa9WR9waV88OE',
    #                               'wx7610ffd2573875a6')
    # ret, decryp_xml = decrypt.DecryptMsg(from_xml, msg_signature, timestamp, nonce)
    # print ret, decryp_xml
    # xml_obj = ET.fromstring(decryp_xml)
    # strToUserName = xml_obj.find('ToUserName').text
    # strFromUserName = xml_obj.find('FromUserName').text
    # strCreateTime = xml_obj.find('CreateTime').text
    # strMsgType = xml_obj.find('MsgType').text
    # strContent = xml_obj.find('Content').text
    # strMsgId = xml_obj.find('MsgId').text
    # print strToUserName
    # print strFromUserName
    # print strCreateTime
    # print strMsgType
    # print strContent
    # print strMsgId
