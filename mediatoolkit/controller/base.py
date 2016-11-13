#!usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import hashlib
import json
import random
import importlib
import time
import datetime
import math
import decimal
from collections import defaultdict
from source.controller import controller
from  conf.config import *

sys.path.append('../..')
from config.config import GLOBAL_CONF as CODE


class base(controller):
    ''' 基类
    '''

    isSign = False  # 是否使用签名验证
    signPass = True  # 是否通过签名验证
    isAuth = True  # 是否使用登录验证
    isAccess = True # 是否权限验证
    json = json
    time = time
    datetime = datetime
    CODE = CODE
    mediaConf = MEDIA_CONF

    def initialize(self, config=None):
        ''' 初始化

        初始化数据类
        '''

        # 加载父类初始化方法
        controller.initialize(self, config)
        controller.operatStatus = 0


        # 设置模板目录(必须)
        self.strViewPath = self.dicConfig['VIEW_PATH']

        if self.isSign:
            # 获取参数
            try:
                strData = self.get_argument('data')
                strTime = self.get_argument('t')
                strHash = self.get_argument('h')
            except Exception, e:
                print e
                strData = ''
                strTime = ''
                strHash = ''

            result = self.sign((strData, strTime), strHash)

            # 如果验证签字未通过，终止程序
            if not result:
                self.signPass = False
                self.out(601)
        self.dicViewData['title'] = self.dicConfig['title']

    # @staticmethod
    # def req_access(*param):
    #     def _deco(func):
    #         def __deco(self, *args, **kwargs):
    #             if len(param)!=1: self.redirect('/')
    #             user_id = self.current_user.get('id')
    #             roleData = self.importService('admin_access_permission').getUserRole(user_id)
    #             moduleData = self.importService('admin_access_permission').getUserModuleId(self.__module__.split('.')[1], None)
    #             roleOpera = self.importService('admin_access_permission').getRoleOpera(roleData['role_id'], moduleData[0]['id'])
    #             count=0
    #             for idx, i in enumerate(roleOpera['access_operat']):
    #                 if i=='1':
    #                     count+=2**(3-idx)
    #
    #             data = count&(2**(4-param[0]))
    #             if data> 0:
    #                 controller.operatStatus=0
    #                 return func(self, *args, **kwargs)
    #             else:
    #                 controller.operatStatus=1
    #                 if self.request.arguments:
    #                     self.display('detail', 'admin_user')
    #                     # self.display('index', self.request.path.split('/')[1], self.request.path.split('/')[2])
    #                 else:
    #                     self.display('index', '', 'index')
    #                 return False
    #         return __deco
    #     return _deco

    def auth(self):
        ''' 登录认证
        读取cookie值，判断是否登录

        '''
        if self.current_user.get('id'):
            self.dicViewData['login_user'] = self.current_user
            return True
        else:
            self.redirect('/login')
            return False

    def validity(self):
        ''' 检测用户是否有效
        '''
        user_id = self.current_user.get('id')
        if user_id:
            dicData = self.importService('admin_access_permission').getUserStatus(user_id)
            if dicData['status'] == 1:
                return False, ""
            else:
                return True, user_id
        else:
            return False, ""

    def sign(self, tupParams, strHash):
        ''' 签名
        将传入参数进行MD5加密，并和传入已签名字符串进行比较，相同，通过，不相同，拒绝

        @params dicParams dict 参数字典
        @params strHash string 传入签字字符串
        '''

        strParams = ''.join(tupParams) + self.dicConfig['API_KEY']  # 连接参数与API_KEY
        strSign = self.md5(strParams)

        # 判断是否相同
        if strSign != strHash:
            return False
        return True

    def apiSign(self, dicData, strPostUrl):
        ''' API签名请求

        @params dicData dict 发送数据字典
        @params strPostUrl string 请求地址
        '''

        # 将数据json
        strData = self.json.dumps(dicData)

        # 生成请求时间
        strTime = str(self.time.time())

        # 进行签名加密
        strHash = self.md5('%s%s%s' % (strData, strTime, self.dicConfig['bag_api_key']))

        # 发送请求
        # print "strData = ", strData
        strResult = self.rquest(strPostUrl, 'POST', {'data': strData, 'tamp': strTime, 'hash': strHash})
        # print strResult.encode('utf8')

        dicResult = {}
        try:
            dicResult = self.json.loads(strResult)
        except:
            return False

        return dicResult

    def md5(self, strText):
        ''' MD5加密

        @params strText string 需加密字符串
        @return strResult string 加密后字符串
        '''
        strResult = hashlib.md5(strText)
        return strResult.hexdigest()

    def salt(self, intSaltLen=6):
        ''' 密码加密字符串
        生成一个固定位数的随机字符串，包含0-9a-z

        @params intSaltLen int 生成字符串长度
        '''

        strChrset = '0123456789abcdefghijklmnopqrstuvwxyz'
        lisSalt = []
        for i in range(6):
            strItem = random.choice(strChrset)
            lisSalt.append(strItem)

        strSalt = ''.join(lisSalt)
        return strSalt

    def out(self, statusCode, strMsg='', dicData=None):
        ''' 输出结果

        @params statusCode int 状态值
        @params strMsg string 说明文字
        @params dicData dict 返回数据字典
        '''
        if dicData is None:
            dicData = {}
        dicOut = {
            'status': statusCode,
            'msg': strMsg,
            'data': dicData
        }

        self.write(json.dumps(dicOut, cls=DecimalEncoder))

    def page(self, intPage, intPageDataNum, intDataCount, strPageUrl):
        ''' 分页处理

        @params intPage int 当前页码
        @params intPageDataNum int 每页多少条数据
        @params intDataCount int 共有多少条数据
        @params strPageUrl string 分页链接
        <nav>
            <ul class="pagination pull-right">
                <li><a href="#">&laquo;</a></li>
                <li class="active"><a href="#">1</a></li>
                <li><a href="#">2</a></li>
                <li><a href="#">3</a></li>
                <li><a href="#">4</a></li>
                <li><a href="#">5</a></li>
                <li><a href="#">&raquo;</a></li>
            </ul>
        </nav>
        '''
        lisPageHtml = []

        intPageCount = int(math.ceil(float(intDataCount) / float(intPageDataNum)))
        if intPageCount > 1:
            lisPageHtml.append('<nav style="margin:20px 20px 20px 0px;"><ul class="pagination" style="display:inline;">')
            if intPage > 1:
                lisPageHtml.append('<li><a href="%s&page=%d">&laquo;</a></li>' % (strPageUrl, 1))

            if intPageCount < 10:
                for i in range(1, intPageCount + 1):
                    strClassName = 'active' if i == intPage else ''
                    strPageNum = '<li class="%s"><a href="%s&page=%d">%d</a></li>' % (strClassName, strPageUrl, i, i)
                    lisPageHtml.append(strPageNum)
            else:
                # intNum = int(math.ceil(float(intPage / 10) + 1 if intPage / 10 == 1 else float(intPage) / 10))
                intNum = 0
                if intPage >= intPageDataNum:
                    intNum = intPage / intPageDataNum
                if intNum == 0:
                    intStartPageNum = 1
                    intEndPageNum = intPageDataNum - 1 if intPageCount >= intPageDataNum - 1 else intPageCount
                else:
                    intStartPageNum = intNum * intPageDataNum
                    intEndPageNum = intNum * intPageDataNum + intPageDataNum - 1 if intPageCount >= (intNum * intPageDataNum + intPageDataNum - 1) else intPageCount
                    intMorePrePageNum = intStartPageNum - 1
                    lisPageHtml.append('<li><a href="%s&page=%d">...</a></li>' % (strPageUrl, intMorePrePageNum))

                for i in range(intStartPageNum, intEndPageNum + 1):
                    strClassName = 'active' if i == intPage else ''
                    strPageNum = '<li class="%s"><a href="%s&page=%d">%d</a></li>' % (strClassName, strPageUrl, i, i)
                    lisPageHtml.append(strPageNum)

                if intPageCount >= (intNum * intPageDataNum + intPageDataNum - 1):
                    intMoreNextPageNum = intEndPageNum + 1
                    lisPageHtml.append('<li><a href="%s&page=%d">...</a></li>' % (strPageUrl, intMoreNextPageNum))

            if intPage < intPageCount:
                lisPageHtml.append('<li><a href="%s&page=%d">&raquo;</a></li>' % (strPageUrl, intPageCount))

            lisPageHtml.append('</ul><div class="searchBox">'
                               '<input id="pageInput" class="typeText" style="width:50px;height:32px;margin-left:20px;">'
                               '<span> / </span><span id="pageMax">%d</span>'
                               '<button id="pageGo" class="btnOk" style="margin-left:10px;">Go</button></div></nav>' % intPageCount)

        strPageHtml = ''.join(lisPageHtml)
        return strPageHtml

    def formatTime(self, intTime, strTime='%Y-%m-%d %H:%I:%M'):
        ''' 将时间戳格式化为时间
        '''

        return self.time.strftime(strTime, self.time.localtime(intTime))

    def datetime_timestamp(self):
        ## 获取当天整点时间戳 时间 2016/5/17 0:0:0
        today = self.datetime.date.today()
        return self.time.mktime(today.timetuple())

    def get_current_user(self):
        ''' 获取cookie值
        '''
        userId      = self.get_secure_cookie('user_id')
        userName    = self.get_secure_cookie('user_name')  #nickname
        # if userId:
        #     access = self.importService('admin_access').getUserModuleName(userId)
        # else:
        #     access = ''
        # userAccess      = ','.join(access) if access else ''              #做用户数据权限验证，保存之前的set格式，见access函数
        # userAccess  = set(userAccess.split(','))                          #多角色用户去重
        #
        # accsess_data = self.importService('admin_access').getUserAccess()
        # menu_list = []
        # for item in list(accsess_data):
        #     menu = {}
        #     if str(item['id']) in userAccess:
        #         menu['id'] = item['id']
        #         menu['label'] = item['label']
        #         menu['parent_id'] = item['parent_id']
        #         menu['menu_route'] = item['menu_route']
        #         menu['access_id'] = item['access_id']
        #         menu['level'] = item['access_level']
        #         menu['is_child'] = item['is_exsit_child']
        #         menu['validity'] = item['validity']
        #         menu_list.append(menu)

        # return {'id': userId, 'name': userName, 'accesslist':self.json.dumps(menu_list),'access':userAccess} #set格式json编码出错，则需按list格式
        return {'id': userId, 'name': userName}

    def reset_cookie_expires(self):
        userId = self.get_secure_cookie('user_id')
        userName = self.get_secure_cookie('user_name')
        self.set_secure_cookie("user_id", userId, expires=time.time() + 1800)
        self.set_secure_cookie("user_name", userName, expires=time.time() + 1800)

    def clearTemplateCache(self):
        ''' 清除模板缓存
        '''

        self._template_loaders.clear()

    def get(self):
        ''' 重写父类get方法，接受GET请求
        增加登录验证判断

        固定参数a，如果a有值，调用同名方法，如果a没有值，调用index方法
        '''

        if self.isAuth:
            auth = self.auth()
            if not auth:
                return
            self.reset_cookie_expires()

        if self.isAccess:
            access = self.access()
            if not access:
                return

        if not self.signPass:
            return

        controller.get(self)

    def post(self):
        ''' 重写父类post方法，接受POST请求
        增加登录验证判断

        固定参数a，如果a有值，调用同名方法，如果a没有值，调用index方法
        '''
        if self.isAuth:
            auth = self.auth()
            if not auth:
                return
            self.reset_cookie_expires()

        if self.isAccess:
            access = self.access()
            if not access:
                return

        if not self.signPass:
            return

        controller.post(self)

    def user_access_module(self, userID, permission, url):
        status = self.importService("admin_access_permission").adminModuleIndex(userID, permission, url)
        if status != 200:
            self.redirect('/')
            return False

        # status = self.importService("admin_access_permission").deleteUserIndex(PASSTIME) #
        # if status['statusCode'] != 200:
        #     self.redirect('/')
        #     return False
        return True

    def check_user_accessIndex(self, userId):                                               # 检测一分钟内用户是否访问100次
        counts = self.importService("admin_access_permission").getUserIndex(userId, ACCESSTIME)
        if counts > ACCESSINDEX:
            status = self.importService("admin_access_permission").setUserInvalidity(userId)    # 清除cookie
            if status == 200:
                self.set_secure_cookie('user_id', '')
                self.set_secure_cookie('user_name', '')
                self.redirect('/login')
                return False
            else:
                return True
        return True

    def access(self):

        status, userId = self.validity()
        if not status:                                  # 检测登录后的用户被设置禁止访问
            self.redirect('/login')
            return False

        status = self.check_user_accessIndex(userId)    #最近10秒超过15次，退出用户，并禁用用户
        if not status:
            self.redirect('/login')
            return False

        return True

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

class SingnalTon：
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, _single):
            cls._single = super().__new__(cls, *args, **kwargs)
        return cls._single

