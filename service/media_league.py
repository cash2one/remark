# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, _model, param):
        base.baseService.__init__(self, _model, param)
        self.mediaModel = self.importModel('project_media')
        self.leagueModel = self.importModel('project_league')
        self.mediaLeagueModel = self.importModel('project_media_league')

    def get_league(self, intPage, intPageDataNum, strSearch):
        '''
        :func: 获取简要信息
        :param intPage: 页码
        :param intPageDataNum: 单页数据条数
        :param strSearch: 搜索的内容
        '''
        # 当前页起始序号
        intDataNumStart = (intPage - 1) * intPageDataNum
        # 搜索条件
        searchCondition = ''
        if strSearch:
            searchCondition = 'name like "%{search}%" or description like "%{search}%"'.format(search=strSearch)
        # 简要信息
        tupData, intRows = self.leagueModel.findPaginate({
            'condition': '{search}'.format(search=searchCondition),
            'page': [intPage, intPageDataNum],
            'order': 'last_update_time desc'
        })
        # 数据格式化
        for i in tupData:
            i['last_update_time'] = self.formatTime(i['last_update_time'], '%Y-%m-%d')
        return tupData, intRows

    def get_league_detail(self, _id):
        dicMedia = self.leagueModel.findOne({
            'condition': 'id={id}'.format(id=_id)
        })
        dicMedia['last_update_time'] = self.formatTime(dicMedia['last_update_time'], '%Y-%m-%d')
        return dicMedia

    def create_league(self, dicData):
        now = int(self.time.time())
        self.leagueModel.insert({
            'key': 'name, description, last_update_time',
            'val': '"%s", "%s", %s' % (dicData['name'], dicData['description'], now)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_league(self, dicArg):
        fields = []
        for k in dicArg:
            if k == 'id':
                continue
            if dicArg[k] is None:
                fields.append('{k}={v}'.format(k=k, v='null'))
            else:
                fields.append('{k}=\'{v}\''.format(k=k, v=dicArg[k]))
        fields.append('last_update_time={ut}'.format(ut=int(self.time.time())))
        self.leagueModel.update({
            'fields': fields,
            'condition': 'id={id}'.format(id=dicArg['id'])
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_league_media(self, _id):
        tupData = self.mediaLeagueModel.findManyAs(
            self.dicConfig['DB_PROJECT'] + '.media_league as ml',
            {
                'join': self.dicConfig['DB_PROJECT'] + '.media as m on (m.id = ml.media_id)',
                'condition': 'ml.league_id={id}'.format(id=_id),
                'order': 'm.last_update_time desc'
            }
        )
        cids, mids, tids = [], [], []
        for i in tupData:
            cids.append(i['category_media_id'])
            mids.append(i['media_id'])
            tags = i.get('tags')
            if tags:
                tids += tags.split(',')
            i['last_update_time'] = self.formatTime(i['last_update_time'], '%Y-%m-%d')
            i['platform'] = self.platform(i['platform_id'])
        category = self.get_league_category(cids) if cids else []
        tag = self.get_league_tag(mids, tids) if mids else []

        return {'media': tupData, 'category': category, 'tag': tag}

    def platform(self, platform_id):
        all = {2: '微信公众号', 3: 'bilibili', 4: '报纸', 5: '朋友圈', 6: '知乎', 7: '微博', 8: '社群'}
        return all.get(platform_id, '')

    def add_media(self, league_id, media_id):
        res = self.mediaLeagueModel.findOne({
            'condition': "league_id={lid} and media_id={mid}".format(lid=league_id, mid=media_id)
        })
        if res:
            return 601
        self.mediaLeagueModel.insert({
            'key': "league_id, media_id",
            'val': "{lid}, {mid}".format(lid=league_id, mid=media_id)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def remove_media(self, league_id, media_id):
        self.mediaLeagueModel.delete({
            'condition': "league_id={lid} and media_id={mid}".format(lid=league_id, mid=media_id)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_league_category(self, cids):
        tupData = self.importModel('project_category_media').findMany({})
        dicCategory = {i['id']: i['name'] for i in tupData}
        res = [dicCategory.get(j) for j in cids if j]

        from collections import Counter
        return Counter(res).most_common(1)

    def get_league_tag(self, mids, tids=None):
        tupData = self.importModel('project_media_tag').findManyAs(
            self.dicConfig['DB_PROJECT'] + '.media_tag as mt',
            {
                'fields': ['t.name'],
                'join': self.dicConfig['DB_PROJECT'] + '.tag as t on (t.id = mt.tag_id)',
                'condition': 'mt.media_id in ({id})'.format(id=','.join([str(i) for i in mids if i])),
            }
        )
        res = [d['name'] for d in tupData]
        if tids:
            # 遗留数据
            tupDataOld = self.importModel('project_tag').findMany({})
            dicTag = {i['id']: i['name'] for i in tupDataOld}
            res_old = [dicTag.get(int(j)) for j in tids if j]
            res += res_old

        from collections import Counter
        return Counter(res).most_common(6)
