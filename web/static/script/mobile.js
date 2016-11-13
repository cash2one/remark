/**
 * Created by john on 2015/4/17.
 */
var current_banner = 1;
var loadUrl = '/api/demand/demand_list';
var current_page_list = 1;
var current_page_selfmedia = 1;
var maxPage_list = 0;
var maxPage_selfmedia = 0;
var page_size = 10;
var page_type = 'list';
var isMobie = false;
var isTouch = false;
var isFirst = true;
var currentX = 0;
var currentY = 0;
var endX = 0;
var endY = 0;
var lock = false;

function changePage(str){
    if(!$('#' + str).hasClass('current-page')){
        $('.change-btn').removeClass('current-page');
        $('#' + str).addClass('current-page');
        if(str=="need"){
            if(page_type!='list') {
                page_type = 'list';
                loadUrl = '/api/demand/demand_list';
                //loadData();
                if(!isFirst){
                    $('#list').animate({'left':'0'},500).show();
                    $('#selfmedia').animate({'left':'1242px'},500,function(){$(this).hide()});
                }
            }
        }else{
            if(page_type!='selfmedia'){
                page_type = 'selfmedia';
                loadUrl = '/api/smedia/smedia_list';
                //loadData();
                if(!isFirst){
                    $('#list').animate({'left':'-1242px'},500,function(){$(this).hide()});
                    $('#selfmedia').animate({'left':'0'},500).show();
                }
            }
        }
    }
}

$(function(){
    isMobie = checkMobile();
    round_banner();
    loadData();
    addTouchEvent();
    $('.container').css('height',window.innerHeight-395).scroll(function(){
        var obj = page_type=='list'?$('#list-content'):$('#selfmedia-content');
        var obj1 = page_type=='list'?$('#list'):$('#selfmedia');
        if ((50 + obj1.scrollTop()) >= (obj.height() - $('.container').height())) {
            if(page_type=='list'){
                if(current_page_list<maxPage_list){
                    current_page_list++;
                    loadData();
                }
            }else{
                if(current_page_selfmedia<maxPage_selfmedia){
                    current_page_selfmedia++;
                    loadData();
                }
            }
        }
    });
    $('.back-color').click(function(){
        if(!lock){
            $('#tips').fadeOut();
        }
    });
    var href = location.href;
    if(href.indexOf('yidao.info')!=-1){
        var _hmt = _hmt || [];
        (function() {
            var hm = document.createElement("script");
            hm.src = "//hm.baidu.com/hm.js?90d759cbb892b43f47d5a4716264c0f7";
            var s = document.getElementsByTagName("script")[0];
            s.parentNode.insertBefore(hm, s);
        })();
    }
});

function showTips(){
    $('#tips').fadeIn(300,function(){
        unlock();
    });
    lock = true;
    $('.tips').unbind('click').bind('click',linkToHome);
}

function linkToHome(){
    if(!lock){
        document.cookie = 'yidao_from=mobile';
        window.location.href = '/';
    }
}
var movelock_left = false;
var movelock_top = false;
function addTouchEvent(){
    var evt0 = isMobie?'touchstart':'mousedown';
    var evt1 = isMobie?'touchmove':'mousemove';
    var evt2 = isMobie?'touchend':'mouseup';
    $(document)[0].addEventListener(evt0,function(e){
        isTouch = true;
        currentX = isMobie? e.touches[0].clientX: e.clientX;
        currentY=isMobie? e.touches[0].clientY: e.clientY;
        endX = currentX;
        endY  = currentY;
        movelock_left = false;
        movelock_top = false;
    },false);
    $(document)[0].addEventListener(evt1,function(e){
        if(isTouch){
            endX = isMobie? e.touches[0].clientX: e.clientX;
            endY = isMobie? e.touches[0].clientX: e.clientY;
            var tx = endX - currentX;
            var ty = endY - currentY;
            if(!movelock_left && !movelock_top){
                if(Math.abs(tx)>30)movelock_left = true;
                if(Math.abs(ty)>30)movelock_top = true;
                return;
            }
        }
    },false);
    $(document)[0].addEventListener(evt2,function(e){
        if(isTouch){
            isTouch = false;
            var tx = endX - currentX;
            if(tx>200 && movelock_left){
                changePage('need');
            }else if(tx<-200 && movelock_left){
                changePage('sm');
            }else if(tx>20 && movelock_left &&page_type=='selfmedia'){
                $('#list').animate({'left':'-1242px'},300,function(){$(this).hide()});
                $('#selfmedia').animate({'left':'0'},300);
            }else if(tx<-20 && movelock_left &&page_type=='list'){
                $('#list').animate({'left':'0'},500);
                $('#selfmedia').animate({'left':'1242px'},500,function(){$(this).hide()});
            }else{
                if(endY>200 && Math.abs(endY-currentY)<30){
                    if($('#tips').is(':hidden')){
                        showTips();
                    }
                }
            }
        }
    },false);
}

