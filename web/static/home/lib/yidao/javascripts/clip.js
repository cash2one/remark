//互推要求
var req_con = [];
$('.addmember-list .copytext').each(function(){
	req_con.push($(this).text());
});
var req = req_con.join() + '\n' + $('#req').data('url');
$('#req-copy').zclip({
	path: '/static/javascripts/ZeroClipboard.swf',
	copy: req
});

//文案样式
function SelectText(id) {
	var obj = document.getElementById(id);
	if($.support.changeBubbles){
		// 现代浏览器
		var selection = window.getSelection();
		selection.selectAllChildren(obj);
	}else{
		// ie8及以下
        var range = document.body.createTextRange();
        range.moveToElementText(obj);
        range.select();
	};
	$('#copy-alert').fadeIn();
};
$('#writer-copy').click(function(){
	SelectText('copy-con');
});
$('#writer-copy2').click(function(){
	SelectText('copy-con');
});