# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

import MySQLdb
from config.config import GLOBAL_CONF as CONFIG

class DB(object):
    def __init__(self, mode='dev', base='DB_PROJECT'):
        # 连接MYSQL
        self.__host = CONFIG[mode]['DB_HOST']
        self.__user = CONFIG[mode]['DB_USER']
        self.__pass = CONFIG[mode]['DB_PASS']
        self.__base = CONFIG[mode][base]
        self.db = MySQLdb.connect(self.__host, self.__user, self.__pass, self.__base, use_unicode=1, charset='utf8')
        self.cursor = self.db.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    def find(self, strTableName, strType, dicData, booFormatData=True):
        ''' 读取一组数据

        @params strTableName string 表名
        @params strType string 类型，可以是list, first
        @prams dicData dict 数据字典
        @params booFormatData bool 是否格式化数据，默认为True
        '''

        if booFormatData:
            dicData = self.formatData(dicData)

        strTableName = self.buildTableName(strTableName)

        strFields = self.buildFields(dicData['fields'])

        strCondition = self.buildCondition(dicData['condition'])

        strJoin = self.buildJoin(dicData['join'])

        strLimit = self.buildLimit(dicData['limit'])

        strGroup = self.buildGroup(dicData['group'])

        strOrder = self.buildOrder(dicData['order'])

        strSql = "select %s from %s %s %s %s %s %s" % (
            strFields, strTableName, strJoin, strCondition, strGroup, strOrder, strLimit)
        # print strSql

        self.cursor.execute(strSql)

        if strType == 'list':
            dicList = self.cursor.fetchall()
        else:
            dicList = self.cursor.fetchone()

        return dicList

    def paginate(self, strTableName, dicData, cacheRow):
        ''' 分页读取数据

        @params strTableName string 表名
        @params dicData dict 数据字典，可以包裹field, fields, condition等key
        '''

        dicData = self.formatData(dicData)

        # 页码
        intPage = 1
        intPageNum = 10
        if 'page' in dicData:
            intPage = dicData['page'][0]
            if len(dicData['page']) == 2:
                intPageNum = dicData['page'][1]
        intStartLimit = (intPage - 1) * int(intPageNum)
        dicData['limit'] = [str(intStartLimit), str(intPageNum)]

        # 总条数
        intRows = self.getRows(strTableName, {
            'fields': ['count(*) as count'],
            'condition': dicData['condition'],
            'join': dicData['join']
        }, False, cacheRow)

        # 获取数据
        tupList = self.find(strTableName, 'list', dicData, False)

        return [tupList, intRows]

    def getRows(self, strTableName, dicData, booFormatData=True, cache=False):
        ''' 获取数据记录数

        @params strTableName string 表名
        @params dicData dict 数据字典
        @params booFormatData bool 是否格式化数据，默认为True
        '''

        if booFormatData:
            dicData = self.formatData(dicData)

        strTableName = self.buildTableName(strTableName)

        strFields = self.buildFields(dicData['fields'])

        strJoin = self.buildJoin(dicData['join'])

        strCondition = self.buildCondition(dicData['condition'])

        strSql = "select %s from %s %s %s" % (strFields, strTableName, strJoin, strCondition)
        # print strSql
        if cache:
            import time
            now = int(time.time())
            expires_in = now + 60 * 10
            strSqlHash = hash(strSql)
            res = self.find('verify_info', 'first', {'condition': 'name="%s"' % strSqlHash})
            if res and res['expires_in'] > now:
                return int(res.get('value', '0'))
            self.cursor.execute(strSql)
            dicRows = self.cursor.fetchone()
            rtn = dicRows['count'] if dicRows else 0
            if not res:
                self.insert('verify_info', {'key': 'name, value, expires_in, last_update_time',
                                            'val': '"%s", "%s", %s, %s' % (strSqlHash, rtn, expires_in, now)})
            else:
                self.update('verify_info', {'fields': ['value="%s"' % rtn,
                                                       'expires_in=%s' % expires_in,
                                                       'last_update_time=%s' % now],
                                            'condition': 'name="%s"' % strSqlHash})
            self.db.commit()
        else:
            self.cursor.execute(strSql)
            dicRows = self.cursor.fetchone()
            rtn = dicRows['count'] if dicRows else 0
        return rtn

    def insert(self, strTableName, dicData):
        ''' 插入数据

        @params strTableName string 表名
        @params dicData dict 数据字典
        '''
        dicData = self.formatData(dicData)
        strTableName = self.buildTableName(strTableName)

        strSql = "insert into %s (%s) values (%s)" % (strTableName, dicData['key'], dicData['val'])
        # print strSql.encode('u8')
        return self.cursor.execute(strSql)

    def update(self, strTableName, dicData):
        ''' 修改数据

        @params strTableName string 表名
        @params dicData dict 数据字典
        '''

        dicData = self.formatData(dicData)
        strTableName = self.buildTableName(strTableName)
        strFields = self.buildFields(dicData['fields'])
        strCondition = self.buildCondition(dicData['condition'])

        strSql = "update %s set %s %s" % (strTableName, strFields, strCondition)
        print strSql.encode('u8')
        return self.cursor.execute(strSql)

    def delete(self, strTableName, dicData):
        ''' 删除数据

        @params strTableName string 表名
        @params dicData dict 数据字典
        '''
        dicData = self.formatData(dicData)
        strTableName = self.buildTableName(strTableName)
        strCondition = self.buildCondition(dicData['condition'])

        strSql = "delete from %s %s" % (strTableName, strCondition)
        # print strSql
        return self.cursor.execute(strSql)

    @staticmethod
    def formatData(dicData):
        ''' 格式化数据
        将fields, condition, join 等数据格式化返回

        @params dicData dict 数据字典
        '''

        dicData['fields'] = dicData.get('fields', '')
        dicData['join'] = dicData.get('join', '')
        dicData['condition'] = dicData.get('condition', '')
        dicData['order'] = dicData.get('order', '')
        dicData['group'] = dicData.get('group', '')
        dicData['limit'] = dicData.get('limit', '')
        dicData['key'] = dicData.get('key', '')
        dicData['val'] = dicData.get('val', '')

        return dicData

    def buildTableName(self, strTableName):
        ''' 构建表名
        根据配置文件中的表前辍，构建表名

        @params strTableName string 表名
        '''

        strTableName = strTableName

        return strTableName

    @staticmethod
    def buildFields(lisFields):
        ''' 构建读取字段

        @params lisFields list 字段列表
        '''

        strFields = ','.join(lisFields) if lisFields else '*'

        return strFields

    @staticmethod
    def buildJoin(strJoin):
        ''' 构建Join

        @params dicCondition dict 条件字典
        '''

        return 'LEFT JOIN %s' % strJoin if strJoin else ''

    @staticmethod
    def buildCondition(strCondition):
        ''' 构建条件

        @params dicCondition dict 条件字典
        '''

        return 'where %s' % strCondition if strCondition else ''

    @staticmethod
    def buildGroup(strGroup):
        ''' 构建order
        未完成

        @params group 分组
        '''
        return 'group by ' + strGroup if strGroup else ''

    @staticmethod
    def buildOrder(strOrder):
        ''' 构建order
        未完成

        @params
        '''
        return 'order by ' + strOrder if strOrder else ''

    @staticmethod
    def buildLimit(lisLimit):
        ''' 构建limit

        @params lisLimit list limit
        '''

        strLimit = ','.join(lisLimit) if lisLimit else ''

        return 'limit ' + strLimit if strLimit else ''

    def commit(self):
        try:
            self.db.commit()
        except Exception, e:
            print e
            self.db.rollback()
        finally:
            self.cursor.close()
            self.db.close()
