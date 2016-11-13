# -*- coding:utf-8 -*-

import json
import time
import MySQLdb

DB_HOST = 'rdshf7hicnex6yhgi3h8.mysql.rds.aliyuncs.com'
# dest_test
DB_USER = 'yidao_test'
DB_PASS = 'Okg8dEZh1laNrpmY'
DB_BASE = 'yidao_test'

# # dest_online
# DB_USER = 'yidao'
# DB_PASS = ''
# DB_BASE = 'yidao'

# src
DB_USER_OL = 'yidao_dev'
DB_PASS_OL = 'byXPqETUBRcBTPJb'
DB_BASE_OL = 'yidao_dev'

db = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_BASE, use_unicode=1, charset='utf8')
db_ol = MySQLdb.connect(DB_HOST, DB_USER_OL, DB_PASS_OL, DB_BASE_OL, use_unicode=1, charset='utf8')
# 域名筛选
domain = ('.com', '.cn', '.net', '.org', '.cc', '.me', '.COM',
          '.biz', '.im', '.tv', '.in', '.tw', '.jp', '.asia', '.hk', '.info')
now = int(time.time())


def deleteAll(db_obj, tbl_name):
    print 'now clear tbl:', tbl_name
    cursor = db_obj.cursor()
    sql = 'DELETE FROM {tbl} WHERE 1'.format(tbl=tbl_name)
    try:
        cursor.execute(sql)
        db_obj.commit()
    except Exception, e:
        print e
        db_obj.rollback()
    cursor.close()


def deleteByTagId(db_obj, tbl_name):
    cursor = db_obj.cursor()
    sql = 'DELETE FROM {tbl} WHERE tag_id BETWEEN 27 and 60'.format(tbl=tbl_name)
    try:
        cursor.execute(sql)
        db_obj.commit()
    except Exception, e:
        print e
        db_obj.rollback()
    cursor.close()


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


def findDicCol(db_obj, tbl_name, col_str, start=1):
    dic_data = {}
    cursor = db_obj.cursor()
    sql = 'SELECT {col} FROM {tbl}'.format(col=col_str, tbl=tbl_name)
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        for i in data:
            if start == 1:
                key = str(i[0])
            else:
                key = str(i[:start])
            dic_data.setdefault(key, [])
            dic_data[key].append(i[start:])
    except Exception, e:
        print e
    cursor.close()
    return dic_data


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


def updateFeedbackOrderId(db_obj, data):
    cursor = db_obj.cursor()
    set_str = 'order_id = %s'
    cond_str = 'demand_id = %s and media_id = %s'
    sql = 'UPDATE demand_wechat_feedback SET {s} WHERE {c}'.format(s=set_str, c=cond_str)
    try:
        cursor.executemany(sql, data)
        db_obj.commit()
    except Exception, e:
        print e
        db_obj.rollback()
    cursor.close()


def change_user():
    pt_users = findMany(db_ol, 'pt_users')
    users = []
    accounts = []
    for idx, row in enumerate(pt_users, 1):
        user_id, account, password, salt, nickname, avatar, email, phone, qq, \
        city, city_id, vcode, ctime, utime, activate, status = row
        if city_id != '0' and city_id is not None:
            lisId = city_id.split(',')
            if len(lisId) == 1:
                pid = lisId[0]
                cid = '0'
                vid = '0'
            elif len(lisId) == 2:
                pid = lisId[0]
                cid = lisId[1]
                vid = '0'
            elif len(lisId) == 3:
                pid = lisId[0]
                cid = lisId[1]
                vid = lisId[2]
            else:
                pid, cid, vid = '0', '0', '0'
        else:
            pid, cid, vid = '0', '0', '0'
        # 邮箱帐号 或 微信openid帐号
        if '@' in account and account.endswith(domain) or 'o0oNOt' in account:
            # pass
            users.append([user_id, nickname, '', '0', avatar, pid, cid, vid, phone, account, qq, '0', ctime, now])
        else:
            # pass
            users.append([user_id, nickname, '', '0', avatar, pid, cid, vid, phone, account, qq, '0', ctime, now])
        if 'o0oNOt' not in account:
            accounts.append([idx, user_id, account, password, salt, '1', ctime])
            if '@' not in account or not account.endswith(domain):
                print '[!]may be wrong account:', account.encode('u8'), 'user id', user_id
    # 迁移数据
    deleteAll(db, 'account')
    deleteAll(db, 'user')
    insertMany(db, 'account', accounts)
    insertMany(db, 'user', users)


