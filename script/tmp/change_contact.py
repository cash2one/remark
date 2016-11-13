# -*- coding: utf-8 -*-


import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
sys.path.append("..")
import time
from script.db_base import DB
mode = 'online'
db = DB(mode)


def run():
    contacts = db.find('media', 'list', {
        'fields': ['id', 'contact_person', 'contact_phone', 'contact_qq', 'contact_wechat', 'contact_email'],
    })

    contacts = {i.pop('id'): i for i in contacts}

    person = {}
    tel = {}
    phone = {}
    qq = {}
    wechat = {}
    email = {}

    for cid in contacts:
        i = contacts[cid]
        cps, cp, cq, cw, ce = i['contact_person'], i['contact_phone'], i['contact_qq'], i['contact_wechat'], i['contact_email']
        # 联系方式为空
        if not (cp or cq or cw or ce):
            i['contact_tel'] = None
            continue
        if cps:
            person.setdefault(cps, [])
            person[cps].append(cid)
        if cp:
            # 电话
            if not cp.startswith('1'):
                tel.setdefault(cp, [])
                tel[cp].append(cid)
                i['contact_tel'] = cp
                i['contact_phone'] = None
            # 手机
            else:
                phone.setdefault(cp, [])
                phone[cp].append(cid)
                i['contact_tel'] = None
        else:
            i['contact_tel'] = None
        if cq:
            qq.setdefault(cq, [])
            qq[cq].append(cid)
        if cw:
            wechat.setdefault(cw, [])
            wechat[cw].append(cid)
        if ce:
            email.setdefault(ce, [])
            email[ce].append(cid)

    print len(person), len(tel), len(phone), len(qq), len(wechat), len(email)

    full_contacts = []
    for idx, cid in enumerate(contacts, 1):
        i = contacts[cid]
        cps, ct, cp, cq, cw, ce = i['contact_person'], i['contact_tel'], i['contact_phone'], i['contact_qq'], i['contact_wechat'], i['contact_email']
        if not (ct or cp or cq or cw or ce):
            continue
        # if idx % 10 == 0:
        #     break
        contact = {}
        contact['id'] = cid

        contact.setdefault('contact_person', set())
        for c0 in person.get(cps, []):
            if not contacts[c0]['contact_person']:
                continue
            contact['contact_person'].add(contacts[c0]['contact_person'])

        contact.setdefault('contact_tel', set())
        for c1 in tel.get(ct, []):
            if not contacts[c1]['contact_tel']:
                continue
            contact['contact_tel'].add(contacts[c1]['contact_tel'])

        contact.setdefault('contact_phone', set())
        for c2 in phone.get(cp, []):
            if not contacts[c2]['contact_phone']:
                continue
            contact['contact_phone'].add(contacts[c2]['contact_phone'])

        contact.setdefault('contact_qq', set())
        for c3 in qq.get(cq, []):
            if not contacts[c3]['contact_qq']:
                continue
            contact['contact_qq'].add(contacts[c3]['contact_qq'])

        contact.setdefault('contact_wechat', set())
        for c4 in wechat.get(cw, []):
            if not contacts[c4]['contact_wechat']:
                continue
            contact['contact_wechat'].add(contacts[c4]['contact_wechat'])

        contact.setdefault('contact_email', set())
        for c5 in email.get(ce, []):
            if not contacts[c5]['contact_email']:
                continue
            contact['contact_email'].add(contacts[c5]['contact_email'])
        full_contacts.append(contact)

    fmt_contacts = {}
    for s in full_contacts:
        key = (('contact_person', ', '.join(s['contact_person'])),
             ('contact_phone', ', '.join(s['contact_phone'])),
             ('contact_tel', ', '.join(s['contact_tel'])),
             ('contact_qq', ', '.join(s['contact_qq'])),
             ('contact_wechat', ', '.join(s['contact_wechat'])),
             ('contact_email', ', '.join(s['contact_email'])))
        fmt_contacts.setdefault(key, [])
        fmt_contacts[key].append(s['id'])

    for k in fmt_contacts:
        info = dict(k)
        ids = fmt_contacts[k]
        db.insert('contact', {
            'key': 'contact_person, contact_phone, contact_qq, contact_wechat, contact_email, contact_tel, last_update_time',
            'val': '"%s", "%s", "%s", "%s", "%s", "%s", "%s"' % (
                info['contact_person'], info['contact_phone'], info['contact_qq'],
                info['contact_wechat'], info['contact_email'], info['contact_tel'], int(time.time())
            )
        })
        cid = db.cursor.lastrowid
        for nid in ids:
            db.insert('contact_relation', {
                'key': 'contact_id, relation_id, relation_type',
                'val': '%s, %s, %s' % (cid, nid, 1)
            })
    db.commit()

if __name__ == '__main__':
    run()