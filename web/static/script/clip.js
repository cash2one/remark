//互推要求
var req_con = [];
$('#req p').each(function(){
	req_con.push($(this).text());
});
var req = $('#req').data('user') + '，正在组织互推，要求如下：\n'
		+ '时间：' + $('#req dt').text() + '\n'
		+ req_con.join('\n') + '\n'
		+ '参与互推：' + $('#req').data('url');
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
	showAlert("Ctrl+C 或鼠标右键复制模板到剪贴板<br>然后Ctrl+V 粘贴到微信的图文消息编辑器中","success")
};
$('.writer-copy').click(function(){
	SelectText('copy-con')
});