def change_media():
    pt_oas = findMany(db_ol, 'pt_official_accounts')
    medias = []
    media_wechats = []
    for idx, row in enumerate(pt_oas, 1):
        media_id, user_id, openid, name, user_name, identify, wechat_id, avatar, big_avatar, features, qrcode, biz, \
        sato, sat, vat, uat, score, crawl, status, check, data_info, data_time, asex, ap, type, level, avg_num = row
        medias.append([media_id, user_id, name, features, identify, avatar,
                       '2', None, '0', '0', '0', None, None, level, sat, '0', now])
        media_wechats.append([idx, media_id, openid, wechat_id, qrcode, biz, '', '0', '0', '0'])
    deleteAll(db, 'media')
    deleteAll(db, 'media_wechat')
    insertMany(db, 'media', medias)
    insertMany(db, 'media_wechat', media_wechats)


def change_demand():
    pt_demands = findMany(db_ol, 'pt_demands')
    pt_jiedan = findDicCol(db_ol, 'pt_demand_jiedan', 'demand_id, id')
    pt_pay = findDicCol(db_ol, 'pt_demand_pay', 'demand_id, id')
    pt_feedback = findDicCol(db_ol, 'pt_demand_feedback', 'demand_id, id')
    demands = []
    # 需求单状态转换
    switch = {'-2': '7', '-1': '5', '0': '1', '1': '2', '2': '3', '3': '3', '4': '3', '5': '4'}
    for idx, row in enumerate(pt_demands, 1):
        demand_id, user_id, title, desc, tbegin, tend, market, money, tel, \
        platform, form_id, invoice, ititle, view_count, ctime, status = row
        str_status = str(status)
        str_demand_id = str(demand_id)
        if str_status in ['-2', '-1', '3', '4', '5']:
            demands.append([demand_id, user_id, title, form_id, tbegin, tend, money,
                            '0', None, None, '2', market, '', view_count, switch[str_status], ctime])
        elif str_status in ['0', '1', '2']:
            if pt_jiedan.get(str_demand_id):
                if pt_pay.get(str_demand_id):
                    if pt_feedback.get(str_demand_id):
                        new_status = '3'
                    else:
                        new_status = '3'
                else:
                    if tend < now:
                        new_status = '6'
                    else:
                        new_status = '2'
            else:
                if tend < now:
                    new_status = '6'
                elif str_status == '0':
                    new_status = '1'
                else:
                    new_status = '2'
            demands.append([demand_id, user_id, title, form_id, tbegin, tend, money,
                            '0', None, None, '2', market, '', view_count, new_status, ctime])
    deleteAll(db, 'demand')
    insertMany(db, 'demand', demands)


def change_demand_form():
    pt_forms = findMany(db_ol, 'pt_demand_forms')
    forms = []
    for idx, row in enumerate(pt_forms, 1):
        form_id, title, sort = row
        forms.append([form_id, title, sort])
    deleteAll(db, 'demand_form')
    insertMany(db, 'demand_form', forms)


def change_demand_article():
    pt_demand_articals = findMany(db_ol, 'pt_demand_articals')
    articles = []
    for idx, row in enumerate(pt_demand_articals, 1):
        _id, demand_id, title, author, content, url = row
        articles.append([_id, demand_id, title, author, content, url])
    deleteAll(db, 'demand_article')
    insertMany(db, 'demand_article', articles)


def change_demand_take_order():
    pt_jiedan = findMany(db_ol, 'pt_demand_jiedan')
    jds = []
    switch = {'0': '1', '1': '4'}
    for idx, row in enumerate(pt_jiedan, 1):
        _id, demand_id, user_id, oa_id, p1, p2, p3, p4, phone, desc, t, ct, status = row
        jds.append([_id, demand_id, user_id, oa_id, phone, switch[str(status)], ct])
    deleteAll(db, 'demand_take_order')
    insertMany(db, 'demand_take_order', jds)


def change_demand_reason():
    reason = findMany(db_ol, 'pt_demand_reason')
    reasons = []
    for idx, row in enumerate(reason, 1):
        _id, demand_id, reason = row
        reasons.append([_id, demand_id, reason, '1444960366'])
    deleteAll(db, 'demand_check')
    insertMany(db, 'demand_check', reasons)


def change_media_case():
    case = findMany(db_ol, 'pt_official_accounts_anli')
    cases = []
    for idx, row in enumerate(case, 1):
        _id, oa_id, title, picture, url, price, pat, sat = row
        try:
            new_sat = str(int(time.mktime(time.strptime(str(sat), "%Y-%m-%d %H:%M:%S"))))
        except ValueError:
            new_sat = pat
        cases.append([_id, oa_id, title, picture, url, price, '', pat, new_sat])
    deleteAll(db, 'media_case')
    insertMany(db, 'media_case', cases)


