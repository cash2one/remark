# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append("..")

import time
import xlrd
from db_base import DB
from api import crawler

mode = 'online'
config = {
    'dev': {'yidao_db': 'yidao_new', 'yidao_pf': 'yidao_profile_dev'},
    'online': {'yidao_db': 'yidao', 'yidao_pf': 'yidao_profile'},
}

db = DB(mode)
craw = crawler.crawler()

def get_category():
    category = {}
    res = db.find(config.get(mode, {}).get('yidao_db') + '.category_media', 'list', {})
    for i in res:
        names = i.get('name', '').split('/')
        _id = i.get('id')
        for name in names:
            if not name:
                continue
            category.setdefault(name, _id)
    return category


def get_tag():
    tag = {}
    res = db.find(config.get(mode, {}).get('yidao_db') + '.tag', 'list', {})
    for i in res:
        name = i.get('name')
        _id = i.get('id')
        tag.setdefault(name, _id)
    return tag


def get_area():
    area = {}
    res = db.find(config.get(mode, {}).get('yidao_db') + '.area', 'list', {})
    for i in res:
        name = i.get('name')[:2]
        _id = i.get('id')
        area.setdefault(name, _id)
    return area


def read_wechat_1():
    categories = get_category()
    tags = get_tag()
    areas = get_area()
    excel = xlrd.open_workbook('2.xlsx')
    sheet = excel.sheet_by_index(0)
    rows = sheet.nrows
    for i in range(1, rows):
        items = sheet.row_values(i)
        name, wehchat_id, tp, fans_num, area, ct, brief = items[2:]
        cts = [str(tags.get(t, '')) for t in ct.split('|')]
        tag = ','.join([t for t in cts if t])
        ccs = [str(categories.get(t, '')) for t in ct.split('|')]
        category = [c for c in ccs if c]
        category = str(category[0]) if category else ''
        area = areas.get(area, 0)
        yield {'name': name, 'wechat_id': wehchat_id, 'fans_num': fans_num,
               'area': area, 'category': category, 'tag': tag, 'brief': brief}


def read_wechat_2():
    categories = get_category()
    tags = get_tag()
    areas = get_area()
    excel = xlrd.open_workbook('1.xlsx')
    sheet = excel.sheet_by_index(0)
    rows = sheet.nrows
    for i in range(1, rows):
        items = sheet.row_values(i)
        # print items
        _id, name, wechat_id, fans_num, price, price_mark, identify, avg_num, like_num, category, tip, province, city = items
        # print _id, name, wechat_id, fans_num, price, price_mark, identify, avg_num, like_num, category, tip, province, city
        if price_mark == u'次条' or price_mark == u'非头条':
            f_price, s_price, o_price = 0, price, 0
        elif price_mark == u'末条' or price_mark == '文案询价':
            f_price, s_price, o_price = 0, 0, price
            tip = price_mark + u', ' + tip
        else:
            f_price, s_price, o_price = price, 0, 0
        nm_category = category_2().get(category)
        if nm_category:
            ct = categories.get(nm_category, 26)
        else:
            ct = 26
            tip = category + ', ' + tip
        nm_tag = tag_2().get(category, [])
        tg = ','.join([str(tags.get(j)) for j in nm_tag if tags.get(j)])
        province = areas.get(province, 0)
        city = areas.get(city, 0)
        fans_num = str(fans_num).strip('?')
        # if i == 200:
        #     break
        res = {'name': name, 'wechat_id': wechat_id, 'fans_num':fans_num if fans_num else 0, 'first_price': f_price,
               'second_price': s_price, 'other_price': o_price, 'identify': identify, 'tag': tg,
               'top_three_avg_read_num': avg_num if avg_num else 0, 'like_num': like_num if like_num else 0,
               'category_media_id': ct, 'remark': tip, 'audience_province_id': province, 'audience_city_id': city}
        print res
        yield res
        # for k in res:
        #     print k, res[k].encode('u8') if isinstance(res[k], unicode) else res[k],
        # print

def read_wechat_3():
    excel = xlrd.open_workbook('3.xlsx')
    sheet = excel.sheet_by_index(0)
    rows = sheet.nrows
    for i in range(1, rows):
        items = sheet.row_values(i)
        unuse, category, tp, area, name, wechat_id, fans_num = items
        category = 18
        tag = 14
        area = 0
        # print category, tag, area, name.encode('u8'), wechat_id.encode('u8'), fans_num
        yield {
            'category_media_id':category, 'tag':str(tag), 'name':name, 'wechat_id':wechat_id,
            'audience_province_id': area, 'fans_num': fans_num
        }


