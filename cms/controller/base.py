#!usr/bin/env python
# -*- coding:utf-8 -*-


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
from  conf.config import PASSTIME,ACCESSINDEX,ACCESSTIME



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

    def initialize(self, config=None):
        ''' 初始化

        初始化数据类
        '''

        # 加载父类初始化方法
        controller.initialize(self, config)

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
            dicData = self.importService('admin_access_module').getUserStatus(user_id)
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
            lisPageHtml.append('<nav><ul class="pagination">')
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

            lisPageHtml.append('</ul></nav>')

        strPageHtml = ''.join(lisPageHtml)
        return strPageHtml

    def formatTime(self, intTime, strTime='%Y-%m-%d %H:%I:%M'):
        ''' 将时间戳格式化为时间
        '''

        return self.time.strftime(strTime, self.time.localtime(intTime))

    def get_user_access(self, access_id, userAccess):
        value_dict = {}
        datas = self.importService('admin_access').getUserChildAccess(access_id)     #根据主菜单id取子菜单
        if len(datas)>0 :
            for value in datas:
                if value['name'] in userAccess:
                    menus = {}
                    menus['name'] = value['name']
                    #menus['class_active'] = value['class_active']
                    menus['label'] = value['label']
                    menus['menu_route'] = value['menu_route']
                    value_dict[value['label']] = menus
                    if value['is_exsit_child']==1 and value['name'] in userAccess:
                        child_menu = self.get_user_access( value['access_id'], userAccess)
                        value_dict[value['label']]['child'] = child_menu
        return value_dict

    def get_current_user(self):
        ''' 获取cookie值
        '''
        userId      = self.get_secure_cookie('user_id')
        userName    = self.get_secure_cookie('user_name')  #nickname
        if userId:
            access = self.importService('admin_access').getUserModuleName(userId)
        else:
            access = ''
        userAccess      = ','.join(access) if access else ''              #做用户数据权限验证，保存之前的set格式，见access函数
        userAccess  = set(userAccess.split(','))                          #多角色用户去重
        access = list(userAccess)

        accsess_data = self.importService('admin_access').getUserAccess(1)
        menu_list = []

        for item in list(accsess_data):
            menu = {}
            menu_dict = {}
            if item['is_exsit_child'] == 0 and item['name'] in userAccess:
                menu['name'] = item['name']
                #menu['class_active'] = item['class_active']
                menu['label'] = item['label']
                menu['menu_route'] = item['menu_route']
                menu_dict[item['name']] = menu
                menu_list.append(menu_dict)
            elif item['is_exsit_child'] == 1 and item['parent_id'] == 0 and item['name'] in userAccess:
                menu['name'] = item['name']
                #menu['class_active'] = item['class_active']
                menu['label'] = item['label']
                menu['menu_route'] = item['menu_route']
                menu_dict[item['name']] = menu
                menu = self.get_user_access(item['access_id'], userAccess)
                menu_dict[item['name']]['child'] = menu
                menu_list.append(menu_dict)

        return {'id': userId, 'name': userName, 'accessMenu': json.dumps(menu_list), 'accesslist':json.dumps(access),'access':userAccess} #set格式json编码出错，则需按list格式

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

    def upload(self):
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

        controller.upload(self)

    def user_access_module(self, userID, F_module, C_module):
        data_list = self.importService("admin_access_module").getUserModuleId(F_module, C_module )
        status = self.importService("admin_access_module").adminModuleIndex(userID, data_list)
        if status != 200:
            self.redirect('/')
            return False

        # status = self.importService("admin_access_module").deleteUserIndex(PASSTIME) #
        # if status['statusCode'] != 200:
        #     self.redirect('/')
        #     return False
        return True

    def check_user_accessIndex(self, userId):                                               # 检测一分钟内用户是否访问100次
        counts = self.importService("admin_access_module").getUserIndex(userId, ACCESSTIME)
        if counts > ACCESSINDEX:
            status = self.importService("admin_access_module").setUserInvalidity(userId)    # 清除cookie
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
            return False

        userData = self.current_user
        userId =  userData.get('id')
        accessSet =  userData.get('access')
        # strFileName = self.__module__.split('.')[1]
        strFileName = self.importService("admin_user").getUserModule(self.request.path)
        strClassName = self.__class__.__name__
        strActionName = self.request.arguments.get('a')[0] if self.request.arguments.get('a') else 'index'
        # print "strFileName = ", strFileName

        if strFileName == 'index' or strFileName == 'error' or strFileName in accessSet :
            return self.user_access_module(userId, strFileName, '.'.join([strFileName,strClassName]))

        if '.'.join([strFileName, strClassName]) in accessSet:
            return self.user_access_module(userId, strFileName, '.'.join([strFileName,strClassName]))

        if '.'.join([strFileName, strClassName, strActionName]) in accessSet:
            return self.user_access_module(userId, strFileName, '.'.join([strFileName,strClassName]))

        self.redirect('/')
        return False


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)