function unlock(){
    lock = false;
    console.log('unlock');
}

function loadData(){
    var current_page = page_type=='list'?current_page_list:current_page_selfmedia;
    $.ajax({
        url:loadUrl,
        dataType:'json',
        method:'get',
        data:{page:current_page,size:page_size,type:'all'},
        success:showList
    })
}

function showList(data){
    if(page_type=='list'){
        maxPage_list = data.max_page;
    }else{
        maxPage_selfmedia = data.max_page;
    }
    var list = data.list;
    var len = list.length;
    var main = page_type=='list'?$('#list .content'):$('#selfmedia .content');
    for(var i=0;i<len;i++){
        var f1 = $('<div></div>');
        f1.addClass('line-box');
        var f2 = $('<div></div>');
        f2.addClass('word-main');
        var str = list[i].title?list[i].title:list[i].name;
        str = str.length>10?str.substr(0,10)+'...':str;
        f2.append('<div class="detail-title">' + str + '</div>');
        if(page_type=='selfmedia'){
            f1.append('<img src="' + list[i].logo_url + '">');
            f2.append('<div class="date">' + list[i].wechat_id + '</div>');
        }else{
            f2.addClass('reset-left');
            f2.append('<div class="date">' + list[i].time_begin + '<small> 至 </small>' + list[i].time_end + '</div>');
            f2.append('<div class="costs"><small>¥ </small>' + formatNumber(list[i].money_parse) +'</div>');
        }
        var f3 = $('<div></div>');
        f3.addClass('interested-container');
        var list2 = list[i].category;
        var len2 = list2.length;
        for(var t=0;t<len2;t++){
            f3.append('<div class="interested-box">' + list2[t] + '</div>');
        }
        f2.append(f3);
        f1.append(f2);
        main.append(f1);
    }
    if(isFirst){
        if(page_type=="list"){
            changePage('sm');
            loadData();
        }else{
            changePage('need');
            isFirst = false;
        }
    }
}

function round_banner(){
    $('.foot img').hide();
    $('#p' + current_banner).show();
    setInterval(resetBanner,6000);
}

function resetBanner(){
    $('#p' + current_banner).fadeOut();
    current_banner = current_banner%3+1;
    $('#p' + current_banner).fadeIn();
}

function formatNumber(num){
    var ss = String(num);
    var str;
    if(ss.indexOf('.')==-1){
        str = ss;
        ss = '';
    }else{
        str = ss.split('.')[0];
        ss = ss.split('.')[1];
    }
    var list = [];
    var len = str.length;
    var times = 1;
    while(len>2){
        list.unshift(str.substr(-3*times++,3));
        len-=3;
    }
    if(len>0)list.unshift((str.substr(-3*times,len)));
    len = list.length;
    str = '';
    for(i=0;i<len;i++){
        str +=list[i];
        if(i!=len-1){
            str += ',';
        }
    }
    if(str=='')str = '0';
    return str+(ss==''?'':'.'+ss);
}

function checkMobile(){
    var mobileAgent = new Array("iphone", "ipod", "ipad", "android", "mobile", "blackberry", "webos", "incognito", "webmate", "bada", "nokia", "lg", "ucweb", "skyfire");
    var browser = navigator.userAgent.toLowerCase();
    var isMobile = false;
    for (var i=0; i<mobileAgent.length; i++){
        if (browser.indexOf(mobileAgent[i])!=-1){ isMobile = true;
        break; } }
    return isMobile;
}