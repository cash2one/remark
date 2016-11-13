# -*- coding:utf-8 -*-

import re
from suds.client import Client 
from urllib import quote

base = "http://211.99.191.148/mms/services/info?wsdl"
client = Client(base) 

secode = 'ZXHD-CRM-0100-WYOYHQ'
passed = '94442324'

dicMsg = {
    'pass':'{{nickname}} 您好，您的广告需求（{{demand_title}}）已通过审核，详情请前往一道自媒体平台查看。',
    'denied':'{{nickname}} 您好，您的广告需求（{{demand_title}}）因为“{{check_info}}”未通过审核，请前往一道自媒体平台重新发布。',
    'take_order': '{{nickname}} 您好，您的广告需求（{{demand_title}}）已有自媒体接单，请前往一道自媒体平台关注接单动态。',
    'apply_change_price': '{{nickname}}您好，您的（{{media_title}} - {{price_name}}）收到改价申请，来自广告需求（{{demand_title}}），请前往一道自媒体平台改价。',
    'already_change_price':'{{nickname}}您好，自媒体（{{media_title}} - {{price_name}}）已改价为（{{price}}），请前往一道自媒体平台查看。',
    'pay': '{{nickname}}您好，您的（{{media_title}}）成功收到下单，来自广告需求（{{demand_title}}），请根据要求完成广告需求，并前往一道自媒体平台反馈。',
    'nopay': '{{nickname}}您好，非常抱歉，您与广告主需求（{{demand_title}}）的投放条件不相符，未被广告主选中，详情请前往一道自媒体平台查看。',
    'feedback': '{{nickname}}您好，您的广告需求（{{demand_title}}）已收到反馈，来自自媒体（{{media_title}}），请前往一道自媒体平台查看。',#反馈
    'feedback_check': '{{nickname}}您好，您的（{{media_title}}）反馈已验收，来自广告需求（{{demand_title}}），交易款项即将结算，请前往一道自媒体平台查看。',#验收
    'complain': '亲爱的{{nickname}}您好，由于您的反馈不符合广告主要求，广告主已向一道平台提出申诉，我们的工作人员会在3个工作日内联系您。详情请前往一道自媒体平台查看。',
    'settlement': '亲爱的{{nickname}}您好，您完成的需求“{{demand_title}}”已经确认结算，详情请前往一道自媒体平台查看。',
    'cancel': '亲爱的{{nickname}}您好，您接单的需求“{{demand_title}}”已撤销，详情请前往一道自媒体平台查看。',

    'verify_phone': '您请求的验证码是: {{verify_code}}'
}

# 处理消息文本
def msg(strKey, dicData):

    if 'demand_id' in dicData.keys():
        dicData['demand_id'] = str(dicData['demand_id'])

    if strKey == 'pass' or strKey == 'take_order':
        dicMap = {
            '{{nickname}}': dicData['nickname'],
            '{{demand_title}}': dicData['demand_title'],
        }

    if strKey == 'apply_change_price':
        dicMap = {
            '{{nickname}}': dicData['nickname'],
            '{{demand_title}}': dicData['demand_title'],
            '{{media_title}}': dicData['media_title'],
            '{{price_name}}': dicData['price_name'],
        }

    if strKey == 'already_change_price':
        dicMap = {
            '{{nickname}}': dicData['nickname'],
            '{{price}}': dicData['price'],
            '{{media_title}}': dicData['media_title'],
            '{{price_name}}': dicData['price_name'],
        }

    if strKey == 'denied':
        dicMap = {
            '{{nickname}}': dicData['nickname'],
            '{{demand_title}}': dicData['demand_title'],
            '{{check_info}}': dicData['check_info']
        }

    if strKey == 'pay':
        dicMap = {
            '{{nickname}}': dicData['nickname'],
            '{{demand_title}}': dicData['demand_title'],
            '{{media_title}}': dicData['media_title']
        }

    if strKey == 'feedback' or strKey == 'feedback_check':
        dicMap = {
            '{{nickname}}': dicData['nickname'],
            '{{demand_title}}': dicData['demand_title'],
            '{{media_title}}': dicData['media_title']
        }

    if strKey == 'nopay'  or strKey == 'settlement':
        dicMap = {
            '{{nickname}}': dicData['nickname'],
            '{{demand_title}}': dicData['demand_title'],
            '{{demand_id}}': dicData['demand_id'],
        }

    if strKey == 'complain':
        dicMap = {
            '{{nickname}}': dicData['nickname'],
            '{{demand_id}}': dicData['demand_id'],
        }

    if strKey == 'cancel':
        dicMap = {
            '{{nickname}}': dicData['nickname'],
            '{{demand_title}}': dicData['demand_title'],
        }

    if strKey == 'verify_phone':
        dicMap = {
            '{{verify_code}}': dicData['verify_code']
        }

    return multiple_replace(dicMsg[strKey], dicMap)


# 替换多个
def multiple_replace(text, adict):
    rx = re.compile('|'.join(map(re.escape, adict)))
    
    def one_xlat(match):
        return adict[match.group(0)]

    return rx.sub(one_xlat, text)


#调用sendSMS发送短讯
def sendsms(phone, strKey, dicData):
    #print 1010101010
    content = msg(strKey, dicData)

    d = dict(in0=secode,
                in1=passed,
                in2=phone,
                in3=quote(content.decode('u8').encode('gbk', "ignore")),
                in4='',
                in5='1',
                in6='',
                in7='1',
                in8='',
                in9='4',)
    ret = client.service.sendSMS(**d)
    print ret
    return ret

#调用getbalance查询余额
def getbalance():
    d = dict(in0=secode,
            in1=passed,)
    ret = client.service.getbalance(**d)
    return ret

def getReport():
    d = dict(in0=secode,
            in1=passed,)
    ret = client.service.getReport(**d)
    return ret
    
if __name__ == '__main__':
    pass
    #print getReport()
    # print getbalance()
    #sendsms('13611089553', '你好帅')
    # pass
    # sendsms('158xxxxxxxx', 'verify_phone', {'verify_code': '特殊字符☞测试'})