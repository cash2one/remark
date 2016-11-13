# -*- coding:utf-8 -*-

import hashlib
import json
import random
import time
import datetime
import importlib
from collections import defaultdict
import tornado.escape


# import conf.config as config

class baseService(object):
    dicConfig = {}  # config.CONF

    time = time

    datetime = datetime

    json = json

    hashlib = hashlib

    status = 200

    def __init__(self, model, param):

        self.model = model
        self.param = param

        self.dicConfig = self.model.dicConfig

    @staticmethod
    def md5(strText):
        """ MD5加密

        @params strText string 需加密字符串
        @return strResult string 加密后字符串
        """
        strResult = hashlib.md5(strText)
        return strResult.hexdigest()

    def importModel(self, strModelName, strModelDir=''):
        """ 加载类

        @params strModelName string 类名
        """

        try:
            model = importlib.import_module('model.' + strModelName)
            return model.model(self.model)
        except Exception, e:
            print e
            return None

    def importService(self, strServiceName, strServiceParam=None):
        """ 加载服务类

        @params strServiceName string 服务类名
        @params strServiceParam string 服务类参数
        """

        try:
            if strServiceParam is None:
                strServiceParam = {}
            service = importlib.import_module('service.' + strServiceName)
            return service.service(self.model, strServiceParam)
        except Exception, e:
            #print 1111
            print e
            return None

    def formatTime(self, intTime, strTime='%Y-%m-%d %H:%I:%M'):
        """ 将时间戳格式化为时间
        """

        return self.time.strftime(strTime, self.time.localtime(intTime))

    def timetostr(self, strDate):
        """ 将日期时间转为时间戳

        @params strDate string 日期时间
        """

        try:
            t = self.time.strptime(strDate, "%m/%d/%Y %H:%M:%S")
        except (TypeError, ValueError):
            t = self.time.strptime(strDate, "%Y-%m-%d %H:%M:%S")

        return int(self.time.mktime(t))

    @staticmethod
    def salt(intSaltLen=6):
        """ 密码加密字符串
        生成一个固定位数的随机字符串，包含0-9a-z

        @params intSaltLen int 生成字符串长度
        """

        strChrset = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWSYZ'
        lisSalt = []
        for i in range(intSaltLen):
            strItem = random.choice(strChrset)
            lisSalt.append(strItem)

        strSalt = ''.join(lisSalt)
        return strSalt

    def getAvatarUrl(self, strCode, strType='avatar'):
        """ 
        """

        return '%s%s%s' % (self.dicConfig['PIC']['HOST'], strCode, '-' + strType)

    @staticmethod
    def escapeString(data, un=None):
        """ 特殊字符转义

        @params data string, tuple, list, dict 转义数据
        """

        if isinstance(data, str):
            return tornado.escape.xhtml_escape(data) if not un else tornado.escape.xhtml_unescape(data)
        elif isinstance(data, tuple) or isinstance(data, list):
            lisData = []
            for item in data:
                lisData.append(
                    tornado.escape.xhtml_escape(str(item)) if not un else tornado.escape.xhtml_unescape(str(item)))

            return lisData
        elif isinstance(data, dict):
            for key in data:
                data[key] = tornado.escape.xhtml_escape(str(data[key])) if not un else tornado.escape.xhtml_unescape(
                    str(data[key]))

            return data

    def research(self,table_name,num = 'one',*condition,**output):
        #author PAN YANG
        #research 方法，输入表名，查询数量findone or findmany，搜索条件格式为list或tuple，output参数为输出字段，返回default dict
        #print num,condition,output
        try:
            if isinstance(table_name,str):
                self.model = self.importModel(table_name)
            else: raise TypeError('Parameter Error，table_name should be str')

            # lis_condition = []
            # if 'id' in condition :
            #     lis_condition.append('id = {para_id}'.format(para_id = condition['id']))
            # if 'status'in condition :
            #     lis_condition.append('status = {para_status}'.format(para_status = condition['status']))

            if num == 'one':
                dic_data = self.model.findOne({
                    'condition': ' and '.join(condition)
                })
                #print dic_data.items()
                re_data = defaultdict(lambda :'-')
                for (k,v) in dic_data.items():
                    if k in output:
                        re_data[k] = v
                return re_data
            elif num == 'many':
                tup_data = self.model.findMand({
                    'condition': ' and '.join(condition)
                })

                lis_data = list(tup_data)
                re_data = []
                re_dict = defaultdict('-')
                for item in lis_data:
                    for(k,v) in item:
                        if k in output:
                            re_dict[k] = v
                    re_data.append(re_dict)
                return re_data
            else:
                raise TypeError('Parameter Error，num should be \'one\' or \'many\'')

        except Exception as e:
            print e
            return None

