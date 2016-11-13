# -*- coding:utf-8 -*-

import time
import MySQLdb

DB_HOST = 'rdshf7hicnex6yhgi3h8.mysql.rds.aliyuncs.com'
# dev
DB_USER = 'yidao_dev'
DB_PASS = 'byXPqETUBRcBTPJb'
DB_BASE = 'yidao_new'
DB_PROF = 'yidao_profile_dev'

# ol
DB_USER_OL = 'yidao'
DB_PASS_OL = ''
DB_BASE_OL = 'yidao'

db_base = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_BASE, use_unicode=1, charset='utf8')
db_prof = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_PROF, use_unicode=1, charset='utf8')
db_ol = MySQLdb.connect(DB_HOST, DB_USER_OL, DB_PASS_OL, DB_BASE_OL, use_unicode=1, charset='utf8')

now = int(time.time())


def findMany(db_obj, tbl_name):
    data = None
    cursor = db_obj.cursor()
    sql = 'SELECT * FROM {tbl}'.format(tbl=tbl_name)
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
    except Exception, e:
        print e
    cursor.close()
    return data


def findPart(db_obj, tbl_name, lt, rt):
    data = None
    cursor = db_obj.cursor()
    sql = 'SELECT * FROM {tbl} WHERE id BETWEEN {lt} AND {rt}'.format(tbl=tbl_name, lt=lt, rt=rt)
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
    try:
        cursor.executemany(sql, data)
        db_obj.commit()
    except Exception, e:
        print e
        db_obj.rollback()
    cursor.close()


def update_from_media():
    media = findMany(db_ol, 'media')
    medias = [i[:-3] + (0, 0, '', '', 0) + i[-3:] for i in media]
    insertMany(db_prof, 'media', medias)


def update_from_media_wechat():
    media_wechat = findMany(db_ol, 'media_wechat')
    insertMany(db_prof, 'media_wechat', media_wechat)


def update_from_wechat():
    step = 10000
    for i in range(0, 800000 - step, step):
        # -1 避免右区间重复
        rt = i + step - 1
        print 'do part {l}~{r}...'.format(l=i, r=rt)
        wechat = findPart(db_prof, 'wechat', i, rt)
        if not wechat:
            continue
        media = []
        media_wechat = []
        for row in wechat:
            a1, a2, a3, a4, a5, a6, a7, a8, a9, b1, b2, b3, b4, b5, b6, b7, b8 = row
            if a2:
                continue
            idx = 20000 + a1
            p1 = [idx, 0, a3, a8, b1, '', 2, 0, 0, 0, 0, None, None, -1, 0, 0, '', '', 1, b8, 0, b6]
            p2 = [idx, idx, a5, a4, a6, a7, '', b2, 0, 0]
            media.append(p1)
            media_wechat.append(p2)
        # print media
        # print media_wechat
        insertMany(db_prof, 'media', media)
        insertMany(db_prof, 'media_wechat', media_wechat)
        # break


def run_all():
    update_from_media()
    update_from_media_wechat()
    update_from_wechat()


run_all()

db_base.close()
db_prof.close()
db_ol.close()
