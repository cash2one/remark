/**
 * uDialog 对话框
 */
var uDialog = {
    'show': function(setOption){
        var _this = this;
        var option = {
            'title': '没事说两句',
            'content': '请通过setOption传入内容, 支持HTML',
            'button': false, // 数组，支持文本，单击事件回调
            'autoClose': false, // 自动关闭，整数，毫秒
            'showMask': true, // 是否显示蒙板
            'onload': false // 回调，加载完成后执行
        }
        // 合并参数
        if(setOption){
            for(var k in setOption){
                option[k] = setOption[k];
            }
        }
        // 蒙板
        if(option.showMask){
            _this.mask();
        }
        // 创建对话框
        var _html = '<div id="dialog">'+
            '<h2 class="dialog_title">'+ option.title +
                '<span id="dialog_close">x</span>'+
            '</h2>'+
            '<div id="dialog_content">'+ option.content +'</div>'+
        '</div>';
        $('body').append(_html);
        // 位置
        this.setPosition();
        // 按钮
        if(option.button){
            var _html = '<div id="dialog_control">';
            for(var k in option.button){
                _html += '<button class="dialog_button">'+ option['button'][k]['text'] +'</button>';
            }
            _html += '</div>';
            $('#dialog').append(_html);
            // 监听事件
            $('.dialog_button').click(function(){
                var k = $(this).index();
                option['button'][k]['click']($(this));
            });
        }
        // 自动关闭
        if(option.autoClose){
            setTimeout(function(){
                _this.close();
            }, option.autoClose);
        }
        // 加载完成回调
        if(option.onload){
            option['onload']($('#dialog_content'));
        }
        // 监听关闭
        this.listenClose();
    },
    // 蒙板
    'mask': function(){
        var _html = '<div id="mask"></div>';
        $('body').append(_html);
        $('body').css('overflow-y', 'hidden');
    },
    'close': function(){
        $('#mask').remove();
        $('#dialog').remove();
        $('body').css('overflow-y', '');
    },
    'listenClose': function(){
        var _this = this;
        $('#dialog_close').click(function(){
            _this.close();
        });
    },
    'setPosition': function(){
        var screenScroll = this.getScreenAndScroll();
        $('#dialog').css('top', screenScroll['scrollTop'] + 100);
        $('#mask').css('height', screenScroll['scrollHeight']);
    },
    'getScreenAndScroll': function(){
        var result = [];
        result['scrollTop'] = window.self.document.documentElement.scrollTop ? window.self.document.documentElement.scrollTop: window.self.document.body.scrollTop;
        result['scrollHeight'] = window.self.document.documentElement.scrollHeight ? window.self.document.documentElement.scrollHeight: window.self.document.body.scrollHeight;
        return result;
    }
}

/**
 * pop提示
 */
var uPop = {
    'show': function(obj, id, text, type){
        if($('#pop_' + id).length == 0){
            var opt = obj.offset();
            var width = obj.outerWidth();
            var height = obj.outerHeight();
            var left = opt.left + width;
            var top = opt.top;
            var type = type == undefined ? 'success': 'error';
            var _html = '<div class="pop '+ type +'" id="pop_'+ id +'">'+
                '<div class="pop_arr"></div>'+
                '<div class="pop_arr_inner"></div>'+
                '<div class="pop_inner">'+ text +'</div>'+
            '</div>';
            $('body').append(_html);
            $('#pop_' + id).css({
                'left': left + 10,
                'top': top
            });
        }else{
            $('#pop_' + id).show();
        }
    },
    'hide': function(id){
        $('#pop_' + id).fadeOut();
    },
    'clear': function(){
        $('.pop').fadeOut();
    }
}

/**
 * 按钮加载
 */
var loadingButton = {
    'show': function(obj){
        var text = obj.text();
        obj.attr('data-text', text);
        obj.attr('disabled', 'disabled').addClass('v3_disabled').text('正在'+ text +'中...');
    },
    'hide': function(obj){
        var text = obj.attr('data-text');
        obj.attr('disabled', false).removeClass('v3_disabled').text(text);
    }
}
