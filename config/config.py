#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 配置文件
import logging

GLOBAL_CONF = {
	# 是否开启调试模式。在调试模式中，修改文件不需要重启服务，且会将错误信息输出到页面
	'debug': True,

    'port' : 2222,          ## 默认启动端口
    'address' : '0.0.0.0',  ## 外网可以访问

    'log_path' : '',        ## log输出文件路径
    'log_level' : logging.WARN,

	# API设置
	'API_KEY': '6HpseTqN2EUfhkUi',

	# COOKIE设置
	'cookie_secret': '([x4DcNKNJWsq)D-Fm#P',
    # 'xsrf_cookies': True,

	# 数据库
	'online' 	: { # MySQL
                    'isDataBase'    : False, # 是否使用数据库，默认为False
                    'DB_HOST'	    : 'rdshf7hicnex6yhgi3h8.mysql.rds.aliyuncs.com',
                    'DB_USER'	    : 'yidao',
					'DB_PASS'	    : '',
					'DB_BASE'	    : 'yidao',
					'DB_ADMIN'      : 'yidao_admin',
					'DB_STAT'       : 'yidao_stat',
					'DB_PROJECT'    : 'yidao_profile',

                    # Redis
                    'isRedis'       : False, # 是否使用Redis，默认为False
                    'REDIS_HOST'    : '123.57.29.208',
                    'REDIS_PORT'    : '6379',
                    'REDIS_PASS'    : '1234',
                    'REDIS_DB_ADMIN': '0',

                    # MongoDB
                    'isMongoDB'     : False, # 是否使用MongoDB，默认为False
                    'MONGODB_HOST'  : '10.170.195.36',
                    'MONGODB_PORT'  : '27018',
                    'MONGODB_USER'  : 'yidao',
                    'MONGODB_PASS'  : '',
                    'MONGODB_DB'    : 'media',

                    ## 推荐域名
					'RECO_HOST'     : 'http://reco.yidao.info',
				},

	'test' 		: {	# MySQL
                    'isDataBase'    : False, # 是否使用数据库，默认为False
                    'DB_HOST'	    : 'rdshf7hicnex6yhgi3h8.mysql.rds.aliyuncs.com',
                    'DB_USER'	    : 'yidao_test',
					'DB_PASS'	    : '4oKcexds3ohgfCAQ',
					'DB_BASE'	    : 'yidao_test',
					'DB_ADMIN'      : 'yidao_admin_test',
					'DB_STAT'       : 'yidao_stat_test',
					'DB_PROJECT'    : 'yidao_profile_dev',

                    # Redis
                    'isRedis'       : False, # 是否使用Redis，默认为False
                    'REDIS_HOST'    : '123.57.29.208',
                    'REDIS_PORT'    : '6379',
                    'REDIS_PASS'    : '1234',
                    'REDIS_DB_ADMIN': '0',

                    # MongoDB
                    'isMongoDB'     : False, # 是否使用MongoDB，默认为False
                    'MONGODB_HOST'  : '123.57.29.208',
                    'MONGODB_PORT'  : '27018',
                    'MONGODB_USER'  : 'yidao_dev',
                    'MONGODB_PASS'  : 'uvT8IohyxkVSJGbO',
                    'MONGODB_DB'    : 'media',

                    ## 推荐域名
					'RECO_HOST'     : 'http://recotest.rangedigit.com',
				},

	'dev'		: {	# MySQL
                    'isDataBase'    : False, # 是否使用数据库，默认为False
                    'DB_HOST'	    : 'rdshf7hicnex6yhgi3h8.mysql.rds.aliyuncs.com',
                    'DB_USER'	    : 'yidao_dev',
					'DB_PASS'	    : 'gDAyDf8LK62dts5r',
					'DB_BASE'	    : 'yidao_new',
					'DB_ADMIN'      : 'yidao_admin_new',
                    'DB_STAT'       : 'yidao_stat_new',
					'DB_PROJECT'    : 'yidao_profile_dev',

                    # redis
                    'isRedis'       : False, # 是否使用Redis，默认为False
                    'REDIS_HOST'    : '123.57.29.208',
                    'REDIS_PORT'    : '6379',
                    'REDIS_PASS'    : '1234',
                    'REDIS_DB_ADMIN': '0',

                    # MongoDB
                    'isMongoDB'     : False, # 是否使用MongoDB，默认为False
                    'MONGODB_HOST'  : '123.57.29.208',
                    'MONGODB_PORT'  : '27018',
                    'MONGODB_USER'  : 'yidao_dev',
                    'MONGODB_PASS'  : 'uvT8IohyxkVSJGbO',
                    'MONGODB_DB'    : 'media',

                    ## 推荐域名
					'RECO_HOST'     : 'http://recodev.rangedigit.com',
				},

	# 静态文件目录
	'static_path'   : 'static',
	'template_path' : 'view',
    'robots'        : 'robots.txt',
    'ueconfig_dir'  : 'static/images',

	# 登录地址 当用户未登录时，系统跳到此地址
	'login_url': '/',
	
	# 模板设置
	'VIEW_PATH': '../view',

	'UPLOAD_PATH': '.',

	# WEB title
	'title': '一道自媒体交易平台',

	# 图片地址
	'PIC': {
		'HOST': 'http://7sbnkf.com2.z0.glb.qiniucdn.com/',
		'SUFFIX': '-blog'
	},
	
	## 错误码
	'DB_OK'     : 200,
	'DB_ERROR'  : 500,

    'SERIVCE_OK'                        : 200,
    'SERIVCE_PARAM_ERROR'               : 401,
    'SERVICE_DB_ERROR'                  : 500,

    'SERVICE_ACCOUNT_NOT_EXIST_ERROR'   : 601,
    'SERVICE_ACCOUNT_EXIST_ERROR'       : 602,
    'SERVICE_ACCOUNT_PASSWORD_ERROR'    : 603,

    'SERVICE_USER_NOT_EXIST_ERROR'      : 701,
    'SERVICE_USER_EXIST_ERROR'          : 702,

    'SERVICE_USER_EXPORT_MAX_ERROR'     : 1001,
    'SERVICE_USER_EXPORT_DAY_MAX_ERROR' : 1002,
}
