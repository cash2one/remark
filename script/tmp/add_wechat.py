# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append("..")

import time
import xlrd
import MySQLdb
from api import crawler

SPLIT_STR = '/'
BOOL_DICT = {'√': 1, '×': 2}
DB_HOST = 'rdshf7hicnex6yhgi3h8.mysql.rds.aliyuncs.com'
# dev
DB_USER = 'yidao_dev'
DB_PASS = 'byXPqETUBRcBTPJb'
DB_PROF = 'yidao_profile_dev'

DB_USER = 'yidao'
DB_PASS = 'ZdKnbciJwveyN47w'
DB_PROF = 'yidao_profile'
db_obj = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_PROF, use_unicode=1, charset='utf8')


def format_data(data):
    one_val = []
    for item in data:
        if item is None:
            one_val.append('null')
        else:
            one_val.append('\'%s\'' % (str(item)))
    return one_val


def insertMany(tbl_name, data):
    print 'now, insert tbl:', tbl_name
    cursor = db_obj.cursor()
    value = ', '.join(['%s'] * len(data[0]))
    sql = 'INSERT INTO {tbl} VALUES ({val})'.format(tbl=tbl_name, val=value)
    print sql
    try:
        cursor.executemany(sql, data)
        db_obj.commit()
    except Exception, e:
        print e
        db_obj.rollback()
    cursor.close()

def db_job(media_data, media_wechat_data):
    media_one = format_data(media_data)
    media_wechat_one = format_data(media_wechat_data)
    name = media_one[1]
    wechat_id = media_wechat_one[1]
    print name, wechat_id
    try:
        res = find_media_wechat(wechat_id)
        media_id = int(res[1]) if res else ''
        if media_id:
            media_id = '\'%s\'' % (str(media_id))
            update_media_wechat([media_id] + media_wechat_one)
            update_media(media_id, media_one)
        else:
            media_id = insert_media(media_one)
            media_id = '\'%s\'' % (str(media_id))
            insert_media_wechat([media_id] + media_wechat_one)
        db_obj.commit()
    except Exception, e:
        print e
        db_obj.rollback()


def find_media(_id):
    cursor = db_obj.cursor()
    sql = 'select * from media where id=%s' % _id
    #print sql
    cursor.execute(sql)
    res = cursor.fetchone()
    cursor.close()
    return res


def find_media_wechat(_wechat_id):
    cursor = db_obj.cursor()
    sql = 'select * from media_wechat where wechat_id=%s' % _wechat_id
    #print sql
    cursor.execute(sql)
    res = cursor.fetchone()
    cursor.close()
    return res


def insert_media(one_val):
    cursor = db_obj.cursor()
    sql = 'INSERT INTO media (`user_id`, `name`, `brief`, `identify`, `avatar`, `platform_id`, `category_media_id`, `tags`, `value_level`, `status`, `audience_gender`, `audience_age`, `audience_career`, `audience_degree`, `audience_income`, `audience_province_id`, `audience_city_id`, `audience_county_id`, `first_price`, `second_price`, `role`, `can_original`, `comment`, `award`, `station`, `worth`, `kol`, `ad`, `ad_type`, `contact_person`, `contact_phone`, `contact_qq`, `contact_wechat`, `remark`, `src_type`, `media_platform_create_time`, `create_time`, `last_update_time`) VALUES ({val})'.format(
        val=", ".join(one_val))
    #print sql
    cursor.execute(sql)
    mid = cursor.lastrowid
    cursor.close()
    return mid


def update_media(media_id, one_val):
    cursor = db_obj.cursor()
    sql = 'UPDATE media SET `name`=%s,`brief`=%s,`avatar`=%s, `audience_gender`=%s,`audience_age`=%s,`audience_career`=%s,`audience_degree`=%s,`audience_income`=%s,`first_price`=%s,`second_price`=%s,`role`=%s,`can_original`=%s,`comment`=%s,`award`=%s,`station`=%s,`worth`=%s,`kol`=%s,`ad`=%s,`ad_type`=%s,`contact_person`=%s,`contact_phone`=%s,`contact_qq`=%s,`contact_wechat`=%s,`remark`=%s,`src_type`=%s,`last_update_time`=%s WHERE `id`=%s' % ( one_val[1],
        one_val[2], one_val[4], one_val[10], one_val[11], one_val[12], one_val[13], one_val[14], one_val[18],
        one_val[19], one_val[20], one_val[21], one_val[22], one_val[23], one_val[24], one_val[25], one_val[26],
        one_val[27], one_val[28], one_val[29], one_val[30], one_val[31], one_val[32], one_val[33], one_val[34],
        one_val[37], media_id
    )
    #print sql
    cursor.execute(sql)
    cursor.close()


def insert_media_wechat(one_val):
    cursor = db_obj.cursor()
    sql = 'INSERT INTO media_wechat(`media_id`, `openid`, `wechat_id`, `qrcode`, `biz`, `gh_id`, `original`, `url`, `nickname_id`, `top_avg_read_num`, `top_three_avg_read_num`, `like_num`) VALUES ({val})'.format(
        val=", ".join(one_val))
    #print sql
    cursor.execute(sql)
    cursor.close()


def update_media_wechat(one_val):
    cursor = db_obj.cursor()
    sql = 'UPDATE media_wechat SET `media_id`=%s, `qrcode`=%s,`biz`=%s,`gh_id`=%s,`url`=%s,`top_avg_read_num`=%s,`top_three_avg_read_num`=%s,`like_num`=%s WHERE `wechat_id`=%s' % (
        one_val[0], one_val[3], one_val[4], one_val[5], one_val[7], one_val[9], one_val[10], one_val[11], one_val[2])
    #print sql
    cursor.execute(sql)
    cursor.close()