def change_attr_value():
    deleteAll(db, 'ad_attribute')
    deleteAll(db, 'ad_value')
    deleteAll(db, 'ad_attribute_value')
    insertMany(db, 'ad_attribute', [['1', '类型']])
    insertMany(db, 'ad_value', [['1', '单图文'], ['2', '多图文头条'], ['3', '多图文二条'], ['4', '多图文其它']])
    insertMany(db, 'ad_attribute_value', [['1', '1', '1'], ['2', '1', '2'], ['3', '1', '3'], ['4', '1', '4']])


def change_tag():
    tag = findMany(db_ol, 'pt_categorys')
    tags = []
    for idx, row in enumerate(tag, 1):
        _id, name, sort, pid, status = row
        tags.append([_id, name, sort])
    deleteAll(db, 'tag')
    insertMany(db, 'tag', tags)


def change_media_tag():
    media_tag = findMany(db_ol, 'pt_official_accounts_categorys')
    media_tags = []
    for idx, row in enumerate(media_tag, 1):
        _id, oid, cid = row
        media_tags.append([_id, oid, cid])
    deleteAll(db, 'media_tag')
    insertMany(db, 'media_tag', media_tags)


def change_media_price():
    price = findMany(db_ol, 'pt_official_accounts_prices')
    prices = []
    idx = 1
    for row in price:
        _id, oid, p1, p2, p3, p4, ct = row
        if p1 != 0:
            prices.append([idx, oid, p1, '[{"attr_id":"1","value":"1"}]'])
            idx += 1
        if p2 != 0:
            prices.append([idx, oid, p2, '[{"attr_id":"1","value":"2"}]'])
            idx += 1
        if p3 != 0:
            prices.append([idx, oid, p3, '[{"attr_id":"1","value":"3"}]'])
            idx += 1
        if p4 != 0:
            prices.append([idx, oid, p4, '[{"attr_id":"1","value":"4"}]'])
            idx += 1
    deleteAll(db, 'media_price')
    insertMany(db, 'media_price', prices)


def change_area():
    area = findMany(db_ol, 'pt_citys')
    areas = []
    fp = {'1': 'b', '2': 't', '3': 'h', '4': 's', '5': 'n', '6': 'l', '7': 'j', '8': 'h', '9': 's',
          '10': 'j', '11': 'z', '12': 'a', '13': 'f', '14': 'j', '15': 's', '16': 'h', '17': 'h', '18': 'h',
          '19': 'g', '20': 'g', '21': 'h', '22': 'c', '23': 's', '24': 'g', '25': 'y', '26': 'x', '27': 's',
          '28': 'g', '29': 'q', '30': 'l', '31': 'x', '32': 't', '33': 'x', '34': 'a', '35': 'h', '36': 'q'}
    for idx, row in enumerate(area, 1):
        _id, name, level, ut, parent, sort = row
        areas.append([_id, name, fp.get(str(_id), ''), level, ut, parent, sort])
    deleteAll(db, 'area')
    insertMany(db, 'area', areas)


def change_feedback():
    feedback = findMany(db_ol, 'pt_demand_feedback')
    # 新表
    demand = findDicCol(db, 'demand', 'id, status')
    feedbacks = []
    order_id = 0
    media_user = findDicCol(db_ol, 'pt_official_accounts', 'id, user_id')
    for idx, row in enumerate(feedback, 1):
        _id, demand_id, jiedan_id, oa_id, title, date, _type, ctype, url, pic, rc, status, t = row
        user_id = media_user[str(oa_id)][0][0]
        try:
            # 新表状态
            demand_status = str(demand[str(demand_id)][0][0])
            if demand_status == '4':
                feedback_status = '0'
            elif demand_status == '3':
                feedback_status = '1'
            else:
                feedback_status = '-1'
        except KeyError:
            print '[!]can not find demand id:', demand_id
            feedback_status = '-1'
        feedbacks.append([_id, user_id, order_id, demand_id, oa_id,
                          url, title, '0', pic, '', '', feedback_status, t])
    deleteAll(db, 'demand_wechat_feedback')
    insertMany(db, 'demand_wechat_feedback', feedbacks)


