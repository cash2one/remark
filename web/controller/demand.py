# -*- coding:utf-8 -*-

import base as base

# 需求
class demand(base.base):

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)
        
        # 引用Service
        self.demandService = self.importService('demand')
        self.userService = self.importService('user')

    # 列表
    def index(self):
        self.display('index')

    # 详情
    def view(self):
        # 获取参数
        strDemandId = self.I('id')
        if not strDemandId:
            self.redirect('/404')

        # 读取数据
        dicDemand = self.demandService.detail(strDemandId)
        if not dicDemand:
            self.redirect('/405')
            return

        # 是否广告主
        booIsMaster = False
        #print dicDemand
        strUserId = self.current_user['user_id']

        print self.formatTime(int(self.time.time()), '%Y%m%d')
        # 是不是广告主
        booIsMaster = True if strUserId == int(dicDemand['user_id']) else False
        
        if booIsMaster:
            self.demandMasterList(dicDemand)
        else:
            self.demandCustomerList(dicDemand)

    def demandMasterList(self, dicDemand):
        """ 广告主查看需求详情时的处理
        """
        
        # 已接单列表 
        tupDemandTakeOrder = self.demandService.demand_take_order(dicDemand['id'])

        #print dicDemand


        #print dicDemand
        self.dicViewData['demand'] = dicDemand
        self.dicViewData['take_order'] = tupDemandTakeOrder
        self.dicViewData['RECO_HOST'] = self.dicConfig['RECO_HOST']

        self.display('view_master')

    def demandCustomerList(self, dicDemand):
        """ 自媒体或游客查看需求详情时的处理
        """
        # 我的自媒体数
        strUserId = self.current_user['user_id']

        strDemandId = self.I('id')
        mediaService = self.importService('media')
        userService = self.importService('user')
        mediaNum = mediaService.user_media_num(strUserId)
        custom_media_info = self.demandService.custom_media(strDemandId, strUserId)
        #print custom_media_info
        dic_user = self.userService.get_user_detail(strUserId)
        if dicDemand['status'] == 1:
            self.redirect('/')
        else:
            self.dicViewData['user'] = dic_user
            self.dicViewData['demand'] = dicDemand
            self.dicViewData['media_num'] = mediaNum
            self.dicViewData['media'] = custom_media_info
            self.dicViewData['RECO_HOST'] = self.dicConfig['RECO_HOST']
            self.display('view_customer')

    def get_media_owner(self):
        """ 广告主查看时，获取自媒体信息
        """

        strDemandId = self.I('id')

        # 检查是否广告主
        dicDemand = self.demandService.detail(strDemandId)
        if dicDemand['user_id'] != self.current_user['user_id']:
            self.out(602)
            return

        self.out(200)


    # 接单
    def take_order(self):
        if not self.current_user['user_id']:
            self.redirect('/login')
            return

        str_demand_id = self.I('id')
        if not str_demand_id:
            self.redirect('/404')

        user_service = self.importService('user')
        dicUser = user_service.get_user(self.current_user['user_id'])
        if not dicUser:
            self.redirect('/404')
            
        # 我的自媒体接单列表
        demand_service = self.importService('demand')
        tup_take_order_media, untake_count = demand_service.take_order_media(self.current_user['user_id'], str_demand_id)
        #for item in tup_take_order_media:
        #    if item['status']==-1:
        #        self.redirect('/demand?a=view&id='+str_demand_id)
        self.dicViewData['demand_id'] = str_demand_id
        self.dicViewData['phone'] = dicUser['phone']
        self.dicViewData['take_order_media'] = tup_take_order_media
        self.dicViewData['untake_count'] = untake_count

        self.display('take_order')

    # 接单提交
    def take_order_submit(self):
        if not self.current_user['user_id']:
            self.redirect('/login')
            return

        str_demand_id = self.I('demand_id')
        if not str_demand_id:
            self.redirect('/404')
        
        str_media_id = self.I('media_id')
        if not str_media_id:
            self.redirect('/404')
        
        str_phone = self.I('phone')
        if not str_phone:
            self.redirect('/404')
        
        # 我的自媒体
        demand_service = self.importService('demand')
        demand_service.take_order(self.current_user['user_id'], str_demand_id, str_media_id, str_phone)
        self.out(demand_service.status)

    # 取消接单
    def take_order_cancel(self):
        if not self.current_user['user_id']:
            self.redirect('/login')
            return

        str_demand_id = self.I('demand_id')
        if not str_demand_id:
            self.redirect('/404')
        
        str_media_id = self.I('media_id')
        if not str_media_id:
            self.redirect('/404')
        
        m_user_id = self.current_user['user_id']
        self.demandService.take_order_cancel(m_user_id, str_demand_id, str_media_id)
        self.out(self.demandService.status)

    # # 创建支付信息
    # def pay_create(self):
    #
    #     # 需要验证登录
    #     self.isAuth = True
    #
    #     # 获取参数
    #     strData = self.I('data')
    #
    #     dicResult = self.demandService.pay_create(strData, self.current_user['user_id'])
    #     self.out(dicResult['status'], '', {
    #         'demand_id': dicResult['demand_id']
    #     })

    def pay(self):
        """ 确认支付
        """

        # 需要验证登录
        self.isAuth = True

        # 获取参数
        strDemandId = self.I('demand_id')
        strData = self.I('cart_data')
        # 获取数据
        dicResp = self.demandService.pay(strData, self.current_user['user_id'])
        intStatus = dicResp['status']
        if intStatus == 200:
            dicResp['data']['demand_id'] = strDemandId
            self.dicViewData['pay'] = dicResp['data']
            self.display('pay')

    # def pay(self):
    #     """ 确认支付
    #     """
    #
    #     # 需要验证登录
    #     self.isAuth = True
    #
    #     # 获取参数
    #     strId = self.I('id')
    #
    #     # 获取数据
    #     dicData = self.demandService.pay(strId, self.current_user['user_id'])
    #
    #     self.dicViewData['pay'] = dicData
    #
    #     self.display('pay')

    def cart(self):
        """ 预选单
        """
        strDemandId = self.I('id')
        strUserId = str(self.current_user['user_id'])
        dicDemand, tupData = self.demandService.cart(strDemandId, strUserId)
        lisDemandOrderData = []
        if tupData:
            lisMediaPriceId = list(set([str(i['media_price_id']) for i in tupData]))
            # 额外的刊例信息
            tupMediaPrice = self.importService('media').media_attr_value_info(lisMediaPriceId)
            dicMediaPrice = {i['media_price_id']: (' + '.join(i['attr_value_info'].values()), i['price'])
                             for i in tupMediaPrice}
            for i in tupData:
                # print i
                # 改价前默认刊例报价
                # i['price'] = 9999999
                if i['status'] != 2 :
                    dic_price = dicMediaPrice.get(i['media_price_id'], {})
                    if dic_price:
                        i['price'] = int(dic_price[1])
                i['media_attr_value'] = ''
                i['media_attr_value'] = ''
                dic_media_attr_value = dicMediaPrice.get(i['media_price_id'], {})
                if dic_media_attr_value:
                    i['media_attr_value'] = dic_media_attr_value[0]
                i['avatar'] = self.getAvatarUrl(i['avatar'])
                lisDemandOrderData.append(i)
        self.dicViewData['cart'] = lisDemandOrderData
        # print lisDemandOrderData
        self.dicViewData['demand_detail'] = dicDemand
        self.dicViewData['total_price'] = int(sum([i['price'] for i in lisDemandOrderData]))
        self.display('cart')

    def cart_create(self):
        """ 预选单
        """
        str_ad_user_id      = self.current_user['user_id']
        str_demand_id       = self.I('id')
        str_m_user_id       = self.I('user_id')
        str_media_id        = self.I('media_id')
        str_media_price_id  = self.I('price_id')
        str_price           = self.I('price')

        self.demandService.cart_create(str_ad_user_id, str_demand_id, str_m_user_id, str_media_id, str_media_price_id, str_price)
        self.out(self.demandService.status)

    def cart_update(self):
        strCartId = self.I('cart_id')
        strPrice = self.I('price')
        if strPrice:
            strPrice =int(strPrice)
        # print strPrice
        intStatus = self.demandService.cart_update({'cart_id':strCartId, 'price': strPrice})
        self.out(intStatus)

    def cart_delete(self):
        strCartId = self.I('cart_id')
        intStatus = self.demandService.cart_delete(strCartId)
        self.out(intStatus)

    def feedback_create(self):
        """ 自媒体提交反馈
        """
        
        # 需要验证登录
        self.isAuth = True

        if not self._POST:
            self.out(501)
            return

        # 获取参数
        strJiedanId = self.I('jiedan_id')
        strFeedbackUrl = self.I('feedback_url')

        if not strJiedanId or not strFeedbackUrl:
            self.out(401)
            return

        # 加载爬虫
        import api.crawler as crawler
        dicData = crawler.crawler().feedback(strFeedbackUrl)

        # 读取接单信息
        dicStatus = self.demandService.feedback_create(strJiedanId, dicData, self.current_user['user_id'])

        self.out(dicStatus['status'])

    def feedback_check(self):
        """ 反馈验收
        """
        
        # 需要验证登录
        self.isAuth = True

        if not self._POST:
            self.out(501)
            return

        # 获取参数
        strId = self.I('id')

        if not strId:
            self.out(401)
            return

        # 验证是否是广告主：
        dicFeedback = self.demandService.demand_feedback_one_id(strId)
        if dicFeedback['user_id'] != self.current_user['user_id']:
            self.out(603)
            return

        # 验证通过，修改反馈状态与订单状态
        intStatus = self.demandService.demand_feedback_update_status(strId, dicFeedback['demand_id'])
        self.out(intStatus)

    def cancel(self):
        """ 取消需求
        """

        # 验证登录
        self.isAuth = True

        # 获取参数
        strDemandId = self.I('id')

        # 加载Service执行取消
        intStatus = self.demandService.cancel(strDemandId, self.current_user['user_id'])
        #self.out(intStatus)
        self.redirect('/demand?a=view&id='+str(strDemandId))
        return
    
    def demand_monitor(self):
        """ 轮循状态
        """

        strDemandId = self.I('demand_id')
        strJiedanNum = self.I('jiedan_num')
        strStatus = self.I('status')

        if not strDemandId:
            self.out(401)

        dicDemand = self.demandService.detail(strDemandId)
        if not dicDemand:
            self.out(601)

        tupDemandJiedan = self.demandService.demand_take_order(strDemandId)

        intJiedanNum = len(tupDemandJiedan)

        if int(strStatus) != dicDemand['status'] or int(strJiedanNum) != intJiedanNum:
            self.out(201)
 