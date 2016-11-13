# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

import time
import MySQLdb
from api import crawler

DB_HOST = 'rdshf7hicnex6yhgi3h8.mysql.rds.aliyuncs.com'
# dev
DB_USER = 'yidao_dev'
DB_PASS = 'gDAyDf8LK62dts5r'
DB_PROF = 'yidao_profile_dev'
DB_YIDAO = 'yidao_new'
# on line
# DB_USER = 'yidao'
# DB_PASS = ''
# DB_PROF = 'yidao_profile'
# DB_YIDAO = 'yidao'
db = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_PROF, use_unicode=1, charset='utf8')


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

def update(cursor, tbl, info):
    set_str =','.join(info.get('fields', ''))
    cond_str = info.get('condition', '')
    sql = 'UPDATE {tbl} SET {s} WHERE {c}'.format(tbl=tbl, s=set_str, c=cond_str)
    cursor.execute(sql)

def update_base(db_obj, dicData):
    now = int(time.time())
    cursor = db_obj.cursor()
    media_info = {
        'fields': ['name=\'{name}\''.format(name=dicData['name'].encode('u8')),
                   'brief=\'{brief}\''.format(brief=dicData['features'].replace('"', u'“').encode('u8')),
                   'avatar=\'{avatar}\''.format(avatar=dicData['avatar']),
                   'last_update_time={ut}'.format(ut=now),
                   ],
        'condition': 'id={id}'.format(id=dicData['id'])
    }
    wechat_info = {
        'fields': ['qrcode=\'{qrcode}\''.format(qrcode=dicData['qrcode']),
                   'gh_id=\'{gid}\''.format(gid=dicData['user_name']),
                   'url=\'{url}\''.format(url=dicData['url']),
                   ],
        'condition': 'media_id={id}'.format(id=dicData['id'])
    }
    try:
        update(cursor, 'media', media_info)
        update(cursor, 'media_wechat', wechat_info)
        db_obj.commit()
    except Exception, e:
        print e
        db_obj.rollback()
    cursor.close()

def run():
    media = findMany(db, 'media_wechat', 'media_id, url')
    for item in media:
        media_id, url = item
        if not url:
            print media_id, 'invalid url.'
            continue
        dicInfo = crawler.crawler().official(url, '')
        if not dicInfo.get('name'):
            print media_id, 'get info failed.'
            continue
        dicInfo['id'] = media_id
        dicInfo['url'] = url
        update_base(db, dicInfo)
        print media_id, 'update'
        # break

if __name__ == '__main__':
    run()