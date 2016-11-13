# -*- coding:utf-8 -*-

import base as base

# 联盟
class Union(base.base):
    
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

        self.unionService = self.importService('union')

    def index(self):

        # 获取参数
        strPage = self.I('page')
        intPage = int(strPage) if strPage else 1
        strCategory = self.I('category')
        dicRequestData = {
            'page': intPage,
            'category': strCategory
        }

        # 联盟列表
        lisUnion = self.unionService.get_list(dicRequestData)
    
        # 引用Service
        categoryService = self.importService('category')
        
        # 常用分类
        tupCategoryCommon = categoryService.commonUse()

        self.dicViewData['category_common'] = tupCategoryCommon
        self.dicViewData['union'] = lisUnion['list']
        self.dicViewData['member'] = lisUnion['member']
        self.dicViewData['category'] = lisUnion['category']
        self.dicViewData['page'] = self.page(intPage, 20, lisUnion['count'], '/union?a=index&catgory=' + strCategory)
        self.dicViewData['category_focus'] = strCategory
        
        self.display('index')

    def view(self):
        """ 联盟详情
        """

        # 获取参数
        strUnionId = self.I('id')
        if not strUnionId:
            self.redirect('/404')
            return

        # 联盟信息
        dicUnion = self.unionService.detail(strUnionId)
        if not dicUnion:
            self.redirect('/404')
            return

        intUnionUserStatus = 0
        # 判断已登录用户在联盟中的状态
        strUserId = self.current_user['user_id']
        if strUserId:
            dicUnionUser = self.unionService.get_union_member(strUnionId, strUserId)
            if dicUnionUser:
                intUnionUserStatus = dicUnionUser['status']

        # 联盟成员
        tupUnionMember = self.unionService.get_union_member_user(strUnionId, '1,4')

        self.dicViewData['union'] = dicUnion
        self.dicViewData['union_user_status'] = intUnionUserStatus
        self.dicViewData['member'] = tupUnionMember['list']
        self.dicViewData['official_count'] = tupUnionMember['count']

        self.display('view')

    def manage(self):
        """ 联盟管理
        """

        # 需要登录用户
        self.isAuth = True
        
        # 获取参数
        strUnionId = self.I('id')

        if self._POST:
            dicRequestData = {
                'union_id': strUnionId,
                'user_id': self.current_user['user_id'],
                'name': self.I('name'),
                'logo': self.I('logo'),
                'desc': self.I('desc'),
                'category': self.I('category'),
                'tel': self.I('tel')
            }
            
            if not dicRequestData['union_id'] or not dicRequestData['name'] or not dicRequestData['logo'] \
                or not dicRequestData['desc'] or not dicRequestData['category'] or not dicRequestData['tel']:
                    self.out(401)
                    return

            intStatus = self.unionService.update(dicRequestData)
            self.out(intStatus)
            return
        
        if not strUnionId:
            self.redirect('/404')
            return

        # 联盟信息
        dicUnion = self.unionService.detail(strUnionId)
        if not dicUnion or dicUnion['user_id'] != self.current_user['user_id']:
            self.redirect('/404')
            return
        
        categoryService = self.importService('category')
        # 获取所有分类
        dicCategory = categoryService.getAll()
        # 在线联盟成员
        tupUnionMember = self.unionService.get_union_member_user(strUnionId, '1, 4')
        # 申请联盟成员
        tupUnionMemberApply = self.unionService.get_union_member_user(strUnionId, '2')

        self.dicViewData['category'] = dicCategory
        self.dicViewData['union'] = dicUnion
        self.dicViewData['member'] = tupUnionMember
        self.dicViewData['member_apply'] = tupUnionMemberApply

        self.display('manage')

    def apply(self):
        """ 申请加入联盟
        """

        if not self._POST:
            self.out(501)
            return

        if 'user_id' not in self.current_user.keys():
            self.out(600)
            return

        # 获取参数
        dicRequestData = {
            'union_id': self.I('union_id'),
            'user_id': self.current_user['user_id']
        }

        if not dicRequestData['union_id']:
            self.out(401)
            return

        # 写数据
        intStatus = self.unionService.apply_union_member(dicRequestData)
        self.out(intStatus)

    def allow_member(self):
        """ 通过与拒绝 
        """
        
        if not self._POST:
            self.out(501)
            return

        if 'user_id' not in self.current_user.keys():
            self.out(600)
            return

        # 获取参数
        dicRequestData = {
            'id': self.I('id'),
            'status': self.I('status'),
            'user_id': self.current_user['user_id']
        }

        if not dicRequestData['id']:
            self.out(401)
            return

        # 写数据
        intStatus = self.unionService.allow_member(dicRequestData)
        self.out(intStatus)

    def dissolve(self):
        """ 解散联盟
        """
        
        if not self._POST:
            self.out(501)
            return

        if 'user_id' not in self.current_user.keys():
            self.out(600)
            return

        # 获取参数
        dicRequestData = {
            'id': self.I('union_id'),
            'user_id': self.current_user['user_id']
        }

        if not dicRequestData['id']:
            self.out(401)
            return

        # 写数据
        intStatus = self.unionService.dissolve(dicRequestData)
        self.out(intStatus)