def read_wechat_4():
    categories = get_category()
    tags = get_tag()
    excel = xlrd.open_workbook('4.xls')
    sheet = excel.sheet_by_index(0)
    rows = sheet.nrows
    for i in range(1, rows):
        items = sheet.row_values(i)
        name, wechat_id, category, sex, sigle, first_price, second_price, other_price, url = items[:9]
        try:
            first_price = int(first_price)
        except:
            first_price = 0
        category_media_id = categories.get(category, 26)
        tag = tags.get(category, '')
        wechat_more = craw.official(url, '', False) if url else {}
        c_wechat_id = wechat_more.get('wechat_id', '')
        c_avatar = wechat_more.get('avatar', '')
        c_name = wechat_more.get('name', '')
        c_biz = wechat_more.get('biz', '')
        c_qrcode = wechat_more.get('qrcode', '')
        c_gh_id = wechat_more.get('user_name', '')
        c_brief = wechat_more.get('features', '')
        c_brief = c_brief.replace("'", "")
        c_brief = c_brief.replace('"', "")
        if not c_wechat_id:
            c_wechat_id = c_gh_id
        if wechat_id != c_wechat_id and c_wechat_id != '':
            print 'unmatch %s' % wechat_id.encode('u8')
        print name.encode('u8'), wechat_id.encode('u8'),category.encode('u8'), sex, sigle, first_price, second_price, other_price
        yield {
            'name': name, 'wechat_id': wechat_id, 'first_price': first_price if first_price else 0,
            'second_price': second_price if second_price else 0, 'other_price': other_price if other_price else 0,
            'tag': tag, 'category_media_id': category_media_id, 'avatar': c_avatar,
            'biz':c_biz, 'qrcode':c_qrcode, 'brief':c_brief, 'gh_id':c_gh_id, 'url': url
        }

def read_wechat_5():
    categories = get_category()
    tags = get_tag()
    excel = xlrd.open_workbook('5.xls')
    sheet = excel.sheet_by_index(0)
    rows = sheet.nrows
    for i in range(1, rows):
        items = sheet.row_values(i)
        name, wechat_id, category, sex, sigle, first_price, second_price, other_price, url, contact= items[:10]
        try:
            first_price = int(first_price)
        except:
            first_price = 0
        try:
            second_price = int(second_price)
        except:
            second_price = 0
        try:
            other_price = int(other_price)
        except:
            other_price = 0
        category_media_id = categories.get(category, 26)
        tag = tags.get(category, '')
        try:
            wechat_more = craw.official(url, '', False) if url else {}
        except:
            wechat_more = {}
        c_wechat_id = wechat_more.get('wechat_id', '')
        c_avatar = wechat_more.get('avatar', '')
        c_name = wechat_more.get('name', '')
        c_biz = wechat_more.get('biz', '')
        c_qrcode = wechat_more.get('qrcode', '')
        c_gh_id = wechat_more.get('user_name', '')
        c_brief = wechat_more.get('features', '')
        c_brief = c_brief.replace("'", "")
        c_brief = c_brief.replace('"', "")
        if not c_wechat_id:
            c_wechat_id = c_gh_id
        if wechat_id != c_wechat_id and c_wechat_id != '':
            print 'unmatch %s' % wechat_id.encode('u8')
        print name.encode('u8'), wechat_id.encode('u8'),category.encode('u8'), first_price, second_price, other_price
        yield {
            'name': name, 'wechat_id': wechat_id, 'first_price': first_price if first_price else 0,
            'second_price': second_price if second_price else 0, 'other_price': other_price if other_price else 0,
            'tag': tag, 'category_media_id': category_media_id, 'avatar': c_avatar,
            'biz':c_biz, 'qrcode':c_qrcode, 'brief':c_brief, 'gh_id':c_gh_id, 'url': url
        }
        # break

def read_wechat_6():
    excel = xlrd.open_workbook('6.xlsx')
    sheet = excel.sheet_by_index(0)
    rows = sheet.nrows
    for i in range(1, rows):
        items = sheet.row_values(i)
        _id, name, wechat_id, first_price, second_price, fans_num = items
        identify = ''
        if name.endswith('V'):
            name = name[:-1]
            identify = u'认证'
        fans_num = fans_num * 10000
        yield {
            'name': name, 'wechat_id': wechat_id, 'identify':identify, 'first_price':first_price,
            'second_price':second_price, 'fans_num':fans_num
        }

