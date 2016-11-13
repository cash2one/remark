#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 路由配置
# 增加控制器, 导入控制器文件引用类，并修改route list

# import tornado.web
# import config

# 自定义控制器，增加路由
from controller.index import index
from controller.demand import demand
from controller.media import media

from controller.union import union
from controller.user import user
import controller.admin_user as au
import controller.statistics as st
import controller.index_op as index_op
import controller.setup as su

from controller.media_paper import paper
from controller.media_wechat import wechat
from controller.media_wechat_friend import wechat_friend
from controller.media_community import community
from controller.media_zhihu import zhihu
from controller.media_weibo import weibo
from controller.media_league import league
from controller.media_toutiao import toutiao

from controller.pf_plan import plan as pf_plan
from controller.pf_feedback import feedback as pf_feedback
from controller.pf_advertiser import advertiser as pf_advertiser
from controller.pf_demand import demand as pf_demand
from controller.pf_documents import documents as pf_documents
from controller.pf_planning import planning as pf_planning
from controller.pf_documents import Ue_ImageUp

from controller.error import error
from controller.account import login
from controller.demand import order
from controller.demand import appeal

from controller.metadata import category
from controller.metadata import tag

route = [
    (r"/", index),
    (r"/login", login),
    (r"/demand", demand),
    (r"/yidao/media", media),
    (r"/union", union),
    (r"/user", user),

    (r"/admin_user/center", au.center),
    (r"/admin_user/media_follow", au.media_follow),
    (r"/admin_user/demand_follow", au.demand_follow),
    (r"/admin_user/user_manage", au.user_manage),
    (r"/admin_user/role_manage", au.role_manage),
    (r"/admin_user/module_manager", au.module_manager),
    (r"/admin_user/passwd_manager", au.passwd_manage),
    (r"/admin_user/advertiser_follow", au.advertiser_follow),
    (r"/admin_user/document_follow", au.document_follow),
    (r"/admin_user/plan_follow", au.plan_follow),
    (r"/admin_user/planning_follow", au.planning_follow),

    (r"/statistics/web", st.statistics),
    (r"/statistics/business", st.business),
    (r"/statistics/operation", st.operation),

    (r"/setup/properties", su.properties),

    (r"/demand/order", order),
    (r"/demand/appeal", appeal),

    (r"/index_op/wechat", index_op.wechat),
    (r"/index_op/friendlink", index_op.friendlink),
    (r"/index_op/blog", index_op.blog),
    (r"/index_op/media", index_op.media),
    (r"/index_op/media_revenue_top", index_op.media_revenue_top),
    (r"/index_op/media_star", index_op.media_star),
    (r"/index_op/banner", index_op.banner),
    (r"/index_op/demand", index_op.demand),
    (r"/index_op/ad", index_op.ad),
    (r"/index_op/notice", index_op.notice),
    (r"/index_op/case", index_op.case),

    (r"/media/wechat", wechat),
    (r"/media/paper", paper),
    (r"/media/wechat_friend", wechat_friend),
    (r"/media/community", community),
    (r"/media/zhihu", zhihu),
    (r"/media/weibo", weibo),
    (r"/media/league", league),
    (r"/media/toutiao", toutiao),

    (r"/profile/feedback", pf_feedback),
    (r"/profile/advertiser", pf_advertiser),
    (r"/profile/plan", pf_plan),
    (r"/profile/demand", pf_demand),
    (r"/profile/documents", pf_documents),
    (r"/profile/imageup", Ue_ImageUp),
    (r"/profile/planning", pf_planning),

    (r"/metadata/category", category),
    (r"/metadata/tag", tag),

    (r".*", error),
]
