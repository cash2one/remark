#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 路由配置
# 增加控制器, 导入控制器文件引用类，并修改route list

# 自定义控制器，增加路由
import controller.index as Index
import controller.list as List
import controller.demand as Demand
import controller.account as Account
import controller.union as Union
import controller.media as Media
import controller.wechat as Wechat
import controller.user as User
import controller.area as Area
import controller.pay as Pay
import controller.about as About
import controller.error as Error
import controller.case as case
import controller.debug as Debug


route = [
	(r"/",              Index.index),
	(r"/login",         Account.Login),
	(r"/account",       Account.Account),
	(r"/wechat_login",  Account.WechatLogin),
	(r"/bind_wechat",   Account.BindWechat),
#	(r"/register",      Account.Register),
	(r"/list\/*",       List.List),
	(r"/demand\/*",     Demand.demand),
	(r"/media\/*",      Media.Media),
	(r"/wechat_submit", User.WechatSubmit),
	(r"/wechat_message", User.WechatMessage),
	(r"/wechat_bind",   User.WechatBind),
	(r"/wechat\/*",     Wechat.Wechat),
	(r"/union\/*",      Union.Union),
	(r"/user\/*",       User.User),
	(r"/area\/*",       Area.Area),
	(r"/pay\/*",        Pay.Pay),
	(r"/u",             User.U),
	(r"/pay/return\/*", Pay.Return),
	(r"/pay/notify\/*", Pay.Notify),
    (r"/pay/wallet\/*", Pay.Wallet),
	(r"/case\/*",       case.case),
	(r"/about\/*",      About.About),
	(r"/debug",         Debug.Debug),
	(r".*",             Error.error),
]