def read_wechat_7():
    excel = xlrd.open_workbook('7.xls')
    sheet = excel.sheet_by_index(0)
    rows = sheet.nrows
    for i in range(1, rows):
        items = sheet.row_values(i)
        if not items:
            continue
        wechat_id, name, contact_person, u1, q_str, u2, e_str, u3, t_str, u4, remark = items[:11]
        try:
            qq = q_str[3:]
        except:
            qq = q_str
        try:
            email = e_str[3:]
        except:
            email = e_str
        try:
            tel = t_str[3:]
        except:
            tel = t_str
        yield {
            'name': name, 'wechat_id': wechat_id, 'contact_person':contact_person, 'qq':qq,
            'email':email, 'tel':tel, 'remark':remark
        }

def read_wechat_9():
    excel = xlrd.open_workbook('9.xls')
    sheet = excel.sheet_by_index(0)
    rows = sheet.nrows
    for i in range(1, rows):
        items = sheet.row_values(i)
        if not items:
            continue
        wechat_id, email, name, gh_id = items[:4]
        if not gh_id.startswith('gh'):
            continue
        gh_id = gh_id[:15]
        yield {
            'name': name, 'wechat_id': wechat_id,
            'email':email, 'gh_id': gh_id
        }

def read_wechat_8():
    excel = xlrd.open_workbook('8.xlsx')
    sheet = excel.sheet_by_index(0)
    rows = sheet.nrows
    for i in range(1, rows):
        items = sheet.row_values(i)
        if not items:
            continue
        u1, u2, name, wechat_id = items[:4]
        wechat_id=wechat_id.strip()
        yield {
            'name': name, 'wechat_id': wechat_id,
        }


def category_2():
    return {u'财经': u'金融/保险', u'购物': u'', u'互联网': u'互联网', u'家居房产': u'家居', u'健康养生': u'医疗/健康',
            u'教育培训': u'教育/培训', u'科技IT': u'科技/3C', u'旅游摄影': u'旅游', u'美容瘦身': u'美容', u'美食': u'食品/餐饮',
            u'母婴育儿': u'母婴/儿童', u'汽车': u'汽车/交通', u'情感': u'情感', u'情歌': u'', u'生活': u'生活',
            u'时尚': u'', u'体育锻炼': u'运动/健身', u'新闻资讯': u'媒体/杂志', u'星座命理': u'',
            u'幽默': u'', u'游戏动漫': u'游戏/软件', u'娱乐': u'娱乐/明星', u'职场': u''}


def tag_2():
    return {u'财经': [], u'购物': [u'网购'], u'互联网': [], u'家居房产': [u'房地产', u'家居'], u'健康养生': [u'健康'],
            u'教育培训': [u'教育'], u'科技IT': [u'科技'], u'旅游摄影': [u'旅行'], u'美容瘦身': [u'美容'], u'美食': [u'美食'],
            u'母婴育儿': [u'母婴'], u'汽车': [u'汽车'], u'情感': [u'情感'], u'情歌': [], u'生活': [u'生活'],
            u'时尚': [u'时尚'], u'体育锻炼': [u'体娱', u'运动'], u'新闻资讯': [u'资讯'], u'星座命理': [],
            u'幽默': [u'幽默'], u'游戏动漫': [u'游戏'], u'娱乐': ['体娱'], u'职场': [u'职场']}


