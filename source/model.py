# -*- coding:utf-8 -*-

from mysql import MySQL
from mongodb import MongoDB
from redis import Redis

class Model(object):
    ''' 数据类
    '''

    strTableName = ''
    dicConfig = {}
    #status = 200  # 多数据源事务处理

    db   = None
    mongodb = None
    redis   = None

    def init(self, dicConfig):
        ''' 初始化
        '''

        self.dicConfig = dicConfig
        
        if self.dicConfig['isDataBase']:
            self.db = MySQL()
            self.db.init(self.dicConfig)

        if self.dicConfig['isMongoDB']:
            self.mongodb = MongoDB()
            self.mongodb.init(self.dicConfig)

        if self.dicConfig['isRedis']:
            self.redis = Redis()
            self.redis.init(self.dicConfig)

    def finish(self):
        if self.dicConfig['isDataBase']:
            self.db.finish()
        if self.dicConfig['isMongoDB']:
            self.mongodb.finish()
        if self.dicConfig['isRedis']:
            self.redis.finish()
