# coding: utf-8

import json
import requests

api_user = 'Range_test_EHg7ic'
api_key = 'YfIUV5UIhAmC5zyq'
default_from = 'hello@mail.yidao.info'
#SENDCLOUD_API = 'http://sendcloud.sohu.com/webapi/mail.send.json'
SENDCLOUD_API = 'http://sendcloud.sohu.com/webapi/mail.send_template.json'

def send_mail(to, subject, content, from_=default_from, **kwargs):
    params = {
        'api_user': api_user,
        'api_key': api_key,
        'from': from_,
        'to': to,
        'subject': subject,
        'html': content,
    }
    params.update(kwargs)
    resp = requests.post(SENDCLOUD_API, params)
    return resp.json()['message'] == 'success'

def send_template_mail(subject, from_ = default_from, **kwargs):
    params = {
        'api_user': api_user,
        'api_key': api_key,
        'from': from_,
        'subject': subject
    }
    params.update(kwargs)
    resp = requests.post(SENDCLOUD_API, params)
    return resp.json()['message'] == 'success'

if __name__ == '__main__':
    # http://sendcloud.sohu.com/webapi/template.get.json?api_user=Range_test_EHg7ic&api_key=YfIUV5UIhAmC5zyq
    # 内容只能根据模板一样才能发送
    pass
    

