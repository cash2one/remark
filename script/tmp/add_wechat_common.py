# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append("..")

import time
import xlrd
from db_base import DB

mode = 'dev'
config = {
    'dev': {'yidao_db': 'yidao_new', 'yidao_pf': 'yidao_profile_dev'},
    'online': {'yidao_db': 'yidao', 'yidao_pf': 'yidao_profile'},
}
wechat_col = ['media_id', 'openid', 'wechat_id', 'qrcode', 'biz', 'gh_id', 'original', 'url',
              'top_avg_read_num', 'top_three_avg_read_num', 'like_num']
wechat_col = set(wechat_col)

db = DB(mode)

def get_category():
    category = {}
    res = db.find(config.get(mode, {}).get('yidao_db') + '.category_media', 'list', {})
    for i in res:
        names = i.get('name', '').split('/')
        _id = i.get('id')
        for name in names:
            if not name:
                continue
            category.setdefault(name[:2], _id)
    return category


def get_tag():
    tag = {}
    res = db.find(config.get(mode, {}).get('yidao_db') + '.tag', 'list', {})
    for i in res:
        name = i.get('name')
        _id = i.get('id')
        tag.setdefault(name[:2], _id)
    return tag


def get_area():
    area = {}
    res = db.find(config.get(mode, {}).get('yidao_db') + '.area', 'list', {})
    for i in res:
        name = i.get('name')[:2]
        _id = i.get('id')
        area.setdefault(name, _id)
    return area

categories = get_category()
tags = get_tag()
areas = get_area()


def format_area(area):
    try:
        rtn = areas.get(area[:2], 0)
    except:
        rtn = 0
    return rtn

def format_category(category):
    try:
        category = category[:2]
        rtn = categories.get(category, 0)
    except:
        rtn = 0
    return rtn

def format_tags(category):
    try:
        for i in ['、', ',', '/', ' ', '\t', '|']:
            if i in category:
                cts = [j.strip() for j in category.split(i)]
                break
        else:
            cts = [category]
        rtns = [tags.get(k[:2]) for k in cts]
    except:
        rtns = []
    return ', '.join([str(s) for s in rtns if s])

def format_name(name):
    if not isinstance(name, basestring):
       name = str(name)
    rtn = name.strip()
    if name.endswith('V'):
        rtn = name[:-1]
    return rtn

def format_wechat_id(wechat_id):
    try:
        wechat_id = wechat_id.strip()
    except:
        wechat_id = ''
    return wechat_id

def format_price(price):
    try:
        rtn = int(price)
    except:
        rtn = 0
    return rtn

def format_text(text):
    if not isinstance(text, basestring):
       text = str(text)
    return text.replace('"', '\'')

def format_num(num):
    num = str(num).lower().strip('+')
    num = num.replace(',', '')
    num = num.replace(' ', '')
    num = num.replace('，', '')
    if not num:
        return 0
    try:
        if num.endswith('w'):
            rtn = float(num[:-1])*10000
        elif num.endswith('k'):
            rtn = float(num[:-1])*1000
        else:
            rtn = int(float(num))
    except Exception, e:
        print e
        rtn = 0
    return rtn

# def format_contact(num):
#     if isinstance(num, basestring):
#         return num.strip()
#     return str(int(num)) if num else ''


def into_db(dicData):
    # print dicData
    wechat_id = dicData.get('wechat_id', '')
    if not wechat_id:
        return
    res = db.find('media_wechat', 'first', {
        'condition': 'wechat_id = "%s"' % wechat_id
    })
    now = int(time.time())
    if res:
        print 'update >>>'
        fp_old = res.get('first_price', 0)
        sp_old = res.get('second_price', 0)
        op_old = res.get('other_price', 0)
        idy = res.get('identify', '')
        dicData['first_price'] = dicData.get('first_price', 0) if dicData.get('first_price', 0) > fp_old else fp_old
        dicData['second_price'] = dicData.get('second_price', 0) if dicData.get('second_price', 0) > sp_old else sp_old
        dicData['other_price'] = dicData.get('other_price', 0) if dicData.get('other_price', 0) > op_old else op_old
        dicData['identify'] = dicData.get('identify', '') if len(dicData.get('identify', '')) > len(idy) else idy
        media_id = res.get('media_id')
        media_fields = ['last_update_time=%s' % now]
        wechat_fields = []
        for key in dicData:
            value = dicData[key]
            if not value:
                continue
            if key in wechat_col:
                wechat_fields.append('%s="%s"' % (key, value))
            else:
                media_fields.append('%s="%s"' % (key, value))
        db.update('media', {
            'fields': media_fields,
            'condition': 'id = "%s"' % media_id
        })
        if wechat_fields:
            db.update('media_wechat', {
                'fields': wechat_fields,
                'condition': 'media_id = "%s"' % media_id
            })
    else:
        print 'insert >>>'
        media_key = 'src_type, create_time, last_update_time'
        wechat_key = 'media_id'
        media_cols, media_values = [], []
        wechat_cols, wechat_values = [], []
        for key in dicData:
            value = dicData[key]
            if not value:
                continue
            if key in wechat_col:
                wechat_cols.append(key)
                wechat_values.append('"%s"' % value)
            else:
                media_cols.append(key)
                media_values.append('"%s"' % value)
        if media_cols:
            media_key = ', '.join(media_cols) + ', ' + media_key
        if wechat_cols:
            wechat_key = wechat_key + ', ' + ', '.join(wechat_cols)
        media_value =  '%s, %s, %s' % (2, now, now)
        db.insert('media', {
            'key': media_key,
            'val': ', '.join(media_values) + ', ' + media_value
        })
        media_id = db.cursor.lastrowid
        wechat_value = '%s' % media_id
        db.insert('media_wechat', {
            'key': wechat_key,
            'val': wechat_value + ', ' + ', '.join(wechat_values)
        })

def read_excel(file_name):
    excel = xlrd.open_workbook(file_name)
    sheet = excel.sheet_by_index(0)
    rows = sheet.nrows
    for i in range(1, rows):
        items = sheet.row_values(i)
        name, wechat_id, fp, sp, op, read_num, t_read_num, lm, fans_num, ct, \
        tg, idy, area, city, brief, remark, person, phone, qq, wechat, email = items[:21]
        # name, wechat_id, fp, sp, op, read_num, t_read_num, lm, fans_num, ct, tg, idy, area, city, brief, remark = items[:16]
        tag = tg if tg else ct
        cat = ct if ct else tg
        yield {
            'category_media_id': format_category(cat),
            'tags': format_tags(tag),
            'name': format_name(name),
            'wechat_id': format_wechat_id(wechat_id),
            'fans_num': format_num(fans_num),
            'brief': format_text(brief),
            'audience_province_id': format_area(area),
            'top_three_avg_read_num': format_num(read_num),
            'like_num': format_num(lm),
            'top_avg_read_num': format_num(t_read_num),
            'first_price': format_price(fp),
            'second_price': format_price(sp),
            'other_price': format_price(op),
            'remark': remark,
            # 'remark': '总阅读数：%s，最高阅读数：%s，wci：%s' % (u2, u3, u4),
            # 'contact_person': person,
            # 'contact_phone': format_contact(phone),
            # 'contact_qq': format_contact(qq),
            # 'contact_wechat': wechat,
            # 'contact_email': email,
        }


if __name__ == '__main__':
    for i in read_excel('1.xlsx'):
        for k in i:
            if isinstance(i[k], basestring):
                print k, i[k].encode('u8'), '\t',
            else:
                print k, i[k], '\t',
        print
        into_db(i)
    db.commit()

