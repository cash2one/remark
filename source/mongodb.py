# -*- coding:utf-8 -*-

import pymongo


class MongoDB(object):
    ''' 数据类
    '''

    strTableName = ''
    dicConfig = {}
    status = 200

    def init(self, dicConfig):
        self.dicConfig = dicConfig
        strDbHost = self.dicConfig['MONGODB_HOST']
        strDbPort = self.dicConfig['MONGODB_PORT']
        strDbUser = self.dicConfig['MONGODB_USER']
        strDbPass = self.dicConfig['MONGODB_PASS']
        strDb = self.dicConfig['MONGODB_DB']
        intDbPort = int(strDbPort)
        self.client = pymongo.MongoClient(strDbHost, intDbPort)
        if strDbUser:
            self.client[strDb].authenticate(strDbUser, strDbPass)
        self.db = self.client[strDb]
        self.desc = pymongo.DESCENDING
        self.asc = pymongo.ASCENDING

    def _find(self, strTableName, strType, dicData):
        if not isinstance(dicData, dict):
            return

        dicCondition = dicData.get('condition')

        lisOrder = self.buildOrder(dicData.get('order'))

        if strType == 'list':
            if dicCondition:
                result = self.db[strTableName].find(dicCondition)
            else:
                result = self.db[strTableName].find()
            if lisOrder:
                result = result.sort(lisOrder)
        else:
            if dicCondition:
                result = self.db[strTableName].find_one(dicCondition)
            else:
                result = self.db[strTableName].find_one()
        return result

    def find(self, strTableName, strType, dicData):
        res = self._find(strTableName, strType, dicData)
        if strType == 'list':
            return [i for i in res]
        return res

    def paginate(self, strTableName, dicData):
        pass

    def getRows(self, strTableName, dicData):
        return self._find(strTableName, 'list', dicData).count()

    def insert(self, strTableName, dicData):
        dicField = dicData.get('fields')
        if dicField:
            self.db[strTableName].insert(dicField)

    def update(self, strTableName, dicData):
        dicField = dicData.get('fields')
        dicCondition = dicData.get('condition')
        if dicField and dicCondition:
            self.db[strTableName].update(dicCondition, {"$set": dicField})
        elif dicField:
            self.db[strTableName].update({}, {"$set": dicField})

    def delete(self, strTableName, dicData):
        dicCondition = dicData.get('condition')
        if dicCondition:
            self.db[strTableName].remove(dicCondition)
        else:
            self.db[strTableName].remove()

    def buildOrder(self, strOrder):
        if not strOrder:
            return
        lisOrder = []
        for item in strOrder.split(','):
            item = item.strip()
            order, orderType = item.split(' ')
            if orderType == 'desc':
                lisOrder.append((order, self.desc))
            else:
                lisOrder.append((order, self.asc))
        return lisOrder

    def finish(self):
        try:
            self.client.close()
        except Exception, e:
            print e
