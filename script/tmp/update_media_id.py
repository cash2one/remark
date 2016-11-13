# -*- coding:utf-8 -*-


import MySQLdb


# dest
DB_HOST = 'rdshf7hicnex6yhgi3h8.mysql.rds.aliyuncs.com'
DB_USER_NEW = 'yidao_dev'
DB_PASS_NEW = 'byXPqETUBRcBTPJb'
DB_BASE_NEW = 'yidao_profile_dev'

DB_USER = 'yidao'
DB_PASS = 'ZdKnbciJwveyN47w'
DB_BASE = 'yidao'

db = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_BASE, use_unicode=1, charset='utf8')
db_new = MySQLdb.connect(DB_HOST, DB_USER_NEW, DB_PASS_NEW, DB_BASE_NEW, use_unicode=1, charset='utf8')


def findMany(db_obj, tbl_name, str_field, str_cond=''):
    data = None
    cursor = db_obj.cursor()
    if not str_cond:
        sql = 'SELECT {col} FROM {tbl}'.format(col=str_field, tbl=tbl_name)
    else:
        sql = 'SELECT {col} FROM {tbl} WHERE {cond}'.format(col=str_field, tbl=tbl_name, cond=str_cond)
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
    except Exception, e:
        print e
    cursor.close()
    return data


def updateMany(db_obj, data):
    cursor = db_obj.cursor()
    set_str = 'media_id = %s'
    cond_str = 'wx_biz = %s'
    sql = 'UPDATE wechat SET {s} WHERE {c}'.format(s=set_str, c=cond_str)
    print sql
    try:
        row = cursor.executemany(sql, data)
        print row
        db_obj.commit()
    except Exception, e:
        print e
        db_obj.rollback()
    cursor.close()


def insertMany(db_obj, tbl_name, data):
    print 'now, insert tbl:', tbl_name
    cursor = db_obj.cursor()
    value = ', '.join(['%s'] * 24)
    sql = 'INSERT INTO {tbl} VALUES ({val})'.format(tbl=tbl_name, val=value)
    try:
        cursor.executemany(sql, data)
        db_obj.commit()
    except Exception, e:
        print e
        db_obj.rollback()
    cursor.close()


res = set([i[1] for i in findMany(db, 'media_wechat', 'media_id, biz')])
res_new = set(i[0] for i in findMany(db_new, 'wechat', 'biz'))

# updateMany(db_new, res)
datas = findMany(
    db,
    'media_wechat as mw LEFT JOIN media as m ON (m.id = mw.media_id)',
    'mw.media_id, mw.openid, mw.wechat_id, mw.qrcode, mw.biz, m.name, m.brief, m.identify',
    'mw.biz in ("{biz}")'.format(biz='","'.join(res - res_new))
)
# print datas[:20]
new = []
idx = 1110965
for i in datas:
    a1, a2, a3, a4, a5, a6, a7, a8 = i
    new.append([idx, a1, 0, a6, a3, a2, a4, a5, a7, 0, a8, '', 0, 0, 0, '', 0, '', -1, 0, -1, -1, 0, -1])
    idx += 1
# insertMany(db_new, 'wechat', new)

db.close()
db_new.close()
