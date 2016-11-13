# -*- coding: utf-8 -*-
'''
Created on 2011-4-21
支付宝接口
@author: Yefe
'''
import types
from urllib import urlencode, urlopen
import hashlib

# 安全检验码，以数字和字母组成的32位字符
ALIPAY_KEY = 'acl1q8yxsnts1legfs2wapzdecxsy5nn'

ALIPAY_INPUT_CHARSET = 'utf-8'

# 合作身份者ID，以2088开头的16位纯数字
ALIPAY_PARTNER = '2088712069253443'

# 签约支付宝账号或卖家支付宝帐户
ALIPAY_SELLER_EMAIL = 'p@rangedigit.com'

ALIPAY_SIGN_TYPE = 'MD5'

# 付完款后跳转的页面（同步通知） 要用 http://格式的完整路径，不允许加?id=123这类自定义参数
#ALIPAY_RETURN_URL='http://192.168.0.130:2111/pay/return'
ALIPAY_RETURN_URL='pay/return'

# 交易过程中服务器异步通知的页面 要用 http://格式的完整路径，不允许加?id=123这类自定义参数
ALIPAY_NOTIFY_URL='pay/notify'

ALIPAY_SHOW_URL=''

# 访问模式,根据自己的服务器是否支持ssl访问，若支持请选择https；若不支持请选择http
ALIPAY_TRANSPORT='http'

def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    if not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s

# 网关地址
_GATEWAY = 'https://mapi.alipay.com/gateway.do?'


# 对数组排序并除去数组中的空值和签名参数
# 返回数组和链接串
def params_filter(params):
    ks = params.keys()
    ks.sort()
    newparams = {}
    prestr = ''
    for k in ks:
        v = params[k]
        k = smart_str(k, ALIPAY_INPUT_CHARSET)
        if k not in ('sign','sign_type') and v != '':
            newparams[k] = smart_str(v, ALIPAY_INPUT_CHARSET)
            prestr += '%s=%s&' % (k, newparams[k])
    prestr = prestr[:-1]
    return newparams, prestr


# 生成签名结果
def build_mysign(prestr, key, sign_type = 'MD5'):
    if sign_type == 'MD5':
        return hashlib.md5(prestr + key).hexdigest()
    return ''


# 即时到账交易接口
def create_direct_pay_by_user(tn, bank, subject, body, total_fee, base_url):
    params = {}
    params['service']       = 'create_direct_pay_by_user'
    params['payment_type']  = '1'
    
    # 获取配置文件
    params['partner']           = ALIPAY_PARTNER
    params['seller_id']         = ALIPAY_PARTNER  
    params['seller_email']      = ALIPAY_SELLER_EMAIL
    params['return_url']        = base_url + ALIPAY_RETURN_URL
    params['notify_url']        = base_url + ALIPAY_NOTIFY_URL
    params['_input_charset']    = ALIPAY_INPUT_CHARSET
    params['show_url']          = ALIPAY_SHOW_URL
    
    # 从订单数据中动态获取到的必填参数
    params['out_trade_no']  = tn        # 请与贵网站订单系统中的唯一订单号匹配
    params['subject']       = subject   # 订单名称，显示在支付宝收银台里的“商品名称”里，显示在支付宝的交易管理的“商品名称”的列表里。
    params['body']          = body      # 订单描述、订单详细、订单备注，显示在支付宝收银台里的“商品描述”里
    params['total_fee']     = total_fee # 订单总金额，显示在支付宝收银台里的“应付总额”里
    