def change_category_media():
    deleteAll(db, 'category_media')
    insertMany(db, 'category_media', [
        ['1', '互联网', '1'], ['2', '情感', '2'], ['3', '游戏/软件', '3'], ['4', '教育/培训', '4'],
        ['5', '金融/保险', '5'], ['6', '旅游', '6'], ['7', '美容', '7'], ['8', '科技/3C', '8'],
        ['9', '食品/餐饮', '9'], ['10', '服饰', '10'], ['11', '生活', '11'], ['12', '运动/健身', '12'],
        ['13', '商务', '13'], ['14', '母婴/儿童', '14'], ['15', '文化/艺术', '15'], ['16', '法律', '16'],
        ['17', '房地产/建筑', '17'], ['18', '汽车/交通', '18'], ['19', '家居', '19'], ['20', '政务', '20'],
        ['21', '娱乐/明星', '21'], ['22', '医疗/健康', '22'], ['23', '酒店/住宿', '23'], ['24', '社会/民生', '24'],
        ['25', '媒体/杂志', '25'], ['26', '其它', '26']
    ])


def change_demand_media_tag():
    demand_tag = findMany(db_ol, 'pt_demand_categorys')
    demand_tags = []
    for idx, row in enumerate(demand_tag, 1):
        _id, demand_id, cid = row
        demand_tags.append([_id, demand_id, cid])
    deleteAll(db, 'demand_media_tag')
    insertMany(db, 'demand_media_tag', demand_tags)


def change_demand_order():
    pay = findMany(db_ol, 'pt_demand_pay')
    ad_user = findDicCol(db_ol, 'pt_demands', 'demand_id, user_id')
    take_order_time = findDicCol(db, 'demand_take_order', 'demand_id, create_time')
    take_order = findDicCol(db, 'demand_take_order', 'id, user_id, media_id')
    media_price = findDicCol(db, 'media_price', 'media_id, attr_value_info, id', start=2)
    feedback = findDicCol(db, 'demand_wechat_feedback', 'demand_id, media_id, status', start=2)
    orders = []
    idx = 1
    for row in pay:
        # money总价
        _id, user_id, demand_id, tp, money, detail, t, ct, trade_code, status = row
        detail = json.loads(detail)
        try:
            ad_user_id = ad_user[str(demand_id)][0][0]
        except KeyError:
            print '[!]can not find demand id:', demand_id
            continue
        if not detail:
            continue
        try:
            new_ct = str(int(time.mktime(time.strptime(str(ct), "%Y-%m-%d %H:%M:%S"))))
        except ValueError:
            try:
                ts = take_order_time[str(demand_id)]
                new_ct = max([t[0] for t in ts]) + 24 * 60 * 60
            except KeyError:
                print '[!]can not find demand id in take order:', demand_id
                new_ct = 0
        flag = (money - sum([float(i['price'].replace(',', '')) for i in detail]))
        length = len(detail)
        for m in detail:
            jid = str(m['jid'])
            kl = str(m['ptype'])
            price = m['price'].replace(',', '')
            try:
                m_user_id = str(take_order[jid][0][0])
                media_id = str(take_order[jid][0][1])
            except KeyError:
                print '[!]can not find take order id:', jid
                continue
            try:
                if kl == 'price_1x':
                    mpid = media_price['({mid}L'.format(mid=media_id) + ', u\'[{"attr_id":"1","value":"1"}]\')'][0][0]
                elif kl == 'price_x1':
                    mpid = media_price['({mid}L'.format(mid=media_id) + ', u\'[{"attr_id":"1","value":"2"}]\')'][0][0]
                elif kl == 'price_x2':
                    mpid = media_price['({mid}L'.format(mid=media_id) + ', u\'[{"attr_id":"1","value":"3"}]\')'][0][0]
                else:
                    mpid = media_price['({mid}L'.format(mid=media_id) + ', u\'[{"attr_id":"1","value":"4"}]\')'][0][0]
            except KeyError:
                print '[!]can not find price id by media_id:', media_id, 'and attr:', kl
                continue
            if flag == 0:
                new_price = price
            elif flag < 0 and length == 1:
                new_price = money
            else:
                print '[!]my be wrong money:', money, 'detail:', detail
                new_price = price
            fb = feedback.get('({did}L, {mid}L)'.format(did=demand_id, mid=media_id))
            if not fb:
                new_status = '2'
            elif str(fb[0][0]) == '0':
                new_status = '4'
            else:
                new_status = '3'
            orders.append([idx, ad_user_id, demand_id, m_user_id, media_id, mpid, new_price, new_status, new_ct])
            idx += 1
    deleteAll(db, 'demand_order')
    insertMany(db, 'demand_order', orders)


