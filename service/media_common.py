# -*- coding:utf-8 -*-

import base
import locale

class service(base.baseService):
    def __init__(self, _model, param):
        base.baseService.__init__(self, _model, param)
        self.mediaModel = self.importModel('project_media')
        self.mediaCartModel = self.importModel('project_media_cart')
        self.contactModel = self.importModel('project_contact')
        self.contactRelationModel = self.importModel('project_contact_relation')

    def get_media_cart(self, uid):
        tupData = self.mediaCartModel.findManyAs(
            self.dicConfig['DB_PROJECT'] + '.media_cart as mc',
            {
                'fields': ['mc.*', 'm.name', 'p.name as platform_name', 'p.label as platform_label'],
                'join': self.dicConfig['DB_PROJECT'] + '.media as m on (m.id = mc.media_id) LEFT JOIN ' +
                        self.dicConfig['DB_PROJECT'] + '.platform as p on (p.id = m.platform_id)',
                'condition': 'mc.user_id=%s' % uid,
            }
        )
        return tupData

    def add_media_cart(self, uid, mid):
        res = self.mediaCartModel.findOne({'condition': 'user_id=%s and media_id=%s' % (uid, mid)})
        if res:
            return 601
        self.mediaCartModel.insert({
            'key': 'user_id, media_id',
            'val': '%s, %s' % (uid, mid)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def del_media_cart(self, uid, mid):
        self.mediaCartModel.delete({
            'condition': 'user_id=%s and media_id=%s' % (uid, mid)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def clear_media_cart(self, uid):
        self.mediaCartModel.delete({
            'condition': 'user_id=%s' % uid
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_category_media(self):
        rtn = self.importModel('project_category_media').findMany({})
        locale.setlocale(locale.LC_COLLATE, 'zh_CN.UTF8')
        rtn = sorted(rtn, key=lambda i:i['name'], cmp=locale.strcoll)
        return rtn

    def get_tag(self):
        rtn = self.importModel('project_tag').findMany({})
        locale.setlocale(locale.LC_COLLATE, 'zh_CN.UTF8')
        rtn = sorted(rtn, key=lambda i:i['name'], cmp=locale.strcoll)
        return rtn

    def get_area(self, pid=None):
        if pid:
            rtn = self.importModel('area').findMany({
                'condition': 'parent = {pid}'.format(pid=pid)
            })
        else:
            rtn = self.importModel('area').findMany({})
        return rtn

    def get_contact_page(self, dic_arg):
        lisCondition = ['cr.relation_type=%s' % dic_arg['relation_type']]
        if dic_arg['query']:
            dicField = {'1': 'contact_person', '2': 'contact_phone', '3': 'contact_tel', '4': 'contact_wechat',
                        '5': 'contact_qq', '6': 'contact_email', '7': 'contact_other'}
            strField = dic_arg['field']
            strQuery = dic_arg['query']
            strCol = dicField[strField]
            searchCondition = 'c.{col} like \'%{key}%\''.format(col=strCol, key=strQuery)
            lisCondition.append(searchCondition)
        tupData, count = self.contactRelationModel.findPaginateAs(
            self.dicConfig['DB_PROJECT'] + '.contact as c',
            {
                'fields': ['DISTINCT c.*, cr.relation_type'],
                'condition': ' and '.join(lisCondition),
                'join': self.dicConfig['DB_PROJECT'] + '.contact_relation as cr on (cr.contact_id = c.id)',
                'page': [dic_arg['page'], 10],
                'order': 'c.last_update_time desc'
            },
            cacheRow=True
        )
        return tupData, count

    def get_contact(self, mid, relation_type):
        tupData = self.contactRelationModel.findManyAs(
            self.dicConfig['DB_PROJECT'] + '.contact as c',
            {
                'fields': ['c.*'],
                'join': self.dicConfig['DB_PROJECT'] + '.contact_relation as cr on (c.id = cr.contact_id)',
                'condition': 'cr.relation_id=%s and cr.relation_type=%s' % (mid, relation_type)
            }
        )
        return tupData

    def add_contact(self, dicArg):
        conditions = []
        phone = dicArg.get('contact_phone')
        wechat = dicArg.get('contact_wechat')
        qq = dicArg.get('contact_qq')
        if not (phone or wechat or qq):
            return 401
        if phone:
            conditions.append('contact_phone="%s"' % phone)
        if wechat:
            conditions.append('contact_wechat="%s"' % wechat)
        if qq:
            conditions.append('contact_qq="%s"' % qq)
        res = self.contactModel.findOne({'condition': ' or '.join(conditions)})
        if res:
            cid = res.get('id')
            status = 603
        else:
            cid = self.contactModel.insert({
                'key': 'contact_person, contact_position, contact_phone, contact_qq, contact_wechat, '
                       'contact_email, contact_tel, contact_other, last_update_time',
                'val': '"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s"' % (
                    dicArg.get('contact_person', ''), dicArg.get('contact_position', ''),
                    phone, qq, wechat, dicArg.get('contact_email', ''),
                    dicArg.get('contact_tel', ''), dicArg.get('contact_other', ''), int(self.time.time())
                )

            })
            status = 200
        ret = self.contactRelationModel.findOne({
            'condition': 'contact_id=%s and relation_id=%s and relation_type=%s' % (
                cid, dicArg.get('relation_id'), dicArg.get('relation_type'))
        })
        if not ret:
            self.contactRelationModel.insert({
                'key': 'contact_id, relation_id, relation_type',
                'val': '%s, %s, %s' % (cid, dicArg.get('relation_id'), dicArg.get('relation_type'))
            })
        if self.model.db.status != 200:
            return 500
        return status

    def get_contact_detail(self, cid):
        ret = self.contactModel.findOne({
            'condition': 'id=%s' % cid
        })
        return ret

    def update_contact(self, dicArg):
        fields = ['last_update_time=%s' % int(self.time.time())]
        for k in dicArg:
            if k == 'id':
                continue
            if dicArg[k] is None:
                fields.append('%s=%s' % (k, 'null'))
            else:
                fields.append('%s="%s"' % (k, dicArg[k]))
        self.contactModel.update({
            'fields': fields,
            'condition': 'id=%s' % dicArg['id']
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def del_contact(self, dicArg):
        cid = dicArg['contact_id']
        # 单个关联引用
        if dicArg['relation_id']:
            condition = 'contact_id=%s and relation_id=%s and relation_type=%s' % (
                cid, dicArg['relation_id'], dicArg['relation_type'])
        # 所有关联引用
        else:
            condition = 'contact_id=%s' % cid
        self.contactRelationModel.delete({
            'condition': condition
        })
        res = self.contactRelationModel.findOne({
            'condition': 'contact_id=%s' % cid
        })
        # 无任何关联引用时删除联系人
        if not res:
            self.contactModel.delete({
                'condition': 'id=%s' % cid
            })
        if self.model.db.status != 200:
            return 500
        return 200
