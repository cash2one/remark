# -*- coding:utf-8 -*-

import base as base
import api.alipay as alipay

class Pay(base.base):
    """ 支付
    """

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        """ 去付款
        """

        # 需要验证登录
        self.isAuth = True

        # 获取参数
        strDemandId = self.I('demand_id')
        strBank = self.I('bank')
        strHost = self.I('host')

        if not strDemandId or not strBank or not strHost:
            self.redirect('/404')
            return
            
        # 获取数据
        demandService = self.importService('demand')
        dicData = demandService.get_pay_info(strDemandId, self.current_user['user_id'])
        if not dicData:
            self.redirect('/404')
            return

        pay_link = alipay.create_direct_pay_by_user(dicData['trade_code'], strBank, dicData['title'], '', dicData['money'], strHost)
        if not pay_link:
            self.redirect('/405')
            return

        self.redirect(pay_link)


class Return(base.base):
    """ 回调
    """

    def initialize(self):
        
        base.base.initialize(self)

    def index(self):
    
        #dicRequest = self.request.arguments
        #dicData = {}
        #if dicRequest:
        #    for k in dicRequest:
        #        dicData[k] = dicRequest[k][0]
        #        
        #    # 读取订单及支付状态
        #    demandService = self.importService('demand')
        
        self.display('index')


class Notify(base.base):
    """ 异步回调
    """

    def initialize(self):
    
        # 需要验证登录
        # self.isAuth = True
        
        base.base.initialize(self)

    def index(self):
        
        dicRequest = self.request.arguments
        # print dicRequest
        #print 'callback code: {code}'.format(dicRequest['out_trade_no'])
        dicData = {}
        if dicRequest:
            for k in dicRequest:
                dicData[k] = dicRequest[k][0]

        if alipay.notify_verify(dicData) and dicData['trade_status'] == 'TRADE_SUCCESS':
            # 改变订单状态
            strTradeNo = dicData['out_trade_no']
            if not strTradeNo:
                self.out(401)
                return

            # 读取订单及支付状态
            demandService = self.importService('demand')

            intStatus = demandService.pay_check(dicData)
            #print intStatus
            if intStatus == 200:
                self.write('success')



class Wallet(base.base):
    """ 用户钱包
    """
    def initialize(self):

        # 需要验证登录
        self.isAuth = True
        config = {'isDataBase' : True}
        base.base.initialize(self, config)
        self.accountService = self.importService('account')

    def index(self):
        user_id = self.current_user['user_id']
        walletData = self.accountService.get_wallet(user_id)
        self.out(200, '', walletData)

    def getPayOrder(self):
        user_id = self.current_user['user_id']
        payData = self.accountService.get_pay_order(user_id)
        self.out(200, '', payData)