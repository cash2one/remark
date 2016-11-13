# -*- coding:utf-8 -*-

import base
import re

class service(base.baseService):
    """ 站内消息
    """

    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)

        self.blogModel = self.importModel('blog')
        self.messageModel = self.importModel('message')

    # def create(self):
    #     """ 生成消息
    #     """
    #     pass
    dicMsg = {
    'reg':'{{nickname}} 您好，欢迎使用一道自媒体平台。现在一道提供自媒体广告交易系统，您可以 <a href = "/user?a=demand_form">发布广告需求</a>，也可以 <a href = "/user?a=media_create">入驻自媒体</a> 接单，如有疑问请联系客服。',
    'pass':'您的广告需求<a href = "/demand?a=view&id={{demand_id}}">{{demand_title}}</a>已通过审核，您可以邀请自媒体接单。',
    'denied':'您的广告需求<a href = "/demand?a=view&id={{demand_id}}">{{demand_title}}</a>因为<strong>“{{check_info}}”</strong>未通过审核，请重新<a href = "/user?a=demand_form">发布广告需求</a>。',
    'take_order': '您的广告需求<a href = "/demand?a=view&id={{demand_id}}">{{demand_title}}</a>已有自媒体接单。',
    'apply_change_price': '您的<strong>{{media_title}} - {{price_name}}</strong>收到改价申请，前往广告需求<a href = "/demand?a=view&id={{demand_id}}">{{demand_title}}</a>改价。',
    'already_change_price':'自媒体<strong>{{media_title}} - {{price_name}}</strong>已改价为{{price}}，查看<a href = "/demand?a=cart&id={{cart_id}}">预选单</a>。',
    'pay': '您的<strong>{{media_title}}</strong>成功收到下单，来自广告需求<a href = "/demand?a=view&id={{demand_id}}">{{demand_title}}</a>，前往查看<a href = "/user?a=demand_order_detail&id={{order_id}}">订单详情<a/>。',
    'nopay': '您接单的广告需求 <a href = "/demand?a=view&id={{demand_id}}">{{demand_title}}</a> 已经投放给其它自媒体，请找寻更适合您的 <a href = "list">广告需求</a>。',
    'feedback': '您已收到自媒体<strong>{{media_title}}</strong> 的反馈，前往查看<a href = "/user?a=demand_order_detail&id={{order_id}}">反馈结果</a>。',#反馈
    'feedback_check': '您的 <strong>{{media_title}}</strong> 提交的反馈已验收，交易款项即将结算，前往查看 <a href = "/user?a=demand_order_detail&id={{order_id}}">订单详情</a> 并给广告主评价.',#验收
    'complain': '广告主对您的 <strong>{{media_title}}</strong> 提交的反馈有异议并已提交申诉，客服将会帮助调解，前往查看 <a href = "/user?a=demand_order_detail&id={{order_id}}">订单申诉</a>。',
    'appeal_done_media':'您的 <strong>{{media_title}}</strong> 收到的申诉已有处理结果，前往查看 <a href = "/user?a=demand_order_detail&id={{order_id}}">申诉结果</a>。',
    'appeal_done':'您对 <strong>{{media_title}}</strong> 提交的申诉已有处理结果，前往查看 <a href = "/user?a=demand_order_detail&id={{order_id}}">申诉结果</a>。',
    'demand_cancel':'您接单的广告需求 <a href = "/demand?a=view&id={{demand_id}}">{{demand_title}}</a> 已被广告主撤销，请找寻其它 广告需求。',
    'demand_expire':'您的广告需求 <a href = "/demand?a=view&id={{demand_id}}">{{demand_title}}</a> 即将过期，已有 {{take_order_num}} 个自媒体接单。',
    'demand_expire_media':'您接单的广告需求 <a href = "/demand?a=view&id={{demand_id}}">{{demand_title}}</a> 已过期，请找寻其它 广告需求',
    'settlement': '亲爱的{{nickname}}您好，您完成的需求“<a href = "/demand?a=view&id={{demand_id}}">{{demand_title}}</a>”已经确认结算，详情请前往一道自媒体平台查看。',
    'invite':'您的 {{media_title}} 收到广告需求 <a href = "/demand?a=view&id={{demand_id}}">{{demand_title}}</a> 的接单邀请。',
    }

    def msg(self,strKey,dicData):
        if strKey == 'demand_expire':
            dicMap = {
                '{{demand_id}}': dicData['demand_id'],
                '{{demand_title}}': dicData['demand_title'],
                '{{take_order_num}}': dicData['take_order_num'],
            }

        if strKey == 'pass' or strKey == 'take_order' or strKey == 'demand_expire_media' or strKey == 'demand_cancel':
            dicMap = {
                '{{demand_title}}': dicData['demand_title'],
                '{{demand_id}}': dicData['demand_id'],
            }

        if strKey == 'apply_change_price':
            dicMap = {
                '{{demand_id}}': dicData['demand_id'],
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
                '{{cart_id}}': dicData['cart_id'],
            }

        if strKey == 'denied':
            dicMap = {
                '{{demand_id}}': dicData['demand_id'],
                '{{demand_title}}': dicData['demand_title'],
                '{{check_info}}': dicData['check_info']
            }

        if strKey == 'feedback' or strKey == 'feedback_check' or strKey == 'complain' or strKey == 'appeal_done' or strKey == 'appeal_done_media':
            dicMap = {
                '{{order_id}}': dicData['order_id'],
                '{{media_title}}': dicData['media_title']
            }
        if strKey == 'pay':
            dicMap = {
                '{{demand_title}}': dicData['demand_title'],
                '{{media_title}}': dicData['media_title'],
                '{{demand_id}}': dicData['demand_id'],
                '{{order_id}}': dicData['order_id'],
            }

        if strKey == 'nopay'  :
            dicMap = {

                '{{demand_title}}': dicData['demand_title'],
                '{{demand_id}}': dicData['demand_id'],
            }

        if strKey == 'reg':
            dicMap = {
                '{{nickname}}': dicData['nickname'],

            }
        if strKey == 'settlement':
            dicMap = {
                '{{nickname}}': dicData['nickname'],
                '{{demand_title}}': dicData['demand_title'],
                '{{demand_id}}': dicData['demand_id'],
            }



        return self.multiple_replace(self.dicMsg[strKey], dicMap)


# 替换多个
    def multiple_replace(self,text, adict):
        rx = re.compile('|'.join(map(re.escape, adict)))

        def one_xlat(match):
            return adict[match.group(0)]

        return rx.sub(one_xlat, text)
    def send_message(self,userId,strKey,dicDate):
        #print 10
        content = self.msg(strKey,dicDate)
        #print content
        self.messageModel.insert({
            'key': 'user_id,type, info, status, create_time',
                'val': '\'{uId}\', \'{type}\', \'{info}\',{status}, {time}'.format(
                    uId=userId, type=0, info=content, status=1, time=int(self.time.time())
                )
            })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}
