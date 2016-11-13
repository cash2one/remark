# -*- coding:utf-8 -*-


class baseDBModel(object):
    def __init__(self, db):
        self.db = db
        self.strTableName = ''
        self.lastrowid = -1

    def findPaginate(self, dicArg, cacheRow=False):
        '''
        :func: 通用分页查询
        '''
        tupData = self.db.paginate(self.strTableName, dicArg, cacheRow)
        return tupData

    def findPaginateAs(self, strTableName, dicArg, cacheRow=False):
        '''
        :func: 通用分页查询(带表名)
        '''
        tupData = self.db.paginate(strTableName, dicArg, cacheRow)
        return tupData

    def findMany(self, dicArg):
        '''
        :func: 通用多条查询
        '''
        tupData = self.db.find(self.strTableName, 'list', dicArg)
        return tupData

    def findManyAs(self, strTableName, dicArg):
        '''
        :func: 通用多条查询(带表名)
        '''
        tupData = self.db.find(strTableName, 'list', dicArg)
        return tupData

    def findOne(self, dicArg):
        '''
        :func: 通用单条查询
        '''
        dicData = self.db.find(self.strTableName, 'first', dicArg)
        if dicData is None:
            return {}
        return dicData

    def findOneAs(self, strTableName, dicArg):
        '''
        :func: 通用单条查询(带表名)
        '''
        dicData = self.db.find(strTableName, 'first', dicArg)
        if dicData is None:
            return {}
        return dicData

    def getRows(self, dicArg):
        '''
        :func: 通用获取记录条数
        '''
        return self.db.getRows(self.strTableName, dicArg)

    def insert(self, dicArg):
        '''
        :func: 通用新增记录
        '''
        self.db.b_commit = True
        try:
            self.db.insert(self.strTableName, dicArg)
            return self.db.cursor.lastrowid
        except Exception, e:
            print e
            self.db.status = self.db.dicConfig['DB_ERROR']
            return 0
            
    def update(self, dicArg):
        '''
        :func: 通用更新记录
        '''
        self.db.b_commit = True
        try:
            self.db.update(self.strTableName, dicArg)
            return self.db.cursor.lastrowid
        except Exception, e:
            #print 1112
            print e
            self.db.status = self.db.dicConfig['DB_ERROR']
            return 0

    def delete(self, dicArg):
        '''
        :func: 通用删除记录
        '''
        self.db.b_commit = True
        try:
            self.db.delete(self.strTableName, dicArg)
        except Exception, e:
            print e
            self.db.status = self.db.dicConfig['DB_ERROR']
            return 0