def into_db_1(dicData):
    print dicData
    wechat_id = dicData.get('wechat_id', '')
    print wechat_id.encode('u8')
    res = db.find('media_wechat', 'first', {
        'condition': 'wechat_id = "%s"' % wechat_id
    })
    now = int(time.time())
    if res:
        media_id = res.get('media_id')
        db.update('media', {
            'fields': ['name=\'{name}\''.format(name=dicData['name']),
                       'brief=\'{bf}\''.format(bf=dicData['brief']),
                       'fans_num={fn}'.format(fn=dicData['fans_num']),
                       'audience_province_id={apid}'.format(apid=dicData['area']),
                       'category_media_id=\'{cmid}\''.format(cmid=dicData['category']),
                       'tags=\'{tags}\''.format(tags=dicData['tag']),
                       'last_update_time={ut}'.format(ut=now),
                       ],
            'condition': 'id={id}'.format(id=media_id)
        })
    else:
        db.insert('media', {
            'key': 'name, brief, fans_num, audience_province_id, category_media_id, tags, src_type, '
                   'create_time, last_update_time',
            'val': '"%s", "%s", %s, %s, "%s", "%s", %s, %s, %s' % (
                dicData['name'], dicData['brief'], dicData['fans_num'], dicData['area'],
                dicData['category'], dicData['tag'], 2, now, now)
        })
        media_id = db.cursor.lastrowid
        db.insert('media_wechat', {
            'key': 'media_id, wechat_id, biz',
            'val': '%s, "%s", "%s"' % (media_id, dicData['wechat_id'], '')
        })


def into_db_2(dicData):
    print dicData
    wechat_id = dicData.get('wechat_id', '')
    print wechat_id.encode('u8')
    res = db.find('media_wechat', 'first', {
        'condition': 'wechat_id = "%s"' % wechat_id
    })
    now = int(time.time())
    if res:
        media_id = res.get('media_id')
        fields = ['name=\'{name}\''.format(name=dicData['name']),
                   'identify=\'{iy}\''.format(iy=dicData['identify']),
                   'fans_num={fn}'.format(fn=dicData['fans_num']),
                   'audience_province_id={apid}'.format(apid=dicData['audience_province_id']),
                   'audience_city_id={acid}'.format(acid=dicData['audience_city_id']),
                   'category_media_id=\'{cmid}\''.format(cmid=dicData['category_media_id']),
                   'tags=\'{tags}\''.format(tags=dicData['tag']),
                   'remark=\'{remark}\''.format(remark=dicData['remark']),
                   'last_update_time={ut}'.format(ut=now),
                    ]
        if dicData['first_price']:
            fields.append('first_price={fp}'.format(fp=dicData['first_price']))
        if dicData['second_price']:
            fields.append('first_price={sp}'.format(sp=dicData['second_price']))
        if dicData['other_price']:
            fields.append('first_price={op}'.format(op=dicData['other_price']))
        db.update('media', {
            'fields': fields,
            'condition': 'id={id}'.format(id=media_id)
        })
        db.update('media_wechat', {
            'fields': ['top_three_avg_read_num={tn}'.format(tn=dicData['top_three_avg_read_num']),
                       'like_num={ln}'.format(ln=dicData['like_num']),
                       ],
            'condition': 'media_id={id}'.format(id=media_id)
        })
    else:
        db.insert('media', {
            'key': 'name, identify, fans_num, first_price, second_price, other_price, '
                   'audience_province_id, audience_city_id, category_media_id, tags, src_type, '
                   'remark, create_time, last_update_time',
            'val': '"%s", "%s", %s, %s, %s, %s, %s, %s, %s, "%s", %s, "%s", %s, %s' % (
                dicData['name'], dicData['identify'], dicData['fans_num'],
                dicData['first_price'], dicData['second_price'], dicData['other_price'],
                dicData['audience_province_id'], dicData['audience_city_id'],
                dicData['category_media_id'], dicData['tag'], 2, dicData['remark'], now, now)
        })
        media_id = db.cursor.lastrowid
        db.insert('media_wechat', {
            'key': 'media_id, wechat_id, biz, top_three_avg_read_num, like_num',
            'val': '%s, "%s", "%s", %s, %s' % (
                media_id, dicData['wechat_id'], '', dicData['top_three_avg_read_num'], dicData['like_num']
            )
        })

