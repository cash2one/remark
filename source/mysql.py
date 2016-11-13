# -*- coding:utf-8 -*-

import MySQLdb

class MySQL(object):
    ''' 数据类
    '''

    strTableName = ''
    dicConfig = {}
    status = 200  # 一次请求事务处理
    b_commit = False
    
    def init(self, dicConfig):
        ''' 初始化
        '''

        self.dicConfig = dicConfig
        strDbHost = self.dicConfig['DB_HOST']
        strDbUser = self.dicConfig['DB_USER']
        strDbPass = self.dicConfig['DB_PASS']
        strDbBase = self.dicConfig['DB_BASE']

        # 连接MYSQL
        self.db = MySQLdb.connect(strDbHost, strDbUser, strDbPass, strDbBase, use_unicode = 1, charset = 'utf8')
        self.cursor = self.db.cursor(cursorclass=MySQLdb.cursors.DictCursor)


    def find(self, strTableName, strType, dicData, booFormatData = True):
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

        strSql = "select %s from %s %s %s %s %s %s" % (strFields, strTableName, strJoin, strCondition, strGroup, strOrder, strLimit)
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
        if dicData.has_key('page'):
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
        #print strSql
        if cache:
            import time
            now = int(time.time())
            expires_in = now + 60 * 10
            strSqlHash = hash(strSql)
            res = self.find('verify_info', 'first', {'condition':'name="%s"' % strSqlHash})
            if res and res['expires_in'] > now:
                return int(res.get('value', '0'))
            self.cursor.execute(strSql)
            dicRows = self.cursor.fetchone()
            rtn = dicRows['count'] if dicRows else 0
            if not res:
                self.insert('verify_info', {'key': 'name, value, expires_in, last_update_time',
                                        'val':'"%s", "%s", %s, %s' % (strSqlHash, rtn, expires_in, now)})
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
        # print strSql
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
        # print strSql
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
        #print strSql
        return self.cursor.execute(strSql)


    def formatData(self, dicData):
        ''' 格式化数据
        将fields, condition, join 等数据格式化返回

        @params dicData dict 数据字典
        '''

        dicData['fields'] = dicData['fields'] if dicData.has_key('fields') else ''
        dicData['join'] = dicData['join'] if dicData.has_key('join') else ''
        dicData['condition'] = dicData['condition'] if dicData.has_key('condition') else ''
        dicData['order'] = dicData['order'] if dicData.has_key('order') else ''
        dicData['group'] = dicData['group'] if dicData.has_key('group') else ''
        dicData['limit'] = dicData['limit'] if dicData.has_key('limit') else ''
        dicData['key'] = dicData['key'] if dicData.has_key('key') else ''
        dicData['val'] = dicData['val'] if dicData.has_key('val') else ''

        return dicData


    def buildTableName(self, strTableName):
        ''' 构建表名
        根据配置文件中的表前辍，构建表名

        @params strTableName string 表名
        '''

        strTableName = self.dicConfig['DB_TABLEPRE'] + strTableName if self.dicConfig.has_key('DB_TABLEPRE') and self.dicConfig['DB_TABLEPRE'] else strTableName

        return strTableName


    def buildFields(self, lisFields):
        ''' 构建读取字段

        @params lisFields list 字段列表
        '''

        strFields = ','.join(lisFields) if lisFields else '*'

        return strFields


    def buildJoin(self, strJoin):
        ''' 构建Join

        @params dicCondition dict 条件字典
        '''

        return 'LEFT JOIN %s' % strJoin if strJoin else ''


    def buildCondition(self, strCondition):
        ''' 构建条件

        @params dicCondition dict 条件字典
        '''

        return 'where %s' % strCondition if strCondition else ''

    def buildGroup(self, strGroup):
        ''' 构建order
        未完成

        @params
        '''
        return 'group by ' + strGroup if strGroup else ''

    def buildOrder(self, strOrder):
        ''' 构建order
        未完成

        @params
        '''
        return 'order by ' + strOrder if strOrder else ''


    def buildLimit(self, lisLimit):
        ''' 构建limit

        @params lisLimit list limit
        '''

        strLimit = ','.join(lisLimit) if lisLimit else ''

        return 'limit ' + strLimit if strLimit else ''

    def finish(self):
        try:
            if self.status == 200:
                if self.b_commit:
                    self.db.commit()
            else:
                self.db.rollback()

            self.cursor.close()
            self.db.close()
        except Exception, e:
            print e
            pass
