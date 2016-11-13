// JavaScript Document
// full height
var mainheight = $('.ui-full').height();
function resetHeight(){
	var op = $('.op').size() ? $('.op').outerHeight() : 0;
	var h = Math.max(mainheight, $(window).height() - $('.head').height() - 20 - 2 - op);
	$('.ui-full').css('height', h);
	$('.step .push-list,.step .addmember-list,.step-list').css('height', h - 70);
	$('.step .left,.step .mid,.step .layoutSelect').css('height', h - 20);
	$('.step .right').css('height', h + 41);
	$('.step .writer').css('height', h - 69);
	$('.step .req .item textarea').css('height', h - 175);
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
function checkForm(e, id){
	// this, lightbox-id
	var alertbox = $(e).parents('.form').find('.form-alert');
	var isCheck = 1;
	$(e).parents('.form').find('input').each(function(){
		var type = $(this).data('check');
		var val = $(this).val();
		if(type){
			if(val == ''){
				$(this).focus();
				alertbox.html('不能为空').fadeIn();
				isCheck = 0;
				return false;
			};
			if(type == 'email'){
				var email_reg = /^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]+$/;
				if(!email_reg.test(val)){
					$(this).focus();
					alertbox.html('邮箱格式有误').fadeIn();
					isCheck = 0;
					return false;
				};
			};
		};
	});
	if(isCheck && id){
		lightbox(id);
	};
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
/*var setVal = {
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
});*/

//.step-list .avatar
// html: <div class="info-box"><div class="arrows"></div><div class="con clearfix">...</div></div>
/*$('.step-list .avatar').click(function(){
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
};*/