# -*- coding:utf-8 -*-
# 设置环境，根据项目目录结构设置相对路径
import sys
sys.path.append("..")

import time

import gflags
import logging
import MySQLdb
import requests

# 配置文件
from config.config import GLOBAL_CONF
from source.config import merge_config

db = None

######################################################################################
def demand_overdue(db_obj):
    cursor = db_obj.cursor()
    # 审核中和接单中的需求过期后状态变更为已过期(6)
    sql = 'UPDATE demand SET status = 6 WHERE status in (1, 2) and time_end < {t}'.format(t=int(time.time()))
    logging.info(sql)
    try:
        n = cursor.execute(sql)
        db_obj.commit()
        logging.info('{t} expiry demand number: {n}'.format(t=time.strftime('%Y-%m-%d'), n=n))
    except Exception, e:
        logging.error(e)
        db_obj.rollback()
    cursor.close()


def find_demand_id_overdue(db_obj):
    data = None
    cursor = db_obj.cursor()
    # 查找所有已过期的需求id
    sql = 'SELECT id FROM demand WHERE status = 6'
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        data = [i[0] for i in data]
    except Exception, e:
        logging.error(e)
    cursor.close()
    return data


def update_take_order_status(db_obj, data):
    cursor = db_obj.cursor()
    # 过期的需求设置接单信息为广告主取消
    sql = 'UPDATE demand_take_order SET status = 3 WHERE demand_id = %s AND status = 1'
    try:
        n = cursor.executemany(sql, data)
        db_obj.commit()
        logging.info('{t} cancel take_order number: {n}'.format(t=time.strftime('%Y-%m-%d'), n=n))
    except Exception, e:
        logging. warning(e)
        db_obj.rollback()
    cursor.close()

def run():
    demand_overdue(db)
    ids = find_demand_id_overdue(db)
    update_take_order_status(db, ids)
    #requests.post('/overdue_msg',data= ids)
#####################################################################################

Flags = gflags.FLAGS
gflags.DEFINE_string('mode', 'dev', '运行模式')   ## 默认开发环境
gflags.DEFINE_string('log_path', '', 'log路径')

def init():
    Flags(sys.argv)

    common_setting = {}
    common_setting['mode']     = Flags.mode
    common_setting['log_path']        = Flags.log_path
    setting = merge_config(common_setting, GLOBAL_CONF, {})

    logging.basicConfig(level   = logging.INFO,
                        format  = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt = '%a, %d %b %Y %H:%M:%S',
                        filename= setting['log_path'],
                        filemode= 'w')
    logging.info(setting['DB_BASE'])
    global db
    db = MySQLdb.connect(setting['DB_HOST'], setting['DB_USER'], setting['DB_PASS'], setting['DB_BASE'], use_unicode=1, charset='utf8')

def finish():
    db.close()

if __name__ == '__main__':
    init()
    run()
    finish()
