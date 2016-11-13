// JavaScript Document
// full height
var mainheight = $('.ui-full').height();
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
	obj.is(':visible') ? obj.fadeOut() : obj.fadeIn();
};
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
	var type = $.cookie("flash_type"),
		text = decodeURI($.cookie("flash_text"));
	if(type && text){
		showAlert(text,type);
		$.removeCookie("flash_type");
		$.removeCookie("flash_text");
	}
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
function checkForm(e, id, func){
	var id = typeof(id) == "string" ? id : undefined;
	var func = typeof(func) == "function" ? func : undefined;
	var alertbox = $(e).parents('.form').find('.form-alert');
	var isCheck = false;

	alertbox.html('');

	$(e).parents('.form').find('input.text').not($(e)).each(function(i,input){
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
$('.step-tit .btn-count, .push-colse').click(function(){
	var obj = $('.push');
	if(obj.is('.wroking')){
		return false;
	}else{
		obj.addClass('working');
	};
	if(!obj.is('.nano-ready')){
		$('.push-list').nanoScroller();
		obj.addClass('nano-ready');
	};
	obj.animate({right: obj.is('.stepshow') ? -642 : -321}, function(){
		$(this).toggleClass('stepshow');
		$(this).removeClass('working');
	});
});
// writer
var setVal = {
	tit: $('.step .writer .text-tit input').val(),
	con: $('.step .writer .text-con textarea').val()
};
$('.writer').find('.text-tit input, .text-con textarea').focus(function(){
	var v1 = $(this).is('input') ? setVal.tit : setVal.con;
	if($(this).val() == v1){
		$(this).val('')
	};
	$(this).css({'color':'#333', 'background':'#fff'});
}).blur(function(){
	var v1 = $(this).is('input') ? setVal.tit : setVal.con;
	if($(this).val() == ''){
		$(this).val(v1)
		$(this).css({'color':'#999'});
	};
	$(this).css({'background':'none'});
});
$('.step-tit .down dt').click(function(){
	$(this).siblings('dd').slideToggle();
})
$('.step-tit .down dd span').click(function(){
	$(this).addClass('now').siblings().removeClass('now');
	$(this).parent().slideUp().siblings('dt').find('b').html($(this).text());
	$('.type-con').hide().eq($(this).index()).fadeIn();
	$('.writer').nanoScroller();
})
//.step-list .avatar
// html: <div class="info-box"><div class="arrows"></div><div class="con clearfix">...</div></div>
$('.step-list .avatar').click(function(){
	var col = Math.floor($(this).parents('.step-list').width() / 120);
	var index = $(this).index('.step-list .avatar');
	var row = Math.floor(index / col);
	var target = (row + 1) * col - 1;
	var sl = (index % col) * 120 + 60;
	$('.step-list .info-box').remove();
	if($(this).is('.info-now')){
		$('.step-list .avatar').removeClass('info-now');
		return false;
	};
	if($(this).siblings('.info').size() && !$(this).is('.info-now')){
		var html = $(this).siblings('.info').html();
		$('.step-list .avatar').eq(target).parent().after('<div class="info-box"><div class="arrows" style="left:' + sl + 'px"></div><div class="con clearfix">' + html + '</div></div>');
		$('.step-list .avatar').removeClass('info-now');
		$(this).addClass('info-now');
	};
});

function setPad(){
	_col = Math.floor($('.step-list').width() / 120);
	$('.step-list .item').css('padding-left', '20px').filter(':nth-child(' + _col + 'n+1)').css('padding-left', '30px')
}
if($('.step-list .item').size()){
	var _col;
	setPad();
	$(window).resize(function(e) {
		if(_col != Math.floor($('.step-list').width() / 120)){
			setPad();
		};
    });
};
