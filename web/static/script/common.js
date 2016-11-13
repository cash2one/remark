// JavaScript Document
// full height
var mainheight = $('.ui-full').height();
var explorerType = 'ie';
var urlParams = {};
function resetHeight(){
	var op = $('.op').size() ? $('.op').outerHeight() : 0;
	var h = Math.max(mainheight, $(window).height() - $('.head').outerHeight(true) - 2 - op);
	$('.ui-full').css('height', h);
	$('.step-list, .step .push-list, .step .writer').css('height', h - 50);
};
resetHeight();
$(window).resize(function(e) {
	resetHeight();
});
// lightbox
function lightbox(id){
    var obj = $('#' + id);
    if(explorerType=='ie'){
        obj.is(':visible') ? obj.hide(): obj.show();
    }else{
        obj.is(':visible') ? obj.fadeOut() : obj.fadeIn();
    }
}

function getParams(){
    urlParams = {};
    var param = location.search;
    if(param.length>1){
        var list0 = param.replace('?','').split('&');
        for(var i=0;i<list0.length;i++){
            var list1 = list0[0].split('=');
            urlParams[list1[0]] = list1[1];
        }
    }
}

function checkHover(e,target){
    if (getEvent(e).type=="mouseover")  {
        return !contains(target,getEvent(e).relatedTarget||getEvent(e).fromElement) && !((getEvent(e).relatedTarget||getEvent(e).fromElement)===target);
    } else {
        return !contains(target,getEvent(e).relatedTarget||getEvent(e).toElement) && !((getEvent(e).relatedTarget||getEvent(e).toElement)===target);
    }
}function getEvent(e){
    return e||window.event;
}

function contains(parentNode, childNode) {
    if (parentNode.contains) {
        return parentNode != childNode && parentNode.contains(childNode);
    } else {
        return !!(parentNode.compareDocumentPosition(childNode) & 16);
    }
}

function checkToMobile(){
    var search = location.search;
    if(search.indexOf('cf=mobile')!=-1){
        return;
    }
    var mobileAgent = new Array("iphone", "ipod", "ipad", "android", "mobile", "blackberry", "webos", "incognito", "webmate", "bada", "nokia", "lg", "ucweb", "skyfire");
    var browser = navigator.userAgent.toLowerCase();
    var isMobile = false;
    for (var i=0; i<mobileAgent.length; i++){
        if (browser.indexOf(mobileAgent[i])!=-1){ isMobile = true;
            break; } }
    //return isMobile;
    if(isMobile){
        var cookies = document.cookie;
        var obj = {};
        var list0 = cookies.split(';');
        for(var i=0;i<list0.length;i++){
            var list1 = list0[i].split('=');
            obj[list1[0]] = list1[1];
        }
        if(obj.yidao_from!="mobile"){
            location.href = '/mobile';
        }
    }
}

function getExplorer() {
    var explorer = window.navigator.userAgent ;
//ie
    if (explorer.indexOf("MSIE") >= 0) {
        explorerType='ie';
    }
//firefox
    else if (explorer.indexOf("Firefox") >= 0) {
        explorerType = "Firefox";
    }
//Chrome
    else if(explorer.indexOf("Chrome") >= 0){
        explorerType = "Chrome";
    }
//Opera
    else if(explorer.indexOf("Opera") >= 0){
        explorerType = "Opera";
    }
//Safari
    else if(explorer.indexOf("Safari") >= 0){
        explorerType = "Safari";
    }
    else {
        explorerType='others';
    }
}
// scrollForm
function scrollForm(target){
	$('#scrollForm').animate({marginLeft: target == 'reg' ? -500 : 0});
};
$('.light-mid .item').click(function(){
	$(this).find('input').focus();
}).find('input').focus(function(){
	$(this).parents('.item').addClass('item-hover');
}).blur(function(){
	$(this).parents('.item').removeClass('item-hover');
});
$('.edit .form .text').focus(function(){
	$(this).addClass('text-hover');
}).blur(function(){
	$(this).removeClass('text-hover');
});
/**
 * 提示模态框
 * @param  {String} text 提示文案
 * @param  {String} type 模态框类型 normal|success|error
 * @return {[type]}      [description]
 */
function showAlert(text,type){
	var alertbox = "";
	alertbox += '<div class="top-alert top-alert-';
	alertbox += type;
	alertbox += '" id="mod-alert" style="display:none"><span class="icon-close"></span>';
	alertbox += text;
	alertbox += '</div>';
	$("#mod-alert").remove();
	$("body").append(alertbox);
	var alert = $("#mod-alert");
	alert.fadeIn();
	alert.find(".icon-close").on("click",function(){
		alert.fadeOut(400,function(){alert.remove()})
	})
}
function errorAlert(){
	/*var type = $.cookie("flash_type"),
		text = decodeURI($.cookie("flash_text"));
	if(type && text){
		showAlert(text,type);
		$.removeCookie("flash_type");
		$.removeCookie("flash_text");
	}*/
}
errorAlert();
/**
 * 正则校验
 * @param  {regExp} reg 正则表达式
 * @param  {string} val 匹配的值
 * @return {boolean}     匹配结果
 */
