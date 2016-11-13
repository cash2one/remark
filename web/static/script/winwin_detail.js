/**
 * Created by john on 2015/3/24.
 */
function set_style(){

    var syl = $('#sel_style li.now');
    console.log(syl.attr('data'));
    $.ajax({
        type: "GET",
        url: "/winwin/update_style/{% if winwin %}{{ winwin.uuid }}{% endif %}/" + syl.attr('data'),
        success: function(msg){
            console.log(msg);
        }
    });
}
function checkaddMember(oaid){
    $('#dlg_add').attr('oaid', oaid);
    lightbox('dlg_add');
}

//setp_add
function add_oa(){
    var oaid = $('#dlg_add').attr('oaid');

    $.ajax({
        type: "GET",
        url: "/winwin/join/{% if winwin %}{{ winwin.uuid }}{% endif %}/" + oaid,
        success: function(msg){
            if(msg == "ok"){
                location.reload();
            }else if(msg == 'exists'){
                alert('你已经申请加入了。');
            }
        }
    });
}

function addMember(){

    // step
    var obj = $('.addmemberbox');
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
}

function editWinwin(){
    var cform_date = $("#cform_date");
    var cform_content = $("#cform_content");
    var btn_winwin = $('#editWinWin');

    if( btn_winwin.text() == "编辑要求" ){
        cform_date.focus();
        cform_date.removeAttr("readonly");
        cform_content.removeAttr("readonly");
        btn_winwin.text("保存要求");

    }else if (btn_winwin.text() == "保存要求"){

        var cform_date = $("#cform_date").val();
        var cform_content = $("#cform_content").val();

        reg = /^(\d{4})\/(0\d{1}|1[0-2])\/(0\d{1}|[12]\d{1}|3[01])$/;
        errorText = "时间格式错误，请遵照格式：2014/09/01";

        if(!reg.test(cform_date)){
            alert("时间格式错误，请遵照格式：2014/09/01");
            return;
        }
        if(cform_content == ''){
            alert('说明不能为空');
            return;
        }

        var params = { type:'require', start_date:cform_date, description:cform_content };

        $.ajax({
            type: "POST",
            url: "/winwin/update/{% if winwin %}{{ winwin.uuid }}{% endif %}",
            data: $.param(params),
            success: function(msg){
                if(msg == "ok"){
                    $("#cform_date").attr("readonly","readonly");
                    $("#cform_content").attr("readonly","readonly");
                    btn_winwin.text("编辑要求");
                }
            }
        });
    }
}

function editContent(){

    var content_title = $("#content_title");
    var content_content = $("#content_content");
    var btn_edit_content = $('#btn_edit_content');

    if( btn_edit_content.text() == "编辑文案" ){
        content_title.removeAttr("readonly");
        content_content.removeAttr("readonly");
        btn_edit_content.text("保存文案");

        content_content.show();
        $('.mpintro').hide();

    }else if (btn_edit_content.text() == "保存文案"){
        var params = { type:"content", title:content_title.val(), content:content_content.val() };

        $.ajax({
            type: "POST",
            url: "/winwin/update/{% if winwin %}{{ winwin.uuid }}{% endif %}",
            data: $.param(params),  //mark
            success: function(msg){
                if(msg == "ok"){
                    $("#content_title").attr("readonly","readonly");
                    $("#content_content").attr("readonly","readonly");
                    btn_edit_content.text("编辑文案");
                    var c = $("#content_content");
                    c.hide();
                    $('.mpintro p').text(c.val());
                    $('.mpintro').show();
                }
            }
        });
    }
}

function checkDate(a, b){
    var arr = a.split("/");
    var starttime = new Date(arr[0], arr[1], arr[2]);
    var starttimes = starttime.getTime();

    var arrs = b.split("/");
    var lktime = new Date(arrs[0], arrs[1], arrs[2]);
    var lktimes = lktime.getTime();

    if (starttimes >= lktimes) {
        return true;
    }
    else
        return false;

}

Date.prototype.getMonth2 = function(){
    return this.getMonth() + 1;
};

Date.prototype.Format = function(formatStr)
{
    var str = formatStr;
    var Week = ['日','一','二','三','四','五','六'];

    str=str.replace(/yyyy|YYYY/,this.getFullYear());
    str=str.replace(/yy|YY/,(this.getYear() % 100)>9?(this.getYear() % 100).toString():'0' + (this.getYear() % 100));

    str=str.replace(/MM/,this.getMonth2()>9?this.getMonth2().toString():'0' + this.getMonth2());
    str=str.replace(/M/g,this.getMonth());

    str=str.replace(/w|W/g,Week[this.getDay()]);

    str=str.replace(/dd|DD/,this.getDate()>9?this.getDate().toString():'0' + this.getDate());
    str=str.replace(/d|D/g,this.getDate());

    str=str.replace(/hh|HH/,this.getHours()>9?this.getHours().toString():'0' + this.getHours());
    str=str.replace(/h|H/g,this.getHours());
    str=str.replace(/mm/,this.getMinutes()>9?this.getMinutes().toString():'0' + this.getMinutes());
    str=str.replace(/m/g,this.getMinutes());

    str=str.replace(/ss|SS/,this.getSeconds()>9?this.getSeconds().toString():'0' + this.getSeconds());
    str=str.replace(/s|S/g,this.getSeconds());

    return str;
};

function checkCreate(e){
    //lightbox('lb1');
    // this, lightbox-id
    var alertbox = $(e).next();

    var cform_date = $("#cform_date").val();
    var cform_content = $("#cform_content").val();

    reg = /^(\d{4})\/(0\d{1}|1[0-2])\/(0\d{1}|[12]\d{1}|3[01])$/;
    errorText = "时间格式错误，请遵照格式：2014/09/01";

    if(!reg.test(cform_date)){
        alertbox.html(errorText).fadeIn();
        return;
    }
    if(cform_content == ''){
        alertbox.html('说明不能为空').fadeIn();
        return;
    }

    var now = new Date(); //获取系统日期，即Sat Jul 29 08:24:48 UTC+0800 2006

    if(!checkDate(cform_date, now.Format('YYYY/MM/DD'))){
        alertbox.html('日期必须是今天以后哦！').fadeIn();
        return;
    }

    var params = { start_date:cform_date, description:cform_content };

    $.ajax({
        type: "POST",
        url: "/winwin/create",
        data: $.param(params),  //mark
        success: function(msg){

            rets = msg.split("|");
            if( rets[0] == 'ok' ){
                $('.left .btn-box').fadeOut();
                $('.step .left .btn-op').fadeIn();
                $('.left').animate({
                    left: '20px',
                    marginLeft: 0
                }, 400, function () {
                    $('.step .layoutSelect,.step .right,.step .mid').fadeIn();
                    $('.step').removeClass('stepstart');
                    location.href = '/winwin/' + rets[1];
                });
            }
        }
    });
}