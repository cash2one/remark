# -*- coding:utf-8 -*-


import sys
sys.path.append('../..')

import time
from script.db_base import  DB
import gflags
reload(sys)
sys.setdefaultencoding('utf-8')

# mode = 'dev'
mode = 'online'
dase = 'DB_PROJECT'
Flags = gflags.FLAGS

def set_advertiser_contact():
    db = DB(mode, dase)
    data = db.find('advertiser', 'list', {
        'fields':['id, contact_person, contact_position, contact_phone, contact_tel, contact_wechat, contact_qq, contact_email, contact_other, last_update_time'],
        'condition': 'contact_phone!="NULL" or contact_wechat!="NULL" or contact_qq!=0 or contact_tel!="NULL" or contact_email!="NULL" ',
        'group':'contact_phone, contact_wechat, contact_qq, contact_tel, contact_email'
    })

    contact_data = {'key':'contact_person, contact_position, contact_phone, contact_tel, contact_wechat, contact_qq, contact_email, contact_other, last_update_time'}
    for item in data:
        contact_value = '\'{cmp}\', \'{cp}\', \'{cph}\', \'{ctl}\', \'{cwh}\', \'{cqq}\', \'{cem}\', \'{coth}\', {last}'.format(
            cmp=(item['contact_person'] or '').encode('utf-8'), cp=(item['contact_position'] or '').encode('utf-8'), cph=(item['contact_phone'] or '').encode('utf-8'),
            ctl=(item['contact_tel'] or '').encode('utf-8'), cwh=(item['contact_wechat']or '').encode('utf-8'),
            cqq=item['contact_qq'], cem=(item['contact_email'] or '').encode('utf-8'),coth=(item['contact_other'] or '').encode('utf-8'), last=item['last_update_time'])
        contact_data['val'] = contact_value
        db.insert('contact', contact_data)

    db.commit()
    return data

def set_advertiser_relation():
    db = DB(mode, dase)
    data = db.find('advertiser', 'list', {
        'fields':['id'],
    })

    contact_data = {'key':'contact_id, relation_id, relation_type'}
    for item in data:
        contact_value = '{cid}, {rid}, {rty}'.format(
            cid=0, rid=item['id'], rty=2)
        contact_data['val'] = contact_value
        db.insert('contact_relation', contact_data)
    db.commit()
    return True

def add_advertiser_contact(mode):
    adverData = set_advertiser_contact()
    if adverData:
        set_advertiser_relation()
        db = DB(mode, dase)
        for item in adverData:
            searchCondition = 'id!=0 '
            if item['contact_phone'] and item['contact_phone']!='':
                searchCondition += " and contact_phone=\'{cpos}\'".format(cpos=item['contact_phone'])
            if item['contact_wechat'] and item['contact_wechat']!='':
                searchCondition += " and contact_wechat=\'{cpos}\'".format(cpos=item['contact_wechat'])
            if item['contact_qq'] and item['contact_qq']!=0:
                searchCondition += " and contact_qq=\'{cpos}\'".format(cpos=item['contact_qq'])
            if item['contact_tel'] and item['contact_tel']!='':
                searchCondition += " and contact_tel=\'{cpos}\'".format(cpos=item['contact_tel'])
            if item['contact_email'] and item['contact_email']!='':
                searchCondition += " and contact_email=\'{cpos}\'".format(cpos=item['contact_email'])
            # print "advertiser_id = ", searchCondition
            advertiser_id = db.find('advertiser', 'list', {
                            'fields':['id'],
                            'condition':'{condition}'.format(condition = searchCondition)
                            })

            contact_id = db.find('contact', 'list', {
                            'fields':['id'],
                            'condition':'contact_phone=\'{cpos}\' and  contact_wechat = \'{cwh}\' and ' \
                                     'contact_qq =\'{cqq}\' and contact_tel=\'{ctel}\' and  ' \
                                    'contact_email=\'{cem}\''.format(cpos=(item['contact_phone'] or '').encode('utf-8'), cwh=(item['contact_wechat'] or '').encode('utf-8'),
                                                                     cqq=(item['contact_qq'] or '').encode('utf-8'),
                                                                    ctel=(item['contact_tel'] or '').encode('utf-8'), cem=(item['contact_email'] or '').encode('utf-8'))
                            })
            if advertiser_id and contact_id:
                dataId = [str(item['id']) for item in advertiser_id]
                # print "dataId = ",contact_id, dataId
                db.update('contact_relation',{'fields':['contact_id={cid}'.format(cid=contact_id[0]['id'])],
                                             'condition': 'relation_id in ({id})'.format(id=','.join(dataId)) })
        db.commit()
    return True

if __name__ == "__main__":
    if len(sys.argv)!=1:
        print "Missing Parameters", sys.argv
        sys.exit()
    # python advertiser_contact.py
    add_advertiser_contact(mode)