# -*- coding:utf-8 -*-

import base as base
from api import wechat
from api import crawler
import time
import json

# 用户
class User(base.base):

    isAuth = True

    userService = {}

    def initialize(self):

        self.isAuth = True

        config = {'isDataBase' : True}
        base.base.initialize(self, config)

        self.userService = self.importService('user')

    def index(self):
        """ 基本信息
        """

        strMyMenu = 'information'

        # 读取用户信息
        dicUser = self.userService.get_user_basic(self.current_user['user_id'])
        if not dicUser:
            self.redirect('/404')
            return

        if self._POST:
            # 获取参数
            strNickname = self.I('name')
            strCityId = self.I('city_id')
            strProvince = self.I('province')
            strCity = self.I('city')
            strCounty = self.I('county')

            if not strNickname or not strProvince or not strCity or not strCounty or not strCityId:
                self.out(401)

            # 写数据
            dicData = {
                'user_id': self.current_user['user_id'],
                'nickname': strNickname,
                'city_id': strCityId
            }
            intStatus = self.userService.updateUser(dicData)

            # 写cookie
            self.set_secure_cookie("user_nickname", strNickname)

        self.dicViewData['my_menu_focus'] = strMyMenu
        self.dicViewData['user'] = dicUser

        self.display('index')

    def avatar(self):
        """ 上传头像
        """

        if not self._POST:
            self.redirect('/402')
            return

        strFile = self.request.files['avatar']

        import api.upload as upload

        strAvatarUrl = upload.upload(strFile[0]['body'])

        # 保存头像
        intStatus = self.userService.updateUser({
            'user_id': self.current_user['user_id'],
            'avatar': strAvatarUrl['key']
        })
        if intStatus == 200:
            self.set_secure_cookie("user_avatar", strAvatarUrl['key'])
            self.redirect('/user')
            return
        else:
            self.redirect('/500')
            return

    def upload_content(self):
        """ 上传文案
        """

        if not self._POST:
            self.out(404)
            return

        try:
            file_meta = self.request.files['content_file'][0]
            filename = file_meta['filename'].encode('utf-8')
            # 使用配置又不加到config？ 2015-11-10 fix
            path = self.dicConfig['UPLOAD_PATH'] + "/static/data/" + filename
            #有些文件需要已二进制的形式存储，实际中可以更改
            with open(path,'wb') as up:
                up.write(file_meta['body'])
            self.out(200, dicData={'doc_path': "/static/data/" + filename})
        except Exception, e:
            print e
            self.out(500)


    def bind(self):
        """ 绑定
        """

        strMyMenu = 'bind'

        dicUser = self.userService.get_user_and_wechat(self.current_user['user_id'])

        self.dicViewData['my_menu_focus'] = strMyMenu
        self.dicViewData['bind_email'] = dicUser['email'] if dicUser['email'] else ''
        self.dicViewData['bind_wechat'] = dicUser['wechat_nickname'] if dicUser['openid'] else ''
        self.dicViewData['bind_phone'] = dicUser['phone'] if dicUser['phone'] else ''

        self.display('bind');

    def overdue_msg(self):
        if self._POST:
            ids = self.request.arguments
            self.importService('demand').overdue_msg(ids)

    def unbind_wechat(self):
        """ 解绑微信
        """

        intStatus = self.userService.unbind_wechat(self.current_user['user_id'])

        self.out(intStatus)

    def bind_phone_vcode(self):
        """ 绑定手机，发送验证码
        """

        strPhone = self.I('phone')

        if not strPhone:
            self.out(401)
            return

        # 生成验证码
        strVcode = self.salt(6, True)
        # 记录cookie
        self.set_secure_cookie("verify_code", '%s--%s' % (strPhone, strVcode))

        import api.sms as sms
        sms.sendsms(strPhone, 'verify_phone', {
            'verify_code': strVcode
        })

    def bind_phone(self):
        """ 绑定手机
        """

        strPhone = self.I('phone')
        strVcode = self.I('verify_code')

        if not strPhone or not strVcode:
            self.out(401)
            return

        # 读取cookie
        strCookieVcode = self.get_secure_cookie('verify_code')
        strInput = '%s--%s' % (strPhone, strVcode)
        # 验证
        if strCookieVcode != strInput:
            self.out(601)
            return

        # 更新用户数据
        intStatus = self.importService('account').update_account_by_phone(self.current_user['user_id'], strPhone)

        if intStatus == 200:
            self.set_secure_cookie('verify_code', '')
        self.out(intStatus)

    def bind_email(self):
        """ 绑定邮箱
        """

        strMyMenu = 'bind_email'

        self.accountService = self.importService('account')
        if self._POST:
            strEmail = self.I('email')
            strPassword = self.I('password')
            strUserId = str(self.current_user['user_id'])

            if not strEmail or not strPassword or not strUserId:
                self.out(401)
                return

            intStatus = self.accountService.bind_email(strUserId, strEmail, strPassword)
            # print intStatus
            self.out(intStatus)
            return

        self.dicViewData['my_menu_focus'] = strMyMenu

        self.display('bind_email')

    def change_email(self):
        self.accountService = self.importService('account')
        strUserId = self.I('uid')
        strDeadLine = self.I('deadline')
        strEmail = self.I('email')
        strCode = self.I('code')
        strCookieUserId = self.get_secure_cookie("user_id")
        if strUserId != strCookieUserId:
            self.redirect('/user?a=bind_email')
            return
        intStatus = self.accountService.change_email(strUserId, strDeadLine, strEmail, strCode)
        if intStatus == 200:
            self.redirect('/user?a=bind')
        else:
            self.redirect('/user?a=bind_email')

    def password(self):
        """ 修改密码
        """

        strMyMenu = 'password'

        self.dicViewData['my_menu_focus'] = strMyMenu

        self.display('password')



    def notification(self):
        """ 通知中心
        """
        user_id = self.current_user['user_id']
        #print user_id
        strMyMenu = 'notification'
        tupallMsg = self.importService('user').notification(user_id)
        tupshowMsg = self.importService('user').show_notification(user_id)
        #print tupMsg
        self.dicViewData['my_menu_focus'] = strMyMenu
        self.dicViewData['allMsg'] = tupallMsg
        self.dicViewData['showMsg'] = tupshowMsg
        self.display('notification')

    def update_notification(self):
        user_id = self.current_user['user_id']
        if self._POST:
            args = self.request.arguments
            postdata = {
                'id' : self.I('id[]')
            }
            #print args
            #print postdata
            self.userService.update_notification(user_id,postdata)

    def index_msg(self):
        user_id = self.current_user['user_id']
        # if self._POST :
        #     tup_msg = self.userService.index_msg('user_id')
        #     msg = json.dumps(tup_msg)
        #     callback = '%s(%s)' % (self.I('callback'), msg)
        #     self.write(callback)
        # else:
        #     return

        tup_msg = self.userService.index_msg(user_id)
        dic_msg ={}
        for i,item in enumerate(tup_msg):
            dic_msg[i] = item
        #print tup_msg
        if tup_msg:
            self.out(self.userService.status, '', dic_msg)
        else:
            self.out(self.userService.status)

    def update_index_msg(self):
        user_id = self.current_user['user_id']
        self.userService.update_index_msg(user_id)

    def demand(self):

        strMyMenu = 'demand'

        # 获取参数
        strPage = self.I('page')
        intPage = int(strPage) if strPage else 1
        strStatus = self.I('status', '0')
        dicRequestData = {
            'page': intPage,
            'status': int(strStatus),
            'user_id': self.current_user['user_id']
        }

        # 加载Service
        demandService = self.importService('demand')
        tupDemand = demandService.myDemand(dicRequestData)

        # 获取用户信息及城市信息
        dicUser = self.userService.getOneAndCity(self.current_user['user_id'])

        #
        self.dicViewData['my_menu_focus'] = strMyMenu
        self.dicViewData['demand'] = tupDemand[0]
        self.dicViewData['page'] = self.page(intPage, 20, tupDemand[1], '/user?a=demand')
        self.dicViewData['user'] = dicUser
        self.dicViewData['status'] = strStatus

        self.display('demand')

    def demand_online(self):
        """ 在线可接单需求
        """

        # 加载Service
        demandService = self.importService('demand')
        tupDemand = demandService.demand_online(self.current_user['user_id'])
        self.out(200, '', tupDemand)

    def demand_take_order(self):
        """ 我的接单
        """

        strMyMenu = 'demand_take_order'

        # 获取参数
        strPage = self.I('page')
        intPage = int(strPage) if strPage else 1
        # 接单状态
        strStatus = self.I('status', '0')
        intStatus = int(strStatus)
        # 需求状态
        strDemandStatus = self.I('demand_status', '-1')
        intDemandStatus = int(strDemandStatus)
        # 接单自媒体所属用户
        tupDemandTakeOrder = self.importService('demand').demand_take_order_user_id(self.current_user['user_id'], strStatus)
        lisDemandId = [str(i['demand_id']) for i in tupDemandTakeOrder]
        demandData, demandPage = [], 1
        if lisDemandId:
            dicRequestData = {
                'page': intPage,
                'status': intDemandStatus,
                'demand_id': lisDemandId,
            }

            # 加载Service
            demandService = self.importService('demand')
            tupDemand = demandService.myDemand(dicRequestData)
            demandData, demandPage = tupDemand
        # 获取用户信息及城市信息
        dicUser = self.userService.getOneAndCity(self.current_user['user_id'])

        #
        self.dicViewData['my_menu_focus'] = strMyMenu
        self.dicViewData['demand'] = demandData
        self.dicViewData['page'] = self.page(intPage, 20, demandPage, '/user?a=demand_take_order')
        self.dicViewData['user'] = dicUser
        self.dicViewData['status'] = strStatus
        self.dicViewData['demand_status'] = strDemandStatus
        # print demandData
        self.display('demand_take_order')


    def demand_feedback(self):
        strMyMenu = 'demand_feedback'
        self.dicViewData['my_menu_focus'] = strMyMenu

        self.display('demand_feedback')

    def demand_order(self):
        strMyMenu = 'demand_order'
        # 获取参数
        strPage = self.I('page')
        intPage = int(strPage) if strPage else 1
        # 订单状态
        strStatus = self.I('status', '0')
        intStatus = int(strStatus)
        # 需求状态
        strDemandStatus = self.I('demand_status', '-1')
        intDemandStatus = int(strDemandStatus)

        dicArgs = {'status': intStatus, 'page': intPage, 'user_id': self.current_user['user_id']}
        tupData, rows = self.importService('demand').demand_order(dicArgs)
        lisDemandOrderData = []
        if tupData:
            lisDemandId = list(set([str(i['demand_id']) for i in tupData]))
            lisMediaId = list(set([str(i['media_id']) for i in tupData]))
            lisMediaPriceId = list(set([str(i['media_price_id']) for i in tupData]))

            # 额外的需求信息
            tupDemand = self.importService('demand').demand({'status': intDemandStatus, 'demand_id': lisDemandId})
            dicDemand = {i['demand_id']: i for i in tupDemand}
            # 额外的自媒体信息
            tupMedia = self.importService('media').media_simple(lisMediaId)
            dicMedia = {i['media_id']: i for i in tupMedia}
            # 额外的刊例信息
            tupMediaPrice = self.importService('media').media_attr_value_info(lisMediaPriceId)
            dicMediaPrice = {i['media_price_id']: ' + '.join(i['attr_value_info'].values())
                             for i in tupMediaPrice}
            for i in tupData:
                i['media_attr_value'] = dicMediaPrice.get(i['media_price_id'], {})
                i['media_detail'] = dicMedia.get(i['media_id'], {})
                i['demand_detail'] = dicDemand.get(i['demand_id'], {})
                if i['demand_detail']:  ## 需求单撤销就找不到信息，有bug，需要修改
                    lisDemandOrderData.append(i)
        # 获取用户信息及城市信息
        dicUser = self.userService.getOneAndCity(self.current_user['user_id'])

        self.dicViewData['my_menu_focus'] = strMyMenu
        self.dicViewData['demand_order'] = lisDemandOrderData
        self.dicViewData['page'] = self.page(intPage, 20, rows, '/user?a=demand_order')
        self.dicViewData['user'] = dicUser
        self.dicViewData['status'] = strStatus

        self.display('demand_order')

    def demand_order_detail(self):
        strDemandOrderId = self.I('id')
        # 获取用户信息及城市信息
        dicUser = self.userService.getOneAndCity(self.current_user['user_id'])
        dicOrderDetail = self.importService('demand').demand_order_detail(strDemandOrderId)

        strDemandId = str(dicOrderDetail['demand_id'])
        strMediaId = str(dicOrderDetail['media_id'])
        strMediaPriceId = str(dicOrderDetail['media_price_id'])

        lisDemand = self.importService('demand').demand({'status': -1, 'demand_id': [strDemandId]})
        dicDemand = {} if not lisDemand else lisDemand[0]

        lisMedia = self.importService('media').media_simple(strMediaId)
        dicMedia = {} if not lisMedia else lisMedia[0]

        lisMediaPrice = self.importService('media').media_attr_value_info(strMediaPriceId)
        dicMediaPrice = {} if not lisMediaPrice else ' + '.join(lisMediaPrice[0]['attr_value_info'].values())

        dicAppeal = self.importService('demand').order_appeal_detail(strDemandOrderId)
        dic_demand_feedback_detail = self.importService('demand').demand_feedback_detail(strDemandOrderId)

        self.dicViewData['order_detail'] = dicOrderDetail
        self.dicViewData['demand_detail'] = dicDemand
        self.dicViewData['media_detail'] = dicMedia
        self.dicViewData['media_attr_value'] = dicMediaPrice
        self.dicViewData['feedback_detail'] = dic_demand_feedback_detail
        self.dicViewData['appeal_detail'] = dicAppeal
        self.dicViewData['user'] = dicUser
        self.dicViewData['is_ad_user'] = True if self.current_user['user_id'] == dicOrderDetail['ad_user_id'] else False
        self.display('demand_order_detail')

    def upload_feedback(self):
        try:
            strFile = self.request.files['feedback_pic']
            strIdx = self.request.arguments['idx'][0][-1]
        except Exception, e:
            print e
            self.out(401)
            return
        from api.upload import upload
        dicLogo = upload(strFile[0]['body'])

        strKey = dicLogo['key']
        strUrl = '%s%s%s' % (self.dicConfig['PIC']['HOST'], strKey, '-feedback')
        self.out(200, dicData={'idx': strIdx, 'key': strKey, 'url': strUrl})


    def feedback_submit(self):
        strUserId = self.current_user['user_id']
        dicResp = self.feedback_crawl(self.I('link'))
        if not dicResp['title'] or not dicResp['publish_time']:
            self.out(401)
            return
        dicData = {
            'user_id': strUserId,
            'order_id': self.I('order_id'),
            'demand_id': self.I('demand_id'),
            'media_id': self.I('media_id'),
            'url': self.I('link'),
            'title': dicResp['title'],
            'read_num': 0,
            'picture_1': self.I('pic1'),
            'picture_2': self.I('pic2'),
            'picture_3': self.I('pic3'),
            'publish_time': dicResp['publish_time']
        }
        intStatus = self.importService('demand').feedback_submit(dicData)
        #print intStatus
        self.out(intStatus)

    def feedback_crawl(self, strUrl):
        # 订单反馈链接通过新指获取阅读数，另订单结束时再获取
        import api.crawler as crawler
        cw = crawler.crawler()
        dicData = cw.feedback(strUrl)
        dicNumData = cw.get_num_real_time(strUrl)
        dicData.update(dicNumData)
        return dicData

    def feedback_pass(self):
        strOrderId = self.I('order_id')
        strDemandId = self.I('demand_id')
        intStatus = self.importService('demand').feedback_pass(strDemandId, strOrderId)
        self.out(intStatus)

    def cancel_order(self):
        str_user_type = ''
        if self.I('is_ad_user') == 'True':
            str_user_type = '5'
        elif self.I('is_ad_user') == 'False':
            str_user_type = '6'
        str_user_id = str(self.current_user['user_id'])
        str_order_id = self.I('order_id', '')
        intStatus = self.importService('demand').cancel_order(str_user_type, str_user_id, str_order_id)
        self.out(intStatus)

    def order_appeal(self):
        str_user_id     = str(self.current_user['user_id'])
        str_order_id    = self.I('order_id', '')
        str_description    = self.I('description', '')

        demand_service = self.importService('demand')
        demand_service.order_appeal(str_user_id, str_order_id, str_description)
        self.out(demand_service.status)

    # 添加需求表单
    def demand_form(self):
        # 读取用户信息
        dicUser = self.userService.get_user_basic(self.current_user['user_id'])
        if not dicUser:
            self.redirect('/404')
            return

        # 获取营销形式
        demandFormService = self.importService('demand')
        tupDemandForm = demandFormService.demand_form()

        # 输出到模板
        self.dicViewData['demand_form'] = tupDemandForm
        self.dicViewData['user'] = dicUser
        self.display('demand_form')

    def get_category(self):

        categoryMediaService = self.importService('category_media')
        dicCategoryMedia = categoryMediaService.getAll()
        #print dicCategoryMedia
        self.out(200, '', dicCategoryMedia)

    def get_tag(self):

        tagService = self.importService('tag')
        tupTags = tagService.get_list()
        self.out(200, '', tupTags)

    # 添加需求
    def demand_create(self):
        dicParams = {
            'media_platform_id'		: self.I('media_platform_id'), 	# 投放平台
            'form'				    : self.I('form'), 				# 营销形式
            'title'					: self.I('title'), 				# 营销主题
            'time_begin'			: self.I('timeBegin'), 			# 营销时间 开始
            'time_end'				: self.I('timeEnd'), 			# 营销时间 结束
            'category'				: self.I('category'), 			# 需求类型，分类
            'tag'					: self.I('tag'), 				# 需求类型，分类
            'money'					: self.I('money'), 				# 预算总额
            'phone'					: self.I('phone'), 				# 手机
            #'description': self.I('description'), 					# 具体执行要求 描述
            'audience_gender'		: self.I('audienceGender'), 	# 性别
            'audience_province_id'  : self.I('audienceProvinceId'), # 地域
            'audience_city_id'		: self.I('audienceCityId', ''), # 地域
            'audience_county_id'	: self.I('audienceCountyId', ''),# 地域
            'audience_num'			: self.I('audienceNum'), 		# 粉丝数
            'view'					: self.I('view'), 				# 阅读数
            'num'                   : self.I('num', 0),             # 自媒体数
            'marketing'				: self.I('marketing'), 			# 营销建议指标
            'original'              : self.I('original', 0),        # 是否原创
            'article_status'        : self.I('articleStatus'),      # 文案提供方式
            # 'artical_title'		: self.I('articalTitle'), 		# 内容标题
            # 'artical_author'		: self.I('articalAuthor'), 		# 内容作者
            # 'artical_content'		: self.I('articalBody'), 		# 内容内容
            'origin_link'			: self.I('originLink'), 		# 微信图文链接
            'doc_path'              : self.I('docPath'),            # 文档链接
            'extra_info'            : self.I('extraInfo'),          # 额外信息
            #'invoice': 1 if self.I('fapiao') == 'on' else 0, 		# 是否需要发票
            #'invoice_title': self.I('fapiao_title'), 				# 发票台头
            'user_id'				: self.current_user['user_id'] 	# 用户ID
        }

        # 写入需求数据
        demandService = self.importService('demand')
        demand_id = demandService.demandCreate(dicParams)
        self.out(demandService.status, '', {'demand_id' : demand_id})


    # 我的自媒体
    def media(self):

        strMyMenu = 'media'

        # 获取用户信息及城市信息
        dicUser = self.userService.getOneAndCity(self.current_user['user_id'])

        # 用户拥有的自媒体
        mediaService = self.importService('media')
        tup_my_media = mediaService.my_media(self.current_user['user_id'])

        self.dicViewData['my_menu_focus']       = strMyMenu
        self.dicViewData['user']                = dicUser
        self.dicViewData['list_media']          = tup_my_media

        self.display('media')

    def media_edit(self):
        #print 111
        strId = self.I('id')
        if not strId:
           # print 333
            self.redirect('/404')
            return

        if self._POST:
            #print 222
            postData = {
                'id': strId,
                'category_media_id': self.I('category'),
                'tag': self.I('tag'),
                'audience_gender': self.I('audience_gender'),
                'audience_province_id': self.I('audience_province_id'),
                'audience_city_id': self.I('audience_city_id'),
                'audience_county_id': self.I('audience_county_id'),
                'user_id': self.current_user['user_id']
            }
            #print postData

            mediaService = self.importService('media')
            mediaService.media_edit(postData)
            self.out(mediaService.status)
            return

        mediaService = self.importService('media')
        dicMedia = mediaService.get_media(strId)
        if not dicMedia:
            print 'media_id:', strId
        if dicMedia.get('user_id') != self.current_user['user_id']:
            self.redirect('/404')
            return

        # tag
        tup_tag = mediaService.get_tag(strId)
        #print tup_tag

        # 刊例属性
        dic_attribute = mediaService.get_attribute_value()
        attr_value =[]
        for keys in dic_attribute :
            attr_value = dic_attribute[keys]['value']
        attr = json.dumps(attr_value)
        # 已有刊例
        tup_price = mediaService.media_price(strId)
        self.dicViewData['media'] = dicMedia
        #print dicMedia
        #print tup_tag
        self.dicViewData['media_tag'] = tup_tag
        self.dicViewData['attribute'] = dic_attribute
        self.dicViewData['media_price'] = tup_price
        self.dicViewData['attr_value'] = attr
        #print attr
        self.display('media_edit')

    def media_price_edit(self):
        dic_post_data = {
            'id': self.I('id'),
            'media_price_id':self.I('media_price_id'),
            'price': self.I('price'),
            'user_id': self.current_user['user_id']
        }
        #print dic_post_data
        mediaService = self.importService('media')
        intStatus = mediaService.media_price_edit(dic_post_data)
        self.out(intStatus)

    def media_price_create(self):
        """ 添加刊例价格
        """

        dic_post_data = {
            'id': self.I('id'),
            'attribute': self.I('attribute'),
            'price': self.I('price'),
            'user_id': self.current_user['user_id']
        }

        mediaService = self.importService('media')
        intStatus = mediaService.media_price_create(dic_post_data)
        self.out(intStatus)

    def check_origin(self):
        if self._POST:
            #print 111
            str_media_id = self.I('id')
            strUrl = self.I('url')
            if not strUrl or not str_media_id:
                self.out(401)
                return
            #print str_media_id
            intStatus =self.importService('media').check_origin(str_media_id,strUrl)
            #print intStatus
            self.out(intStatus)
            return
        return



    def media_price_del(self):
        """ 删除刊例价格
        """

        str_media_id = self.I('id')

        mediaService = self.importService('media')
        intStatus = mediaService.media_price_del(str_media_id)
        self.out(intStatus)

    def media_create(self):
        """ 添加自媒体
        """

        # 读取用户信息
        dicUser = self.userService.get_user(self.current_user['user_id'])

        # get vcode from cookie
        strVcode = self.get_secure_cookie('media_vcode')
        if not strVcode:
            # create new vcode and save to cookie
            strVcode = self.salt(64)
            self.set_secure_cookie('media_vcode', strVcode, expires=time.time()+900)

        # 提交验证
        if self._POST:
            # 获取参数
            strUrl = self.I('url')

            if not strUrl:
                return 401

            import api.crawler as crawler

            dicData = crawler.crawler().official(strUrl, strVcode)

            strBiz = dicData.get('biz')
            if strBiz is None:
                self.out(603)
                return
            mediaService = self.importService('media')
            boolStatus = mediaService.check_wechat(strBiz)
            if boolStatus:
                self.out(604)
                return

            if dicData and 'status' not in dicData:
                dicData['user_id'] = self.current_user['user_id']
                # 验证通过，写数据
                # 用户自媒体
                dicResp = mediaService.media_wechat_create(dicData)
                if dicResp['status'] == 200:
                    crawler.crawler().add_to_group(strUrl)
                self.out(dicResp['status'], '', dicResp['data'])
            else:
                self.out(500)
            return


        self.dicViewData['user'] = dicUser
        self.dicViewData['vcode'] = strVcode

        self.display('media_create')

    def media_update(self):
        """ 编辑自媒体
        """

        if not self._POST:
            self.redirect('501')
            return

        # 获取请求参数
        dicData = {
            'oa_id': self.I('oid'),
            'price_1x': self.I('price_1x'),
            'price_x1': self.I('price_x1'),
            'price_x2': self.I('price_x2'),
            'price_xx': self.I('price_xx'),
            'category_list': self.I('category_list'),
            'tag_list': self.I('tag_list'),
            'audience_gender': self.I('audience_gender'),
            'audience_area': self.I('audience_area'),
            'province': self.I('province'),
            'city': self.I('city'),
            'county': self.I('county'),
            'user_id': self.current_user['user_id']
        }

        if not dicData['oa_id']:
            self.redirect('/401')
            return

        officialService = self.importService('official')
        # 判断是否是自己的自媒体
        dicOfficial = officialService.official_one(dicData)
        if not dicOfficial:
            self.redirect('/601')
            return

        intStatus = officialService.official_update(dicData)

        if intStatus == 200:
            self.redirect('/user?a=media')
        else:
            self.redirect('/500')

    def media_price_update(self):
        """ 修改自媒体刊例价格
        """

        # get params
        strMediaId = self.I('media_id');
        strPrices = self.I('prices');

        if not strMediaId or not strPrices:
            self.out(401)
            return

        # update
        officialService = self.importService('official')
        intStatus = officialService.official_price_update(self.current_user['user_id'], strMediaId, strPrices)
        self.out(intStatus)

    def union(self):
        """ 我的联盟
        """

        strMyMenu = 'union'

        # 获取用户信息及城市信息
        dicUser = self.userService.getOneAndCity(self.current_user['user_id'])

        # 我的联盟
        unionService = self.importService('union')
        lisUnion = unionService.myUnion(self.current_user['user_id'])

        self.dicViewData['my_menu_focus'] = strMyMenu
        self.dicViewData['user'] = dicUser
        self.dicViewData['union'] = lisUnion

        self.display('union')

    def union_form(self):
        """ 创建联盟表单
        """

        categoryService = self.importService('category')
        # 获取所有分类
        dicCategory = categoryService.getAll()

        self.dicViewData['category'] = dicCategory

        self.display('union_form')

    def union_avatar(self):
        """ 上传联盟头像
        """

        if not self._POST:
            self.redirect('/402')
            return

        strFile = self.request.files['avatar']

        import api.upload as upload

        dicAvatar = upload.upload(strFile[0]['body'])

        self.out(200, '', {
            'url': '%s%s%s' % (self.dicConfig['PIC']['HOST'], dicAvatar['key'], '-union'),
            'key': dicAvatar['key']
        })

    def union_create(self):
        """ 创建联盟
        """

        # 获取参数
        dicData = {
            'union_id': self.I('union_id'),
            'name': self.I('name'),
            'logo': self.I('logo'),
            'desc': self.I('desc'),
            'category': self.I('category'),
            'tel': self.I('tel'),
            'user_id': self.current_user['user_id']
        }

        unionService = self.importService('union')
        intStatus = unionService.create(dicData)
        self.out(intStatus)

    def wallet(self):
        strMyMenu = 'wallet'
        self.dicViewData['my_menu_focus'] = strMyMenu
        self.display('wallet')

