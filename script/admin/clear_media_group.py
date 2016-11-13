# -*- coding:utf-8 -*-


import sys
sys.path.append('../..')

import time
from script.db_base import  DB
import gflags
# reload(sys)
# sys.setdefaultencoding('utf-8')

PASSTIME = 1296000      # 60*60*24*15  15天,自媒体组的过期时间
ACCESSINDEX = 50        # 最近超过30次，退出用户，并禁用用户
ACCESSTIME = 10        # 最近10秒，退出用户，并禁用用户
# mode = 'dev'
# mode = 'online'
dase = 'DB_PROJECT'
Flags = gflags.FLAGS

def getUserIndex(db, tableName):
    val_time = int(time.time()) - ACCESSTIME
    # print "startTime = {st} and endTime = {et} ".format(st=val_time,et=int(self.time.time()))
    data = db.find(tableName, {
        'fields': ['count(1) as counts'],
        'condition': 'user_id = {Uid} and create_time >= {ct}'.format(Uid=14, ct=val_time)
    })
    return  data['counts']

def delete_user_index(db, tableName):
    val_time = int(time.time()) - PASSTIME   #超过半个月的导出操作记录，清除
    status = db.delete(tableName, {
        'condition': 'create_time < {ct}'.format(ct=val_time)
    })
    return status

def delete_group_index(db, tableName):
    val_time = int(time.time()) - PASSTIME   #超过半个月的自媒体组清除
    status = db.delete(tableName, {
        'condition': 'status=0 and create_time < {ct}'.format(ct=val_time)
    })
    return status

def clear_media_group(mode):
    db = DB(mode, dase)
    tableName = 'yidao_export'
    status = delete_user_index(db, tableName)
    if status and status>0:
        print "delete yidao_export info [counts] = ", status
    else:
        print "delete yidao_export info zero"

    tableName = 'follow_group'
    status = delete_group_index(db, tableName)
    if status and status>0:
        print "delete follow_group info [counts] = ", status
    else:
        print "delete follow_group info zero"

    tableName = 'media_follow'
    status = delete_group_index(db, tableName)
    db.commit()
    if status and status>0:
        print "delete media_follow info [counts] = ", status
    else:
        print "delete media_follow info zero"

if __name__ == "__main__":
    if len(sys.argv)!=2:
        print "Missing Parameters", sys.argv
        sys.exit()
    # python clear_media_group.py online
    mode = sys.argv[1]
    clear_media_group(mode)