def into_db_3(dicData):
    print dicData
    wechat_id = dicData.get('wechat_id', '')
    print wechat_id.encode('u8')
    res = db.find('media_wechat', 'first', {
        'condition': 'wechat_id = "%s"' % wechat_id
    })
    now = int(time.time())
    if res:
        print 'update'
        media_id = res.get('media_id')
        db.update('media', {
            'fields': ['name=\'{name}\''.format(name=dicData['name']),
                       'fans_num={fn}'.format(fn=dicData['fans_num']),
                       'audience_province_id={apid}'.format(apid=dicData['audience_province_id']),
                       'category_media_id=\'{cmid}\''.format(cmid=dicData['category_media_id']),
                       'tags=\'{tags}\''.format(tags=dicData['tag']),
                       'last_update_time={ut}'.format(ut=now),
                       ],
            'condition': 'id={id}'.format(id=media_id)
        })
    else:
        print 'insert'
        db.insert('media', {
            'key': 'name, fans_num, audience_province_id, category_media_id, tags, src_type, '
                   'create_time, last_update_time',
            'val': '"%s", %s, %s, "%s", "%s", %s, %s, %s' % (
                dicData['name'], dicData['fans_num'], dicData['audience_province_id'],
                dicData['category_media_id'], dicData['tag'], 2, now, now)
        })
        media_id = db.cursor.lastrowid
        db.insert('media_wechat', {
            'key': 'media_id, wechat_id, biz',
            'val': '%s, "%s", "%s"' % (media_id, dicData['wechat_id'], '')
        })

def into_db_4(dicData):
    print dicData
    wechat_id = dicData.get('wechat_id', '')
    print wechat_id.encode('u8')
    res = db.find('media_wechat', 'first', {
        'condition': 'wechat_id = "%s"' % wechat_id
    })
    now = int(time.time())
    if res:
        print 'update'
        media_id = res.get('media_id')
        db.update('media', {
            'fields': ['name=\'{name}\''.format(name=dicData['name']),
                       'brief=\'{brief}\''.format(brief=dicData['brief']),
                       'avatar=\'{avatar}\''.format(avatar=dicData['avatar']),
                       'category_media_id=\'{cmid}\''.format(cmid=dicData['category_media_id']),
                       'tags=\'{tags}\''.format(tags=dicData['tag']),
                       'first_price={fp}'.format(fp=dicData['first_price']),
                       'second_price={sp}'.format(sp=dicData['second_price']),
                       'other_price={op}'.format(op=dicData['other_price']),
                       'last_update_time={ut}'.format(ut=now),
                       ],
            'condition': 'id={id}'.format(id=media_id)
        })
    else:
        print 'insert'
        db.insert('media', {
            'key': 'name, brief, avatar, category_media_id, tags, src_type, first_price, second_price, other_price, '
                   'create_time, last_update_time',
            'val': '"%s", "%s", "%s", "%s", "%s", %s, %s, %s, %s, %s, %s' % (
                dicData['name'], dicData['brief'], dicData['avatar'],
                dicData['category_media_id'], dicData['tag'], 2,
                dicData['first_price'],dicData['second_price'], dicData['other_price'],
                now, now)
        })
        media_id = db.cursor.lastrowid
        db.insert('media_wechat', {
            'key': 'media_id, wechat_id, biz, qrcode, url, gh_id',
            'val': '%s, "%s", "%s", "%s", "%s", "%s"' % (
                media_id, dicData['wechat_id'], dicData['biz'], dicData['qrcode'], dicData['url'], dicData['gh_id'])
        })

def into_db_6(dicData):
    print dicData
    wechat_id = dicData.get('wechat_id', '')
    print wechat_id.encode('u8')
    res = db.find('media_wechat', 'first', {
        'condition': 'wechat_id = "%s"' % wechat_id
    })
    now = int(time.time())
    if res:
        print 'update'
        media_id = res.get('media_id')
        db.update('media', {
            'fields': ['name=\'{name}\''.format(name=dicData['name']),
                       'fans_num={fn}'.format(fn=dicData['fans_num']),
                       'identify=\'{ify}\''.format(ify=dicData['identify']),
                       'first_price={fp}'.format(fp=dicData['first_price']),
                       'second_price={sp}'.format(sp=dicData['second_price']),
                       'last_update_time={ut}'.format(ut=now),
                       ],
            'condition': 'id={id}'.format(id=media_id)
        })
    else:
        print 'insert'
        db.insert('media', {
            'key': 'name, fans_num, identify, first_price, second_price, src_type, '
                   'create_time, last_update_time',
            'val': '"%s", %s, "%s", %s, %s, %s, %s, %s' % (
                dicData['name'], dicData['fans_num'], dicData['identify'],
                dicData['first_price'], dicData['second_price'], 2, now, now)
        })
        media_id = db.cursor.lastrowid
        db.insert('media_wechat', {
            'key': 'media_id, wechat_id, biz',
            'val': '%s, "%s", "%s"' % (media_id, dicData['wechat_id'], '')
        })


