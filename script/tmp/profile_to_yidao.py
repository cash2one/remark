# -*- coding: utf-8 -*-

import time
import MySQLdb

DB_HOST = 'rdshf7hicnex6yhgi3h8.mysql.rds.aliyuncs.com'
# dev
# DB_USER = 'yidao_dev'
# DB_PASS = 'byXPqETUBRcBTPJb'
# DB_PROF = 'yidao_profile_dev'
# DB_YIDAO = 'yidao_new'
# on line
DB_USER = 'yidao'
DB_PASS = 'ovPZNfv6kFkYuwRC'
DB_PROF = 'yidao_profile'
DB_YIDAO = 'yidao'
db_prof = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_PROF, use_unicode=1, charset='utf8')
db_yidao = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_YIDAO, use_unicode=1, charset='utf8')

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

yidao_media = findMany(db_yidao, 'media', '*')
yidao_wechat = findMany(db_yidao, 'media_wechat', '*')
yidao_media_ids = set([i[0] for i in yidao_media])
yidao_wechat_ids = set([i[0] for i in yidao_wechat])
yidao_wechat_media_ids = set([i[1] for i in yidao_wechat])
prof_media = findMany(db_prof,
                      'media',
                      'id, user_id, name, brief, identify, avatar, platform_id, category_media_id, status, '
                      'audience_gender, audience_province_id, audience_city_id, audience_county_id, value_level, '
                      'src_type, create_time, media_platform_create_time, last_update_time',
                      'platform_id = 2 and fans_num > 50000 order by last_update_time desc limit 0, 40000')
prof_media_ids = [str(int(j[0])) for j in prof_media]
prof_wechat = findMany(db_prof,
                       'media_wechat',
                       'id, media_id, openid, wechat_id, qrcode, biz, gh_id, original, '
                       'top_avg_read_num, top_three_avg_read_num',
                       'media_id in (%s)' % ','.join(prof_media_ids))

print yidao_media[0]
print yidao_wechat[0]
print prof_media[0]
print prof_wechat[0]


new_media, new_wechat = [], []
total_m = 0
for m in prof_media:
    _id, user_id, name, brief, identify, avatar, platform_id, category_media_id, status, \
    audience_gender, audience_province_id, audience_city_id, audience_county_id, value_level, src_type, \
    create_time, media_platform_create_time, last_update_time = m
    if _id in yidao_media_ids:
        continue
    total_m += 1
    new_media.append([_id, 20038, name, brief, identify, avatar, platform_id, category_media_id, status,
                      audience_gender, audience_province_id, audience_city_id, audience_county_id, value_level, 1,
                      create_time, media_platform_create_time, int(time.time())])
total_w = 0
for w in prof_wechat:
    _id, media_id, openid, wechat_id, qrcode, biz, gh_id, original, top_avg_read_num, top_three_avg_read_num = w
    if media_id in yidao_media_ids or _id in yidao_wechat_ids:
        continue
    total_w += 1
    new_wechat.append([_id, media_id, openid, wechat_id, qrcode, biz, gh_id, original,
                       top_avg_read_num, top_three_avg_read_num])

print total_m, total_w
if total_m > total_w:
    print yidao_media_ids - yidao_wechat_media_ids
elif total_m < total_w:
    print yidao_wechat_media_ids - yidao_media_ids
if new_media:
    insertMany(db_yidao, 'media', new_media)
if new_wechat:
    insertMany(db_yidao, 'media_wechat', new_wechat)

db_yidao.close()
db_prof.close()