class U(base.base):
    """ 用户详情
    """

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        """ 他的自媒体
        """

        # 获取参数
        strUserId = self.I('id')

        # 用户信息
        user_service = self.importService('user')
        dic_user = user_service.getOneAndCity(strUserId)
        if not dic_user:
            self.redirect('/404')

        # 他的自媒体
        mediaService = self.importService('media')
        tupMedia = mediaService.my_media(strUserId)

        self.dicViewData['user'] = dic_user
        self.dicViewData['media'] = tupMedia
        self.dicViewData['menu'] = 'media'

        self.display('index')

    def union(self):
        """ 他的联盟
        """

        # 获取参数
        strUserId = self.I('id')

        if not strUserId:
            self.redirect('/404')
            return

        # 用户信息
        user_service = self.importService('account')
        dicUser = user_service.getOneAndCity(strUserId)

        # 他的联盟
        unionService = self.importService('union')
        tupUnion = unionService.myUnion(strUserId)

        self.dicViewData['user'] = dicUser
        self.dicViewData['union'] = tupUnion
        self.dicViewData['menu'] = 'union'

        self.display('union')


class WechatSubmit(base.base):
    """ 微信公众号登录
    """
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)


    def index(self):
        strTicket = self.importService('verify_info').get_component_verify_ticket()
        # print 'get ticket:', strTicket
        access_token = wechat.get_component_access_token(strTicket).get('component_access_token')
        # print access_token
        pre_auth_code = wechat.get_pre_auth_code(access_token).get('pre_auth_code')
        # print pre_auth_code
        if not pre_auth_code:
            self.redirect('/user?a=media_create')
            return
        url = wechat.get_login_url(pre_auth_code, 'http://www.yidao.info/wechat_bind')
        # print url
        self.redirect(url)


