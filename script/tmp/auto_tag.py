# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
sys.path.append("..")

from script.db_base import DB
from rule import rule

mode = 'online'
db = DB(mode)


def task():
    f = open('tmp/result')
    for line in f:
        item = line.strip().split('\t')
        db.update('media', {
            'fields': ['category_media_id = %s' % item[1]],
            'condition': 'id=%s' % item[0]
        })
    f.close()


def run():
    category = db.find('category_media', 'list', {})
    categories = {}
    # categories = {c['name']: c['id'] for c in category}
    for ct in category:
        ct_name = ct['name']
        ct_id = ct['id']
        # if '/' in ct_name:
        #     for s in ct_name.split('/'):
        #         categories[s] = ct_id
        # else:
        #     categories[ct_name] = ct_id
        categories[ct_name] = ct_id

    # tag = db.find('tag', 'list', {})
    # tags = {t['name']: t['id'] for t in tag}

    for category_key in rule:
        try:
            cid = categories[category_key]
        except KeyError:
            print category_key.encode('u8')
            continue
        keywords = rule[category_key]
        for keyword in keywords:
            db.update(
                'media',
                {
                    'fields': ['category_media_id={cid}'.format(cid=cid)],
                    'condition': 'category_media_id = 0 and (brief like "%{key}%" or name like "%{key}%")'.format(key=keyword.lower())
                }
            )

    # for cg in categories:
    #     db.update(
    #         'media',
    #         {
    #             'fields': ['category_media_id={cid}'.format(cid=categories[cg])],
    #             'condition': 'name like "%{key}%"'.format(key=cg)
    #         }
    #     )
    # for key in tags:
    #     res = db.find(
    #         'media',
    #         'list',
    #         {'fields': ['id', 'name'], 'condition': 'name like "%{key}%"'.format(key=key)}
    #     )
    #     for item in res:
    #         t = db.find(
    #             'media_tag',
    #             'first',
    #             {'condition': 'media_id={mid} and tag_id={tid}'.format(mid=item['id'], tid=tags[key])}
    #         )
    #         if not t:
    #             db.insert(
    #                 'media_tag',
    #                 {
    #                     'key': 'media_id, tag_id',
    #                     'val': '{mid}, {tid}'.format(mid=item['id'], tid=tags[key])
    #                 }
    #             )

if __name__ == '__main__':
    task()
    db.commit()