function checkReg(reg, val){
	return reg.test(val);
}
/**
 * 校验报错提示
 * @param  {DOM} ele       未通过校验的input
 * @param  {DOM} alertBox  报错文案的容器
 * @param  {string} errorText 报错文案
 */
function alertMsg(ele, alertBox, errorText){
	$(ele).focus();
	alertBox.html(errorText).fadeIn();
}
/**
 * 表单校验：内置常用类型的校验，并可通过DOM和自定义方法扩展。校验顺序是：内置校验==》扩展校验==》异步校验。三者可以并存
 * @param  {DOM} e    提交的表单元素
 * @param  {String} id   弹窗ID，如果全部校验通过，可弹窗提示
 * @param  {Function} func 扩展的校验方法 校验不通过返回文案信息 校验通过返回true
 * @return {Boolean}
 * =====================================
 DOM 扩展属性一揽
 data-type = "email|qq|date|telephone|userName|weixinName|weixinID" 等内置基本校验
 rel = "RegExp" 扩展正则校验
 errorText = "String" 扩展正则校验的报错文案
 extraCheck = "Boolean" 元素上是否应用扩展校验。扩展方法返回值：未通过校验返回报错文案，通过返回true
 necessary = "Boolean" 是否必需元素，默认为必须（值为false时要校验的元素值可以为空）
 synCheck = "String" 异步校验，所有异步校验目前统一请求接口
 */

function checkMovile(mobile){
    var reg = /^0?1[3|4|5|7|8][0-9]\d{8}$/;
    return reg.test(mobile);
}

function checkEmail(mail){
    var reg = /^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]+$/;
    return reg.test(mail);
}

function checkForm(e, id, func){
	var id = typeof(id) == "string" ? id : undefined;
	var func = typeof(func) == "function" ? func : undefined;
	var alertbox = $(e).parents('.form').find('.form-alert');
	var isCheck = false;

	alertbox.html('');

	$(e).parents('.iform').find('input').not($(e)).each(function(i,input){
		isCheck = false;

		var input = $(input),
			val = input.val(),
			type = input.data('check'),
			reg = new RegExp(input.attr('reg')),
			errorText = input.attr('errorText'),
			synCheck = input.attr('synCheck'),
			extraCheck = input.attr('extraCheck') || false,
			necessary = input.attr('necessary') || true;
		// 元素必须且为空，报错
		if(necessary === true && val === ''){
			alertMsg(input,alertbox,"不能为空")
			return false;
		}else if(val !== ''){
			// 不为空则类型校验
			switch(type){
				case "email":
					reg = /^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]+$/;
					errorText = "邮箱格式有误";
					break;
				case "qq":
					reg = /^\d{5,16}$/;
					errorText = "QQ格式有误";
					break;
				case "password":
					reg = /^.{6,}$/;
					errorText = "密码不足6位，请重新设定";
					break;
				case "userName":
					reg = /^.{1,16}$/;
					errorText = "姓名最多16个字符";
					break;
				case "weixinName":
					reg = /^.{2,32}$/;
					errorText = "请填写正确的微信名称";
					break;
				case "weixinID":
					reg = /^.{6,20}$/;
					errorText = "请填写正确的微信号";
					break;
				case "telephone":
					reg = /^1[3|4|5|8][0-9]\d{8}$/;
					errorText = "手机号码格式有误";
					break;
				case "date":
					reg = /^(\d{4})\/(0\d{1}|1[0-2])\/(0\d{1}|[12]\d{1}|3[01])$/;
					errorText = "时间格式错误，请遵照格式：2014/09/01";
					break;
				case "numLenMax8":
					reg = /^[1-9][0-9]{0,7}$/;
					errorText = "请填写8位以下非零正整数";
					break;
				case "numLenMax10":
					reg = /^[1-9][0-9]{0,7}$/;
					errorText = "请填写10位以下非零正整数";
					break;
				case "disable": //不校验
				case "text":
					isCheck = true;
					break;
				default: break;
			}

			isCheck = reg.source ? checkReg(reg,val) : isCheck;
			if(!isCheck){
                //console.log(errorText);
				alertMsg(input,alertbox,errorText);
				return false;
			}

			// 扩展方法
			if(extraCheck && func){
				var funcCheck = func(input);
				if(funcCheck !== true){
					isCheck = false;
					alertMsg(input,alertbox,funcCheck);
					return false;
				}
			}

			if(synCheck){
                //console.log('post');
				$.ajax({
			        url: '/verify/check',
			        type: 'POST',
			        data: {"value": val,"name": synCheck},
			        async: false,
			        success: function(data){
			            $(e).val($(e).data("val"));
			            data = JSON.parse(data);
			            if(!data[synCheck].check){
			            	isCheck = false;
			                errorText = data[synCheck].errorText;
			            }else{
			            	isCheck = true;
			            }
			        },
			        error: function(){
			        	isCheck = false;
			        	errorText = "服务器异常请稍后再试";
			        },
			        beforeSend: function(){
			        	$(e).data("val",$(e).val()).val("请求中...");
			        }
			    });
			}

			if(!isCheck){
				alertMsg(input,alertbox,errorText)
				return false;
			}
		}else{
			isCheck = true;
		}
	});

	// 全部通过弹窗提示成功
	if(isCheck && id){
		lightbox(id);
	}
	return isCheck;
};
$('input[data-check]').keypress(function(){
	$('.form-alert').fadeOut();
});
function setCheckbox(e){
	$(e).siblings('.icon-checked').toggleClass('checked')
};
function pushCheck(){
	$('.push-small span').toggleClass('checked')
}
// nav
var navTimer = {};
$('.nav .btn, .nav-box .close').click(function(){
	clearTimeout(navTimer);
	$('.nav-box').animate({left: $(this).is('.close') ? -200 : 0});
});
$('.nav-box').mouseleave(function(){
	navTimer = setTimeout(function(){
		$('.nav-box').animate({left: -200});
	}, 1000);
});