class WechatMessage(base.base):
    """
    微信公众号授权事件接收
    """

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        signature = self.I('signature')
        msg_signature = self.I('msg_signature')
        timestamp = self.I('timestamp')
        nonce = self.I('nonce')
        encrypt = self.I('encrypt')
        # print signature, msg_signature, timestamp, nonce, encrypt
        if wechat.sha1(timestamp, nonce, encrypt) == signature:
            # print 'success'
            self.write('success')
            encrypt_xml = self.request.body
            strTicket = wechat.get_component_verify_ticket(encrypt_xml)
            # print 'set ticket:', strTicket
            # TODO 改造为统一中心控制定时刷新，而非业务刷新
            self.importService('verify_info').set_component_verify_ticket(strTicket)

class WechatBind(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        # TODO 改成异步请求，授权后即可，后台跑抓取公众号信息
        auth_code = self.I('auth_code')
        # expires_in = self.I('expires_in')
        # auth_code = 'queryauthcode@@@zP9SvsAW9A0LqkgFAd7VGu4XyvjuVm4q6yAOrvQcqksoKvCVc24TslRdDXBd9Lm0BIvsyCk-bVp776e0YSQfdg'
        # expires_in = 3600
        # print auth_code, expires_in
        strTicket = self.importService('verify_info').get_component_verify_ticket()
        # TODO 改造为统一中心控制定时刷新，而非业务刷新
        cp_access_token = wechat.get_component_access_token(strTicket).get('component_access_token')
        # access_token = 'y9CWPzp0MD23YCtEd6tLRRUUe4Jn-SKKe3DsgulE8ZYaWZaj2twZpM1EjqH7xLdnL0o0u-kqAe67jts29xZXP5upSvopsaVOaH7T9BUljb0EGIgAFASUW'
        # print 'component_access_token:', cp_access_token
        # 授权方即用户的appid
        auth_info = wechat.get_authorization_info(cp_access_token, auth_code).get('authorization_info', {})
        appid = auth_info.get('authorizer_appid')
        access_token = auth_info.get('authorizer_access_token')
        # print 'authorizer_appid:', appid
        # print 'authorizer_access_token:', access_token
        wechat_info = wechat.get_authorizer_info(cp_access_token, appid)
        url = wechat.get_news_url(access_token)
        # print url
        # print wechat_info
        if wechat_info:
            dicData = {}
            auth_info = wechat_info.get('authorizer_info', {})
            dicData['user_id'] = self.get_secure_cookie('user_id')
            dicData['biz'] = wechat.get_biz(url)
            dicData['qrcode'] = wechat.get_qrcode(dicData['biz'])
            dicData['wechat_id'] = auth_info.get('alias')
            # print 'head_img:', auth_info.get('head_img')
            dicData['avatar'] = wechat.get_avatar(auth_info.get('head_img'))
            dicData['name'] = auth_info.get('nick_name')
            dicData['user_name'] = auth_info.get('user_name')
            dicData['features'] = crawler.crawler().get_features(url)
            dicResp = self.importService('media').media_wechat_create(dicData)
            if dicResp['status'] == 200:
                # 添加到新指一道的group中
                crawler.crawler().add_to_group(url)
                self.redirect('/user?a=media_edit&id={id}'.format(id=dicResp['data']['media_id']))
            else:
                self.redirect('/user?a=media_create')
