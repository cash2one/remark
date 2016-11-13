# -*- coding:utf-8 -*-
# WEB 入口文件
# 通过web/conf/route.py文件来配置路由

# 设置环境，根据项目目录结构设置相对路径
import sys
sys.path.append("../")

import gflags
import logging

# Tornado框架
import tornado.web

# 配置文件
from conf.route import route
from conf.config import APP_CONF
from config.config import GLOBAL_CONF

# 应用框架
from source.config import merge_config
import source.controller as controller

Flags = gflags.FLAGS
gflags.DEFINE_string('appname', 'web', '应用名称')   ## 默认开发环境
gflags.DEFINE_string('mode', 'dev', '运行模式')   ## 默认开发环境
gflags.DEFINE_string('log_path', '', 'log路径')
gflags.DEFINE_string('address', '0.0.0.0', '全局访问')
gflags.DEFINE_integer('port', 2222, 'application port')
gflags.DEFINE_boolean('debug', True, 'whether debug')      ## 默认是调试环境

def init():
    Flags(sys.argv)

    common_setting = {}
    common_setting['mode']     = Flags.mode
    common_setting['log_path'] = Flags.log_path
    common_setting['address']  = Flags.address
    common_setting['port']     = Flags.port
    common_setting['debug']    = Flags.debug

    setting = merge_config(common_setting, GLOBAL_CONF, APP_CONF)

    logging.basicConfig(level   = setting['log_level'],
                        format  = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt = '%a, %d %b %Y %H:%M:%S',
                        filename= setting['log_path'],
                        filemode= 'w')

    route.append((r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=setting['static_path'])))
    route.append((r"/robots.txt", tornado.web.StaticFileHandler, dict(path=setting['robots'])))
    return setting

if __name__ == '__main__':
    # 参数初始化
    setting = init()

    # 启动服务
    controller.server().start(route, setting)