def into_db_7(dicData):
    print dicData
    wechat_id = dicData.get('wechat_id', '')
    print wechat_id.encode('u8')
    res = db.find('media_wechat', 'first', {
        'condition': 'wechat_id = "%s"' % wechat_id
    })
    now = int(time.time())
    if res:
        print 'update'
        media_id = res.get('media_id')
        db.update('media', {
            'fields': ['name=\'{name}\''.format(name=dicData['name']),
                       'contact_person=\'{cpe}\''.format(cpe=dicData['contact_person']),
                       'contact_qq=\'{cq}\''.format(cq=dicData['qq']),
                       'contact_email=\'{ce}\''.format(ce=dicData['email']),
                       'contact_phone=\'{cph}\''.format(cph=dicData['tel']),
                       'remark=\'{remark}\''.format(remark=dicData['remark']),
                       'last_update_time={ut}'.format(ut=now),
                       ],
            'condition': 'id={id}'.format(id=media_id)
        })
    else:
        print 'insert'
        db.insert('media', {
            'key': 'name, contact_person, contact_qq, contact_email, contact_phone, remark, src_type, '
                   'create_time, last_update_time',
            'val': '"%s", "%s", "%s", "%s", "%s", "%s", %s, %s, %s' % (
                dicData['name'], dicData['contact_person'], dicData['qq'], dicData['email'],
                dicData['tel'], dicData['remark'], 2, now, now)
        })
        media_id = db.cursor.lastrowid
        db.insert('media_wechat', {
            'key': 'media_id, wechat_id, biz',
            'val': '%s, "%s", "%s"' % (media_id, dicData['wechat_id'], '')
        })

def into_db_9(dicData):
    print dicData
    wechat_id = dicData.get('wechat_id', '')
    print wechat_id.encode('u8')
    res = db.find('media_wechat', 'first', {
        'condition': 'wechat_id = "%s"' % wechat_id
    })
    now = int(time.time())
    if res:
        print 'update'
        media_id = res.get('media_id')
        db.update('media', {
            'fields': ['name=\'{name}\''.format(name=dicData['name']),
                       'contact_email=\'{ce}\''.format(ce=dicData['email']),
                       'last_update_time={ut}'.format(ut=now),
                       ],
            'condition': 'id={id}'.format(id=media_id)
        })
    else:
        print 'insert'
        db.insert('media', {
            'key': 'name, contact_email, src_type, '
                   'create_time, last_update_time',
            'val': '"%s", "%s", %s, %s, %s' % (
                dicData['name'], dicData['email'], 2, now, now)
        })
        media_id = db.cursor.lastrowid
        db.insert('media_wechat', {
            'key': 'media_id, wechat_id, biz, gh_id',
            'val': '%s, "%s", "%s", "%s"' % (media_id, dicData['wechat_id'], '', dicData['gh_id'])
        })

def into_db_8(dicData):
    print dicData
    wechat_id = dicData.get('wechat_id', '')
    print wechat_id.encode('u8')
    res = db.find('media_wechat', 'first', {
        'condition': 'wechat_id = "%s"' % wechat_id
    })
    now = int(time.time())
    if res:
        print 'update'
        media_id = res.get('media_id')
        db.update('media', {
            'fields': [
                       'last_update_time={ut}'.format(ut=now),
                       ],
            'condition': 'id={id}'.format(id=media_id)
        })
    else:
        print 'insert'
        db.insert('media', {
            'key': 'name, src_type, '
                   'create_time, last_update_time',
            'val': '"%s", %s, %s, %s' % (
                dicData['name'], 2, now, now)
        })
        media_id = db.cursor.lastrowid
        db.insert('media_wechat', {
            'key': 'media_id, wechat_id, biz',
            'val': '%s, "%s", "%s"' % (media_id, dicData['wechat_id'], '')
        })

if __name__ == '__main__':
    # for j in read_wechat_1():
    #     into_db_1(j)
    # for t in read_wechat_2():
    #     into_db_2(t)
    # for h in read_wechat_3():
    #     into_db_3(h)
    # for k in read_wechat_4():
    #     into_db_4(k)
    # for l in read_wechat_5():
    #     into_db_4(l)
    # for m in read_wechat_6():
    #     into_db_6(m)
    # for n in read_wechat_7():
    #     into_db_7(n)
    # for o in read_wechat_8():
    #     into_db_8(o)
    # for p in read_wechat_9():
    #     into_db_9(p)
    db.commit()