// top-alert
$('.top-alert span').click(function(){
	$(this).parents('.top-alert').fadeOut();
});

// step


$('.step-tit .btn-count, .push-close').click(function(){
	var obj = $('.push');
	if(obj.is('.working')){
		return false;
	}else{
		obj.addClass('working');
	};
	if(!obj.is('.nano-ready')){
		$('.push-list').nanoScroller();
		obj.addClass('nano-ready');
	};
	obj.animate({width: obj.is('.stepshow') ? 0 : 280}, function(){
		$(this).toggleClass('stepshow');
		$(this).removeClass('working');
	});
});

// writer
var setVal = {
	tit: $('.step .writer .text-tit input').val(),
	con: $('.step .writer .text-con textarea').val()
};
/*$('.writer').find('.text-tit input, .text-con textarea').focus(function(){
	var v1 = $(this).is('input') ? setVal.tit : setVal.con;
	if($(this).val() == v1){
		$(this).val('')
	};
	//$(this).css({'color':'#333', 'background':'#fff'});
}).blur(function(){
	var v1 = $(this).is('input') ? setVal.tit : setVal.con;
	if($(this).val() == ''){
		$(this).val(v1)
		$(this).css({'color':'#999'});
	};
	//$(this).css({'background':'none'});
});*/
$('.step-tit .down dt').click(function(){
	$(this).siblings('dd').slideToggle();
})
$('.step-tit .down dd span').click(function(){
	$(this).addClass('now').siblings().removeClass('now');
	$(this).parent().slideUp().siblings('dt').find('b').html($(this).text());
	$('.type-con').hide().eq($(this).index()).fadeIn();
	$('.writer').nanoScroller();
})



/**
 *  状态提示信
 */
var dicStatusMsg = {
    'signup':{
        200: '注册成功',
        601: '验证码错误',
        602: '该帐号已存在, 请换一个试试',
        603: '密码有错误',
    },
	'bind_phone':{
        200: '绑定成功',
        601: '验证码错误',
        603: '密码有错误',
    },
    'login': {
        200: '登录成功',
        401: '参数错误',
        601: '帐号不存在',
        603: '密码错误',
    },
    'reg': {
        200: '注册成功',
        602: '该帐号已存在, 请换一个试试',
        603: '密码有错误',
    },
    'weixin_bind': {
        200: '注册成功',
        401: '帐号或密码不能为空',
        501: '请求类型错误',
        602: '帐号或密码错误',
        500: '注册失败，请重试'
    },
    'media_create': {
        200: '添加成功',
        500: '验证失败，请检查目录内容页是否有正确的验证码',
        602: '该自媒体已存在',
        603: '添加失败，验证未通过，请检查验证码和链接地址是否正确',
    },
    'media_edit': {
        200: '保存成功',
        500: '保存失败，请刷新重试',
        401: '参数不正确，请填写完整',
        601: '数据不存在'
    },
	'media_price_update': {
		200: '修改成功',
		500: '修改失败，请刷新重试',
		401: '修改失败，参数错误，请刷新重试'
	},
    'anli_create': {
        200: '添加成功',
        401: '参数错误，请刷新重试',
        601: '数据有误，请刷新重试',
        605: '案例地址或内容有误，请检查',
        500: '系统错误，请刷新重试'
    },
    200: '成功',

    401: '参数错误',
    402: '类型错误',

    500: '系统错误',
    501: '请求类型错误',

    600: '未登录',
    601: '未找到用户',
    602: '用户已存在',
    603: '密码错误',

    701: '没有对应权限'
}