def get_checked(p_str, _all=None, single=False):
    if not p_str:
        if single:
            return 0
        return
    p_lst = p_str.split(SPLIT_STR)
    if not _all:
        return ','.join([item for item in p_lst])
    if single:
        return _all.get(p_str, 0)
    return ','.join([str(_all[j]) for j in p_lst])


def get_gender(p_str):
    all_gender = {'不限': 0, '偏女性': 1, '偏男性': 2}
    return get_checked(p_str, all_gender, True)


def get_role(p_str):
    all_role = {'企业': 1, '个人': 2}
    return get_checked(p_str, all_role, True)


def get_ad_type(p_str):
    all_ad_type = {'软广': 1, '硬广': 2}
    return get_checked(p_str, all_ad_type, True)


def get_age(p_str):
    all_age = {u'70后': 1, u'80后': 2, u'85后': 3, u'90后': 4, u'95后': 5, u'其它': 6}
    return get_checked(p_str, all_age, False)


def get_degree(p_str):
    all_degree = {u'高中以下': 1, u'高中': 2, u'大专': 3, u'本科': 4, u'研究生': 5, u'研究生以上': 6}
    return get_checked(p_str, all_degree, False)


def get_career(p_str):
    all_career = {u'工薪阶层': 1, u'白领': 2, u'高管': 3, u'创业者': 4,
                  u'企事业单位': 5, u'国企': 6, u'公职人员': 7, u'自由职业者': 8}
    return get_checked(p_str, all_career, False)


def get_income(p_str):
    all_income = {u'5万元以下': 1, u'5万-10万': 2, u'10万-20万': 3, u'20万以上': 4}
    return get_checked(p_str, all_income, False)


def get_bool_value(p_str):
    return get_checked(str(p_str), BOOL_DICT, True)


excel = xlrd.open_workbook('wechat_data.xlsx')
sheet = excel.sheet_by_index(0)
rows = sheet.nrows
title = sheet.row_values(0)
# print rows
# print ','.join(title).encode('u8')
craw = crawler.crawler()

for i in range(1, rows):
    row_data = sheet.row_values(i)
    # print row_data
    name, wechat_id, top_three_avg_read_num, top_avg_read_num, like_num, contact_phone, contact_qq, contact_email, \
    contact_wechat, url, category, tag, role, comment, award, original, kol, gender, age, career, degree, income, \
    can_original, ad, ad_type, first_price, second_price, station, remark = row_data
    wechat_more = craw.official(url, '', False)
    # print wechat_more
    if len(wechat_more) <= 1:
        # TODO 图文链接抓取失败处理
        print 'in row: {row}, url: {url}'.format(row=i + 1, url=url)
        continue
    c_wechat_id = wechat_more.get('wechat_id')
    c_avatar = wechat_more.get('avatar')
    c_name = wechat_more.get('name')
    c_biz = wechat_more.get('biz')
    c_qrcode = wechat_more.get('qrcode')
    c_gh_id = wechat_more.get('user_name')
    c_brief = wechat_more.get('features')
    c_brief = c_brief.replace("'", "\'")
    n_gender = get_gender(gender)
    n_age = get_age(age)
    n_career = get_career(career)
    n_degree = get_degree(degree)
    n_income = get_income(income)
    n_role = get_role(role)
    n_can_original = get_bool_value(original)
    n_comment = get_bool_value(comment)
    n_award = get_bool_value(award)
    n_station = get_bool_value(station)
    n_worth = 0
    n_kol = get_bool_value(kol)
    n_ad = get_bool_value(ad)
    n_ad_type = get_ad_type(ad_type)
    n_phone = get_checked(str(contact_phone), None, False)
    n_qq = get_checked(str(contact_qq), None, False)
    n_wechat = get_checked(str(contact_wechat), None, False)
    first_price = 0 if not first_price else first_price
    second_price = 0 if not second_price else second_price
    top_three_avg_read_num = top_three_avg_read_num if top_three_avg_read_num else 0
    top_avg_read_num = top_avg_read_num if top_avg_read_num else 0
    like_num = like_num if like_num else 0
    if not c_wechat_id:
        c_wechat_id = c_gh_id
    if wechat_id != c_wechat_id:
        # TODO 抓取结果与excel不一致
        print 'in row: {row}, name: {name}, wechat_id:{wid} and craw name:{c_name}, wechat_id:{cwid}'.format(
            row=i + 1, name=name, wid=wechat_id, c_name=c_name, cwid=c_wechat_id
        )
    # TODO 认证信息抓取
    n_original = 0
    media_data = [0, c_name, c_brief, '', c_avatar, 2, None, None, -1, 0, n_gender, n_age, n_career, n_degree, n_income,
                  0, None, None, first_price, second_price, n_role, n_can_original, n_comment, n_award, n_station,
                  n_worth, n_kol, n_ad, n_ad_type, None, n_phone, n_qq, n_wechat, remark, 2, 0, 0, int(time.time())]
    media_wechat_data = [None, c_wechat_id, c_qrcode, c_biz, c_gh_id, n_original, url, '0', top_avg_read_num,
                         top_three_avg_read_num, like_num]
    # print media_data, len(media_data)
    # print media_wechat_data, len(media_wechat_data)
    db_job(media_data, media_wechat_data)
    # break
db_obj.close()
