# -*- coding:utf-8 -*-


import sys
sys.path.append('../..')

import time
from script.db_base import  DB
import gflags
# reload(sys)
# sys.setdefaultencoding('utf-8')

PASSTIME = 1296000      # 60*60*24*15  15天,用户操作的模块记录的过期时间
ACCESSINDEX = 50        # 最近超过30次，退出用户，并禁用用户
ACCESSTIME = 10        # 最近10秒，退出用户，并禁用用户

# mode = 'dev'
# mode = 'online'
dase = 'DB_ADMIN'
Flags = gflags.FLAGS

def getUserIndex(db, tableName):
    val_time = int(time.time()) - ACCESSTIME
    # print "startTime = {st} and endTime = {et} ".format(st=val_time,et=int(self.time.time()))
    data = db.find(tableName, {
        'fields': ['count(1) as counts'],
        'condition': 'user_id = {Uid} and create_time >= {ct}'.format(Uid=14, ct=val_time)
    })
    return  data['counts']

def deleteUserIndex(db, tableName):
    val_time = int(time.time()) - PASSTIME   #超过半个月的用户操作记录，清除
    status = db.delete(tableName, {
        'condition': 'create_time < {ct}'.format(ct=val_time)
    })
    db.commit()
    return status

def clear_user_access(mode):
    db = DB(mode, dase)
    tableName = 'user_access_permission'
    # counts = getUserIndex(db, tableName)
    # if counts:
    #     status = deleteUserIndex(db, tableName)
    #     print "status = ", status
    status = deleteUserIndex(db, tableName)
    if status and status>0:
        print "delete user info [counts] = ", status
    else:
        print "delete user info zero"

if __name__ == "__main__":
    if len(sys.argv)!=2:
        print "Missing Parameters", sys.argv
        sys.exit()
    # python clear_user_access.py online
    mode = sys.argv[1]
    clear_user_access(mode)