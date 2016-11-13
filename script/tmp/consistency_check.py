# -*- coding:utf-8 -*-

import MySQLdb

# db online
DB_HOST = 'rdshf7hicnex6yhgi3h8.mysql.rds.aliyuncs.com'
DB_USER = 'yidao'
DB_PASS = ''
DB_BASE = 'yidao'

# DB_USER = 'yidao_test'
# DB_PASS = 'Okg8dEZh1laNrpmY'
# DB_BASE = 'yidao_test'

db = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_BASE, use_unicode=1, charset='utf8')


def findMany(db_obj, tbl_name):
    data = None
    cursor = db_obj.cursor()
    col = 'demand_id, status'
    if tbl_name == 'demand':
        col = 'id, status'
    sql = 'SELECT {col} FROM {tbl}'.format(col=col, tbl=tbl_name)
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
    except Exception, e:
        print e
    cursor.close()
    dic_data = {}
    if data is not None:
        for i in data:
            dic_data.setdefault(i[0], [])
            dic_data[i[0]].append(i[1])
    return dic_data

def findDemandIdAndMediaId(db_obj, tbl, lst):
    data = None
    cursor = db_obj.cursor()
    cond_str = ','.join([str(i) for i in lst])
    sql = 'SELECT demand_id, media_id FROM {tbl} WHERE demand_id in ({cond})'.format(tbl=tbl, cond=cond_str)
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
    except Exception, e:
        print e
    cursor.close()
    return data


def updateStatusByDemandId(db_obj, tbl, status, data):
    cursor = db_obj.cursor()
    set_str = 'status = {status}'.format(status=status)
    cond_str = 'demand_id = %s'
    if tbl == 'demand':
        cond_str = 'id = %s'
    sql = 'UPDATE {tbl} SET {s} WHERE {c}'.format(tbl=tbl, s=set_str, c=cond_str)
    try:
        cursor.executemany(sql, data)
        db_obj.commit()
    except Exception, e:
        print e
        db_obj.rollback()
    cursor.close()


def updateTakeOrderStatus(db_obj, status, data):
    cursor = db_obj.cursor()
    set_str = 'status = {status}'.format(status=status)
    cond_str = 'demand_id = %s and media_id = %s'
    sql = 'UPDATE demand_take_order SET {s} WHERE {c}'.format(s=set_str, c=cond_str)
    try:
        cursor.executemany(sql, data)
        db_obj.commit()
    except Exception, e:
        print e
        db_obj.rollback()
    cursor.close()


def check_all():
    demand = findMany(db, 'demand')
    take_order = findMany(db, 'demand_take_order')
    pay = findMany(db, 'order_pay')
    order = findMany(db, 'demand_order')
    feedback = findMany(db, 'demand_wechat_feedback')

    for demand_id in demand:
        demand_status = demand[demand_id][0]
        take_order_status = set(take_order.get(demand_id, []))
        pay_status = set(pay.get(demand_id, []))
        order_status = set(order.get(demand_id, []))
        feedback_status = set(feedback.get(demand_id, []))
        if demand_status == 1 or demand_status == 5:
            if take_order_status or pay_status or order_status or feedback_status:
                print '[ERR] demand_id:', demand_id, 'demand_status:', demand_status, '需求有多余的接单、支付、订单或反馈信息'
        elif demand_status == 2 or demand_status == 6 or demand_status == 7:
            if pay_status or order_status or feedback_status:
                print '[ERR] demand_id:', demand_id, 'demand_status:', demand_status, '需求有多余的支付、订单或反馈信息'
            if 4 in take_order_status:
                print '[ERR] demand_id:', demand_id, 'demand_status:', demand_status, '需求接单中，但有完成接单的信息'
            if 1 in take_order_status and (demand_status == 6 or demand_status == 7):
                print '[WAR] demand_id:', demand_id, 'demand_status:', demand_status, '接单信息需要由接单中变更为广告主撤销'
        elif demand_status == 3:
            if 1 in take_order_status or 4 not in take_order_status:
                print '[WAR] demand_id:', demand_id, 'demand_status:', demand_status, '需求营销中，但接单状态有接单中或无已完成'
            if 0 not in pay_status or (0 in pay_status and len(pay_status) > 1):
                print '[ERR] demand_id:', demand_id, 'demand_status:', demand_status, '需求营销中，但有失败的支付信息'
            if 4 in order and len(order) == 1:
                print '[ERR] demand_id:', demand_id, 'demand_status:', demand_status, '需求营销中，但所有订单已结束'
            if 0 in feedback and len(feedback) == 1:
                print '[ERR] demand_id:', demand_id, 'demand_status:', demand_status, '需求营销中，但所有反馈已验收'
        elif demand_status == 4:
            if 1 in take_order_status or 4 not in take_order_status:
                print '[WAR] demand_id:', demand_id, 'demand_status:', demand_status, '需求已结束，但接单状态有接单中或无已完成'
            if 0 not in pay_status or (0 in pay_status and len(pay_status) > 1):
                print '[ERR] demand_id:', demand_id, 'demand_status:', demand_status, '需求已结束，但有失败的支付信息'
            if 4 not in order_status or (4 in order_status and len(order_status) > 1):
                print '[ERR] demand_id:', demand_id, 'demand_status:', demand_status, '需求已结束，但有未结束的订单'
            if 0 not in feedback_status or (0 in feedback_status and len(feedback_status) > 1):
                print '[ERR] demand_id:', demand_id, 'demand_status:', demand_status, '需求已结束，但有未验收的反馈'
        else:
            print '[ERR] demand_id:', demand_id, 'demand_status:', demand_status, '未知的需求状态'

