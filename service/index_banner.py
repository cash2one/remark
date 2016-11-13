# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        # banner
        self.bannerModel = self.importModel('index_banner')

    def query(self, intPage=1, intPageDataNum=10):
        """
        :func: banner数据
        :param intPage: 页码
        :param intPageDataNum: 单页数据量
        """
        tupData, intRows = self.bannerModel.findPaginate({
            'fields': ['id', 'title', 'bg_color', 'image', 'sort', 'link', 'last_update_time'],
            'page': [intPage, intPageDataNum],
            'order': 'sort asc'
        })
        
        # 数据整合及格式化
        for k, item in enumerate(tupData):
            item['last_update_time'] = self.formatTime(item.get('last_update_time'), '%Y-%m-%d')
        return tupData

    def create(self, dicArgs):
        """
        :func: 新增banner
        :param dicArgs: banner参数
        """
        if 'banner_title' in dicArgs and 'logo_image' in dicArgs and \
                'banner_bg_color' in dicArgs and 'banner_url' in dicArgs:
            strTitle = dicArgs['banner_title'][0]
            strImage = '%s%s%s' % (self.dicConfig['PIC']['HOST'], dicArgs['logo_image'][0], '-bannerx')
            strBgColor = dicArgs['banner_bg_color'][0]
            strUrl = dicArgs['banner_url'][0]
            dicSort = self.bannerModel.findOne({'fields': ['max(sort) as sort']})
            intSort = 1 if dicSort['sort'] is None else dicSort['sort'] + 1
            self.bannerModel.insert({
                'key': 'title, image, bg_color, sort, link, last_update_time',
                'val': '\'{title}\', \'{image}\', \'{bg_color}\', {sort}, \'{link}\', {time}'.format(
                    title=strTitle, image=strImage, bg_color=strBgColor,
                    sort=intSort, link=strUrl, time=int(self.time.time())
                )
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def update(self, dicArgs):
        """
        :func: 更新banner
        :param dicArgs: banner参数
        """
        if 'banner_id' in dicArgs and 'banner_title' in dicArgs and 'logo_image' in dicArgs and \
                'banner_bg_color' in dicArgs and 'banner_url' in dicArgs:
            strId = dicArgs['banner_id'][0]
            strTitle = dicArgs['banner_title'][0]
            strImage = dicArgs['logo_image'][0]
            strBgColor = dicArgs['banner_bg_color'][0]
            strUrl = dicArgs['banner_url'][0]
            lisFields = ['title = \'{title}\''.format(title=strTitle),
                         'bg_color = \'{color}\''.format(color=strBgColor),
                         'link = \'{link}\''.format(link=strUrl),
                         'last_update_time = {time}'.format(time=int(self.time.time()))]
            if strImage:
                lisFields.append('image = \'{lb}\''.format(lb=strImage))
            self.bannerModel.update({
                'fields': lisFields,
                'condition': 'id = {id}'.format(id=strId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def delete(self, intId):
        """
        :func: 删除友链
        :param intId: 友链ID
        """
        self.bannerModel.delete({
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}
