# -*- coding:utf-8 -*-

import base as base


# 联盟Service
class service(base.baseService):
    def __init__(self, model, param):

        base.baseService.__init__(self, model, param)

        self.unionModel = self.importModel('union')

    def top(self):
        """ 排行榜
        """

        self.unionModel.strTableName = 'uniontops as ut'
        tupData = self.unionModel.findMany({
            'join': 'pt_unions as u ON (ut.union_id = u.id)',
            'demand': 'ut.sort asc'
        })
        lisData = []
        if tupData:
            for item in tupData:
                # 处理图片
                item['logo'] = '%s%s%s' % (self.dicConfig['PIC']['HOST'], item['logo'], '-union')

                lisData.append(item)

        return lisData

    def myUnion(self, strUserId):
        """ 我的联盟
        """

        if not strUserId:
            return 401

        tupData = self.unionModel.findMany({
            'condition': 'user_id = "%s"' % strUserId
        })

        lisData = []
        lisUser = []
        if tupData:
            for item in tupData:
                # 处理图片
                item['logo'] = '%s%s%s' % (self.dicConfig['PIC']['HOST'], item['logo'], '-union')
                # 用户
                lisUser.append(str(item['user_id']))
                # 成员数
                dicMember = self.unionModel.get_member_count(item['id'])
                item['member'] = dicMember['count']

                lisData.append(item)

            # 处理用户
            dicUser = {}
            accountService = self.importService('account')
            tupUser = accountService.get_list(','.join(lisUser))
            if tupUser:
                for item in tupUser:
                    dicUser[item['user_id']] = item

            for k, item in enumerate(lisData):
                lisData[k]['username'] = dicUser[item['user_id']]['nickname']

        return lisData

    def create(self, dicData):
        """ 创建联盟

        @params dicData dict 数据
        """

        if 'name' not in dicData.keys() or 'logo' not in dicData.keys() \
                or 'desc' not in dicData.keys() or 'category' not in dicData.keys() \
                or 'user_id' not in dicData.keys():
            return 401

        strCreateTime = self.formatTime(int(self.time.time()), '%Y-%m-%d %H:%M:%S')
        intUnionId = self.unionModel.insert({
            'key': 'user_id, name, logo, `desc`, tel, create_time',
            'val': '"%s", "%s", "%s", "%s", "%s", "%s"' % (
                dicData['user_id'],
                dicData['name'],
                dicData['logo'],
                dicData['desc'],
                dicData['tel'],
                strCreateTime
            )
        })

        # 生成分类对应数据
        if intUnionId:
            lisCategory = dicData['category'].split(',')
            for item in lisCategory:
                if item:
                    self.unionModel.insert_category({
                        'key': 'union_id, category_id',
                        'val': '"%s", "%s"' % (intUnionId, item)
                    })

            # 生成管理员
            self.unionModel.insert_member({
                'key': 'union_id, user_id, create_time, status',
                'val': '"%s", "%s", "%s", "%s"' % (
                    intUnionId,
                    dicData['user_id'],
                    strCreateTime,
                    4
                )
            })
            if self.model.db.status != 200:
                return 601
            return 200

    def update(self, dicData):
        """ 更新联盟信息

        @params dicData dict 数据
            dicData['union_id'] 联盟ID
            dicData['user_id'] 用户ID
            dicData['name'] 联盟名称
            dicData['logo'] 联盟LOGO
            dicData['desc'] 联盟简介
            dicData['category'] 分类
            dicData['tel'] 联系电话
        """

        if 'name' not in dicData.keys() or 'logo' not in dicData.keys() \
                or 'desc' not in dicData.keys() or 'category' not in dicData.keys() \
                or 'user_id' not in dicData.keys() or 'union_id' not in dicData.keys():
            return 401

        # 更新联盟信息
        self.unionModel.update({
            'fields': ['name = "%s"' % dicData['name'], 'logo = "%s"' % dicData['logo'],
                       '`desc` = "%s"' % dicData['desc'], 'tel = "%s"' % dicData['tel']],
            'condition': 'id = "%s" and user_id = "%s"' % (dicData['union_id'], dicData['user_id'])
        })

        # 处理分类
        # 删除现在分类
        self.unionModel.del_union_category(dicData['union_id'])
        # 添加新分类
        lisCategory = dicData['category'].split(',')
        for item in lisCategory:
            if item:
                self.unionModel.insert_category({
                    'key': 'union_id, category_id',
                    'val': '"%s", "%s"' % (dicData['union_id'], item)
                })

        if self.model.db.status != 200:
            return 601
        return 200

    def get_list(self, dicData):
        """ 获取列表
        """

        strPageCount = 20
        strStartLimit = dicData['page'] * strPageCount if dicData['page'] > 1 else 0

        if dicData['category']:
            tupUnion = self.unionModel.findPaginateByCategory({
                'fields': ['u.*', 'uc.category_id'],
                'condition': 'uc.category_id = "%s"' % dicData['category'],
                'join': 'pt_unions as u ON (uc.union_id = u.id)',
                'page': dicData['page'],
                'limit': ['%s' % strStartLimit, '%s' % strPageCount],
                'order': 'u.id desc'
            })
        else:
            tupUnion = self.unionModel.findPaginate({
                'page': dicData['page'],
                'limit': ['%s' % strStartLimit, '%s' % strPageCount],
                'order': 'id desc'
            })

        lisUnion = []
        lisUnionId = []
        dicUser = {}
        dicCategory = {}
        if tupUnion[0]:
            for item in tupUnion[0]:
                # 处理图片
                item['logo'] = '%s%s%s' % (self.dicConfig['PIC']['HOST'], item['logo'], '-union')

                # 描述截取
                item['desc'] = item['desc'][0:50] + '...' if len(item['desc']) > 50 else item['desc']

                # 创建者
                item['master'] = ''
                # 成员
                item['member'] = []

                # 读取联盟成员信息
                lisMember = []
                tupMembers = self.unionModel.get_member(item['id'], '1,4')
                if tupMembers:
                    for value in tupMembers:
                        # 处理图片
                        value['avatar'] = '%s%s%s' % (self.dicConfig['PIC']['HOST'], value['avatar'], '-avatar')

                        if value['status'] == 4:
                            item['master'] = value['nickname']

                        lisMember.append(value)

                    item['member'] = lisMember

                # 成员总数
                dicMemberCount = self.unionModel.get_member_count(item['id'])
                item['member_count'] = dicMemberCount['count']

                lisUnion.append(item)
                lisUnionId.append(str(item['id']))

            # 处理分类
            dicCategory = self.get_union_category(lisUnionId)

        return {
            'list': lisUnion,
            'count': tupUnion[1],
            'member': dicUser,
            'category': dicCategory
        }

    def detail(self, strUnionId):
        """ 联盟详情

        @params strUnionId string 联盟ID
        """

        dicData = self.unionModel.findOne(strUnionId)
        if not dicData:
            return None

        # 处理图片
        dicData['logo_key'] = dicData['logo']
        dicData['logo'] = '%s%s%s' % (self.dicConfig['PIC']['HOST'], dicData['logo'], '-union')

        # 处理分类
        dicData['category'] = self.get_union_category(strUnionId)
        lisCategoryId = []
        if int(strUnionId) in dicData['category'].keys():
            if dicData['category'][int(strUnionId)]:
                for item in dicData['category'][int(strUnionId)]:
                    lisCategoryId.append(str(item['category_id']))

        dicData['category_id'] = ','.join(lisCategoryId)

        return dicData

    def get_union_category(self, unionId):
        """ 处理联盟分类

        @params lisUnionId list, string 联盟ID
        """

        dicCategory = {}
        strUnionId = ''

        if isinstance(unionId, str):
            strUnionId = unionId
        elif isinstance(unionId, list):
            strUnionId = ','.join(unionId)

        tupUnionCategory = self.unionModel.get_union_category(strUnionId)
        if tupUnionCategory:
            for item in tupUnionCategory:
                if item['union_id'] not in dicCategory:
                    dicCategory[item['union_id']] = []

                dicCategory[item['union_id']].append(item)

        return dicCategory

    def get_union_member(self, strUnionId, strUserId=None):
        """ 通过用户ID和联盟ID来读取信息

        @params strUnionId string 联盟ID
        @params strUserId string 用户ID　
        """

        dicModelData = {
            'condition': 'union_id = "%s"' % strUnionId
        }

        if strUserId:
            dicModelData['condition'] += ' and user_id = "%s"' % strUserId

        dicData = self.unionModel.get_union_member(dicModelData)

        return dicData

    def get_union_member_user(self, strUnionId, strStatus):
        """ 通过用户ID和联盟ID来读取信息

        @params strUnionId string 联盟ID
        """

        intTotalOfficial = 0
        tupData = self.unionModel.get_member(strUnionId, strStatus)
        if tupData:
            officialService = self.importService('official')
            for k, item in enumerate(tupData):
                # 处理头像
                tupData[k]['avatar'] = self.getAvatarUrl(item['avatar'])
                # 自媒体
                dicOfficial = officialService.official_list(item['user_id'])
                if dicOfficial['list']:
                    for key, value in enumerate(dicOfficial['list']):
                        dicOfficial['list'][key]['avatar'] = self.getAvatarUrl(value['avatar'])

                intTotalOfficial = intTotalOfficial + dicOfficial['count']
                tupData[k]['official'] = dicOfficial

        return {
            'list': tupData,
            'count': intTotalOfficial,
            'member_count': len(tupData)
        }

    def apply_union_member(self, dicData):
        """ 申请联盟成员

        @params dicData dict 数据
            dicData['union_id'] 联盟ID
            dicData['user_id'] 用户ID
        """

        if 'union_id' not in dicData.keys():
            return 401

        # 判断是否已经存在
        dicMember = self.unionModel.get_union_member({
            'condition': 'union_id = "%s" and user_id = "%s"' % (dicData['union_id'], dicData['user_id'])
        })
        if dicMember:
            if dicMember['status'] == 1 or dicMember['status'] == 4:
                return 602

        strCreateTime = self.formatTime(int(self.time.time()), '%Y-%m-%d %H:%M:%S')
        if dicMember:
            self.unionModel.update_member({
                'fields': ['status = 2'],
                'condition': 'union_id = "%s" and user_id = "%s"' % (dicData['union_id'], dicData['user_id'])
            })
        else:
            self.unionModel.apply_union_member({
                'key': 'union_id, user_id, create_time, status',
                'val': '"%s", "%s", "%s", 2' % (dicData['union_id'], dicData['user_id'], strCreateTime)
            })

        # 重计联盟成员数
        dicUnionMember = self.unionModel.get_member_count(dicData['union_id'])
        self.unionModel.update({
            'fields': ['member_num = "%s"' % dicUnionMember['count']],
            'condition': 'id = "%s"' % dicData['union_id']
        })

        if self.model.db.status != 200:
            return 601
        return 200

    def allow_member(self, dicData):
        """ 通过或拒绝
        """
        # 判断成员状态
        dicMember = self.unionModel.get_union_member({
            'condition': 'id = "%s"' % dicData['id']
        })
        if dicMember['status'] == 4:
            return 701

        self.unionModel.update_member({
            'fields': ['status = "%s"' % dicData['status']],
            'condition': 'id = "%s"' % dicData['id']
        })
        if self.model.db.status != 200:
            return 601
        return 200

    def dissolve(self, dicData):
        """ 解散联盟

        @params dicData dict 数据
            dicData['id'] 联盟ID
            dicData['user_id'] 用户ID
        """

        if 'id' not in dicData.keys() or 'user_id' not in dicData.keys():
            return 401

        self.unionModel.delete({
            'condition': 'id = "%s" and user_id = "%s"' % (dicData['id'], dicData['user_id'])
        })
        if self.model.db.status != 200:
            return 601
        return 200