def switch():
    lst = [156, 166, 180, 291, 311, 325, 327, 328, 342, 343, 361, 362, 363, 364, 370, 371, 372, 373, 374, 375, 376,
           404, 405, 412, 413, 414, 542, 553, 563, 644, 645, 646, 647, 687, 688, 691, 693, 695, 697, 747, 748, 749,
           750, 768, 888, 1049, 1050, 1051, 1161, 1198, 1200, 1225, 1276, 1308, 1309, 1310, 1311, 1312, 1313, 1314,
           1316, 1415, 1451, 1452, 1453, 1490, 1491, 1492, 1493, 1494, 1495, 1497, 1498, 1499, 1500, 1501, 1502, 1503,
           1505, 1512, 1514, 1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1526, 1527, 1528, 1529, 1530, 1531, 1532,
           1534, 1535, 1536, 1537, 1538, 1539, 1540, 1558, 1559, 1560, 1563, 1564, 1566, 1567, 1570, 1586, 1587, 1588,
           1589, 1590, 1591, 1592, 1593, 1595, 1596, 1597, 1598, 1599, 1600, 1601, 1633, 1634, 1635, 1636, 1637, 1638,
           1639, 1640, 1641, 1642, 1643, 1644, 1645, 1646, 1647, 1650, 1651, 1652, 1655, 1656, 1658, 1659, 1663, 1689,
           1690, 1692, 1693, 1694, 1695, 1696, 1697, 1698, 1699, 1700, 1702, 1704, 1705, 1706, 1707, 1726, 1727, 1728,
           1729, 1730, 1731, 1732, 1733, 1734, 1735, 1736, 1738, 1740, 1741, 1742, 1744, 1745, 1746, 1747, 1748, 1749,
           1751, 1752, 1753, 1754, 1755, 1756, 1757, 1758, 1759, 1760, 1761, 1764, 1767, 1768, 1770, 1772, 1774, 1776,
           1780, 1781, 1783, 1784, 1945, 1946, 2047, 2048, 2150, 2200, 2210, 2211, 2214, 2218, 2226, 2235, 2241, 2242,
           2248, 2250, 2255, 2262, 2276, 2278, 2279, 2280, 2290, 2293, 2294, 2296, 2366, 2373, 2378, 2387, 2388, 2389,
           2391, 2397, 2402, 2404, 2410, 2414, 2415, 2418, 2423, 2425, 2426, 2430, 2437, 2441, 2446, 2448, 2450, 2451,
           2459, 2460, 2552]
    take_order = findMany(db, 'demand_take_order')
    pay = findMany(db, 'order_pay')
    order = findMany(db, 'demand_order')
    feedback = findMany(db, 'demand_wechat_feedback')
    ok = []
    war = []
    for demand_id in lst:
        take_order_status = take_order.get(demand_id, [])
        pay_status = pay.get(demand_id, [])
        order_status = order.get(demand_id, [])
        feedback_status = feedback.get(demand_id, [])
        print len(take_order_status), len(pay_status), len(order_status), len(feedback_status),
        if take_order_status and pay_status and order_status and feedback_status:
            print 'OK:', demand_id
            ok.append(demand_id)
        else:
            print 'WAR:', demand_id
            war.append(demand_id)
    print tuple(ok)
    print tuple(war)
    updateStatusByDemandId(db, 'demand', 4, ok)
    updateStatusByDemandId(db, 'demand_order', 4, ok)
    updateStatusByDemandId(db, 'demand_wechat_feedback', 0, ok)
    dto = set(findDemandIdAndMediaId(db, 'demand_take_order', ok))
    do = set(findDemandIdAndMediaId(db, 'demand_order', ok))
    cancel = list(dto - do)
    print cancel
    finish = list(do)
    print finish
    updateTakeOrderStatus(db, 3, cancel)
    updateTakeOrderStatus(db, 4, finish)


# check_all()

# switch()

db.close()