#     # 扩展功能参数——网银提前
#     params['paymethod'] = 'directPay'   # 默认支付方式，四个值可选：bankPay(网银); cartoon(卡通); directPay(余额); CASH(网点支付)
#     params['defaultbank'] = ''          # 默认网银代号，代号列表见http://club.alipay.com/read.php?tid=8681379
    # 扩展功能参数——网银提前  
    if bank=='alipay' or bank=='':  
        params['paymethod'] = 'directPay'   # 支付方式，四个值可选：bankPay(网银); cartoon(卡通); directPay(余额); CASH(网点支付)  
        params['defaultbank'] = ''          # 支付宝支付，这个为空  
    else:  
        params['paymethod'] = 'bankPay'     # 默认支付方式，四个值可选：bankPay(网银); cartoon(卡通); directPay(余额); CASH(网点支付)  
        params['defaultbank'] = bank      # 默认网银代号，代号列表见http://club.alipay.com/read.php?tid=8681379            
    # 扩展功能参数——防钓鱼
    params['anti_phishing_key'] = ''
    params['exter_invoke_ip'] = ''
    
    # 扩展功能参数——自定义参数
    params['buyer_email'] = ''
    params['extra_common_param'] = ''
    
    # 扩展功能参数——分润
    params['royalty_type'] = ''
    params['royalty_parameters'] = ''
    
    params,prestr = params_filter(params)
    
    params['sign'] = build_mysign(prestr, ALIPAY_KEY, ALIPAY_SIGN_TYPE)
    params['sign_type'] = ALIPAY_SIGN_TYPE
    
    return _GATEWAY + urlencode(params)
    
    
# 纯担保交易接口
def create_partner_trade_by_buyer (tn, subject, body, price, base_url):
    params = {}
    # 基本参数
    params['service']       = 'create_partner_trade_by_buyer'
    params['partner']           = ALIPAY_PARTNER
    params['_input_charset']    = ALIPAY_INPUT_CHARSET
    params['notify_url']        = '{}{}'.format(base_url, ALIPAY_NOTIFY_URL)
    params['return_url']        = '{}{}'.format(base_url, ALIPAY_RETURN_URL)

    # 业务参数
    params['out_trade_no']  = tn        # 请与贵网站订单系统中的唯一订单号匹配
    params['subject']       = subject   # 订单名称，显示在支付宝收银台里的“商品名称”里，显示在支付宝的交易管理的“商品名称”的列表里。
    params['payment_type']  = '1'
    params['logistics_type'] = 'POST'   # 第一组物流类型
    params['logistics_fee'] = '0.00'
    params['logistics_payment'] = 'BUYER_PAY'
    params['price'] = price             # 订单总金额，显示在支付宝收银台里的“应付总额”里
    params['quantity'] = 1              # 商品的数量
    params['seller_email'] = ALIPAY_SELLER_EMAIL
    params['body'] = body      # 订单描述、订单详细、订单备注，显示在支付宝收银台里的“商品描述”里
    params['show_url'] = ALIPAY_SHOW_URL
    
    params,prestr = params_filter(params)
    
    params['sign'] = build_mysign(prestr, ALIPAY_KEY, ALIPAY_SIGN_TYPE)
    params['sign_type'] = ALIPAY_SIGN_TYPE
    
    return _GATEWAY + urlencode(params)

# 确认发货接口
def send_goods_confirm_by_platform (tn):
    params = {}

    # 基本参数
    params['service']       = 'send_goods_confirm_by_platform'
    params['partner']           = ALIPAY_PARTNER
    params['_input_charset']    = ALIPAY_INPUT_CHARSET

    # 业务参数
    params['trade_no']  = tn
    params['logistics_name'] = u'银河列车'   # 物流公司名称
    params['transport_type'] = u'POST'
    
    params,prestr = params_filter(params)
    
    params['sign'] = build_mysign(prestr, ALIPAY_KEY, ALIPAY_SIGN_TYPE)
    params['sign_type'] = ALIPAY_SIGN_TYPE
    
    return _GATEWAY + urlencode(params)

def notify_verify(post):
    # 初级验证--签名
    _,prestr = params_filter(post)
    mysign = build_mysign(prestr, ALIPAY_KEY, ALIPAY_SIGN_TYPE)
    if mysign != post['sign']:
        # print 'sing not match'
        # print mysign
        # print post['sign']
        return False
    
    # 二级验证--查询支付宝服务器此条信息是否有效
    params = {}
    params['partner'] = ALIPAY_PARTNER
    params['notify_id'] = post['notify_id']
    if ALIPAY_TRANSPORT == 'https':
        params['service'] = 'notify_verify'
        gateway = 'https://mapi.alipay.com/gateway.do'
    else:
        gateway = 'http://notify.alipay.com/trade/notify_query.do'
    veryfy_result = urlopen(gateway, urlencode(params)).read()
    if veryfy_result.lower().strip() == 'true':
        return True
    return False

