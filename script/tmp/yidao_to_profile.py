# -*- coding: utf-8 -*-

import time
import MySQLdb

DB_HOST = 'rdshf7hicnex6yhgi3h8.mysql.rds.aliyuncs.com'
# dev
# DB_USER = 'yidao_dev'
# DB_PASS = 'gDAyDf8LK62dts5r'
# DB_PROF = 'yidao_profile_dev'
# DB_YIDAO = 'yidao_new'
# on line
DB_USER = 'yidao'
DB_PASS = ''
DB_PROF = 'yidao_profile'
DB_YIDAO = 'yidao'
db_prof = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_PROF, use_unicode=1, charset='utf8')
db_yidao = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_YIDAO, use_unicode=1, charset='utf8')

# 670461
def findMany(db_obj, tbl_name, str_field, str_cond=''):
    data = None
    cursor = db_obj.cursor()
    if not str_cond:
        sql = 'SELECT {col} FROM {tbl}'.format(col=str_field, tbl=tbl_name)
    else:
        sql = 'SELECT {col} FROM {tbl} WHERE {cond}'.format(col=str_field, tbl=tbl_name, cond=str_cond)
        # print sql
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
    except Exception, e:
        print e
    cursor.close()
    return data


def insertMany(db_obj, tbl_name, data):
    print 'now, insert tbl:', tbl_name
    cursor = db_obj.cursor()
    value = ', '.join(['%s'] * len(data[0]))
    sql = 'INSERT INTO {tbl} VALUES ({val})'.format(tbl=tbl_name, val=value)
    # print sql
    try:
        cursor.executemany(sql, data)
        db_obj.commit()
    except Exception, e:
        print e
        db_obj.rollback()
    cursor.close()


yidao_wechat = findMany(db_yidao, 'media_wechat as mw join media as m on (mw.media_id = m.id)', '*')
prof_wechat = findMany(db_prof, 'media_wechat', 'biz')
dic_yidao_wechat = {i[5]: i for i in yidao_wechat}
yidao_biz = set(dic_yidao_wechat.keys())
prof_biz = set([i[0] for i in prof_wechat])
more = yidao_biz - prof_biz
media_infos = []
wechat_infos = []
num = 5000
if more:
    for i in more:
        print i
        num += 1
        info = dic_yidao_wechat.get(i)
        w1, w2, w3, w4, w5, w6, w7, w8, w9, w10, \
        m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, \
        m11, m12, m13, m14, m15, m16, m17, m18 = info
        wechat_infos.append([num, w2, w3, w4, w5, w6, w7, w8, '', 0, w9, w10, 0])
        media_infos.append([m1, m2, m3, m4, m5, m6, m7, m8, '', m14, m9, m10, '', '', '', '',
                            m11, m12, m13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            '', '', '', '', '', '', 0, m17, m16, m18])


    # insertMany(db_prof, 'media', media_infos)
    # insertMany(db_prof, 'media_wechat', wechat_infos)
else:
    print 'nothing to do.'

db_yidao.close()
db_prof.close()