def change_order_pay():
    pay = findMany(db_ol, 'pt_demand_pay')
    take_order_time = findDicCol(db, 'demand_take_order', 'demand_id, create_time')
    pays = []
    for idx, row in enumerate(pay, 1):
        # money总价
        _id, user_id, demand_id, tp, money, detail, t, ct, trade_code, status = row
        try:
            new_ct = str(int(time.mktime(time.strptime(str(ct), "%Y-%m-%d %H:%M:%S"))))
        except ValueError:
            try:
                ts = take_order_time[str(demand_id)]
                new_ct = max([t[0] for t in ts]) + 24 * 60 * 60
            except KeyError:
                print '[!]can not find demand_id in take order:', demand_id
                new_ct = 0
        pays.append([_id, user_id, None, demand_id, 1, money, trade_code, 0, new_ct])
    deleteAll(db, 'order_pay')
    insertMany(db, 'order_pay', pays)


def change_friendlink():
    link = findMany(db_ol, 'pt_friendlinks')
    links = []
    for idx, row in enumerate(link, 1):
        _id, title, logo, lk, desc, sort, status, ct = row
        links.append([_id, title, logo, lk, desc, sort, status, ct])
    deleteAll(db, 'friendlink')
    insertMany(db, 'friendlink', links)


def change_platform():
    deleteAll(db, 'platform')
    insertMany(db, 'platform', [['1', '个人', '1'], ['2', '微信公众号', '2'], ['3', 'blibli', '3']])


def update_feedback_order_id():
    order = findDicCol(db, 'demand_order', 'demand_id, media_id, id', start=2)
    feedback = findMany(db, 'demand_wechat_feedback')
    data = []
    for row in feedback:
        _id, user_id, order_id, demand_id, media_id, url, title, pt, p1, p2, p3, status, ct= row
        try:
            order_id = order['({did}L, {mid}L)'.format(did=demand_id, mid=media_id)][0][0]
            data.append([order_id, demand_id, media_id])
        except KeyError:
            print '[!]can not find order id in order by demand_id:', demand_id, 'media_id:', media_id
    updateFeedbackOrderId(db, data)


def delete_tag():
    deleteByTagId(db, 'demand_media_tag')
    deleteByTagId(db, 'media_tag')


def insert_demand_extra():
    link = findMany(db, 'demand_article')
    links = []
    for row in link:
        _id, demand_id, title, author, body, lk = row
        if lk.startswith('http://mp.weixin.qq.com/'):
            status = 1
        else:
            status = 0
            lk = ''
        links.append([_id, demand_id, 0, 0, 0, 0, 0, status, lk, '', '', now])
    deleteAll(db, 'demand_extra')
    insertMany(db, 'demand_extra', links)

def insert_user_wechat():
    wechat = findMany(db_ol, 'pt_users_weixin')
    wechats = []
    for row in wechat:
        _id, uid, pro, openid, url, lang, city, country, sex, unionid, pri, nickname, status, ct = row
        try:
            new_sat = str(int(time.mktime(time.strptime(str(ct), "%Y-%m-%d %H:%M:%S"))))
        except ValueError:
            new_sat = now
        if not sex:
            sex = '0'
        wechats.append([_id, uid, openid, nickname, sex, pro, city, country, url, pri, unionid, status, new_sat])
    deleteAll(db, 'user_wechat')
    insertMany(db, 'user_wechat', wechats)

def run_all():
    # 用户及帐号
    change_user()

    # 自媒体
    change_media()

    # 需求单
    change_demand()

    # 需求单形式
    change_demand_form()

    # 需求图文
    change_demand_article()

    # 接单信息
    change_demand_take_order()

    # 审核未通过原因
    change_demand_reason()

    # 自媒体案例
    change_media_case()

    # 刊例
    change_attr_value()

    # 标签
    change_tag()

    # 自媒体标签
    change_media_tag()

    # 自媒体刊例报价
    change_media_price()

    # 区域
    change_area()

    # 反馈
    change_feedback()

    # 自媒体行业
    change_category_media()

    # 需求单标签
    change_demand_media_tag()

    # 订单
    change_demand_order()

    # 支付
    change_order_pay()

    # 友链
    change_friendlink()

    # 平台
    change_platform()

    # 更新order_id
    update_feedback_order_id()

    # 删除无效的tag_id引用
    delete_tag()

    # 更新额外信息
    insert_demand_extra()

    # 用户微信信息
    insert_user_wechat()


run_all()


db.close()
db_ol.close()
