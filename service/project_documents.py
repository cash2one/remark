# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    lis_status = ['已结束','准备中','进行中']

    def __init__(self, _model, param):
        base.baseService.__init__(self, _model, param)
        self.documents_model = self.importModel('project_documents')

    def get_documentsPage(self, intPage, intPageDataNum):

        tupData, intRows = self.documents_model.findPaginate({
            'page': [intPage, intPageDataNum],
            'order': 'update_time desc'
        })
        return tupData, intRows

    def get_documents_detail(self, media_id):
        tupData = self.documents_model.findOne({
            'condition':"media_content_id = {id}".format(id=media_id)
        })
        return tupData

    def create_documents(self, dicArgs):

        if not dicArgs['documents_title'] or dicArgs['documents_title']=="":
            return 500

        self.documents_model.insert({
            'key': 'content_info, update_time, create_time, media_title',
            'val': '\'{content}\', {ut}, {ct}, \'{title}\''.format(
                content=dicArgs['content'], ut=int(self.time.time()), ct=int(self.time.time()), title=dicArgs['documents_title'])
        })
        tupPlan = self.documents_model.findOne({
            'fields': ['id','media_title'],
            'order': 'id desc'
        })
        update_fields=[]
        update_fields.append('media_content_id={id}'.format(id = int(tupPlan['id'])))
        self.documents_model.update({
            'fields':update_fields,
            'condition':'id={id}'.format(id = int(tupPlan['id']))
        })

        if self.model.db.status != 200:
            return 500
        return 200

    def update_documents(self, dicArgs):
        if not dicArgs['documents_title'] or dicArgs['documents_title']=="":
            return 500

        self.documents_model.update({
            'fields': ['media_title = \'{title}\''.format(title=dicArgs['documents_title']),
                       'content_info = \'{content}\''.format(content=dicArgs['content']),
                       'update_time = {ut}'.format(ut=int(self.time.time()))],
            'condition': 'media_content_id = {id}'.format(id=dicArgs['media_content_id'])
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def check_group(self, id, uid):
        res = self.importModel('document_follow').findOne({
            'fields':['id'],
            'condition': 'user_id=%s and document_id=%s' % (uid, id)
        })
        return res

    def follow_group(self, id, group, uid, remark):
        if self.check_group(id, uid):
            self.importModel('document_follow').delete({
                'condition': 'user_id=%s and document_id=%s' % (uid, id)
            })
            if self.model.db.status != 200:
                return 500
        else:
            if not group:
                group = ['0']
            for item in group:
                self.importModel('document_follow').insert({
                    'key':'document_id, group_id, remark, user_id, createTime',
                    'val':'{id}, {group}, \'{remark}\', {uid}, {ct}'.format(
                    id=id, group=item, remark=remark, uid=uid, ct=int(self.time.time()))
                })
                if self.model.db.status != 200:
                    return 500
        return 200