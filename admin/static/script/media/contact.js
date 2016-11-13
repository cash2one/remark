$(document).ready(function (){
	//获取全局ID 
    var $media_id = $("#media_id").attr("name");
    var $relation_type = $("#media_id").attr("relation-type");
    if ($relation_type != 3) {
        $relation_type = 1
    }
    var contact = {"contact_person":'联系人',"contact_position":'职位',"contact_phone":'手机',"contact_tel":'座机',"contact_wechat":'微信',"contact_qq":'QQ',"contact_email":'邮件',"contact_other":'其他',"operate":'操作'};
    //显示联系人表格
    $.ajax({
        url: '/media/common?a=get_contact&id=' + $media_id + '&relation_type=' + $relation_type,
        method: 'get',
        dataType: 'json',
        success: function(json){
            if(json.status == 200){
                var $html = '';
                var detail = json.data;                            
                $html += '<tr>'
                for(var i in contact) {
                     $html += '<td>' + contact[i] + '</td>'
                }
                $html += '</tr>'
                for(var j in detail){
                    var $div = '<div><button class="btn btnColor btn-info btn-xs contact_edit" name="' + detail[j].id + '">修改</button>&nbsp;<button class="btn btnColor btn-danger btn-xs btn-delete" name="' + detail[j].id +'">删除</button></div>'
                    $html += '<tr>'
                    for(var i in contact){
                        for(var k in detail[j]){
                            if(i == k){
                                if (detail[j][k]) {
                                        $html += '<td>' + detail[j][k] + '</td>'
                                    }else{
                                        $html += '<td>' + '-' + '</td>'
                                    }
                            }
                        }
                    }
                    $html += '<td>' + $div + '</td>'
                }
            }else if(json.status == 403){
                $("#contact-list").hide();
            }else if(json.status == 500){
                alert("联系人数据获取失败");
            }
            $("#contact-list").find('tbody').append($html);
            contact_edit($media_id);       //修改联系方式
            delete_contact($media_id,$relation_type);       //删除联系人
        }
	})

    // 添加联系方式
    $("#add_contact_btn").click(function(){
        add_contact($media_id,$relation_type);
    })

    //修改联系方式提交
    $("#media_contact_update").click(function(event) {
        var name_id = $("#contact_update_dialog").attr('name');
        update_contact_wechat(name_id,$media_id,$relation_type);
    });

})

// 修改联系人
function contact_edit($media_id){
    $(".contact_edit").click(function() {
        var contact_id = $(this).attr('name');
        $("#contact_update_dialog").attr('name', contact_id);
        $("#contact_update_dialog").modal();
        $.getJSON('/media/common?a=get_contact&id=' + $media_id,function(json) {
            for(var i in json.data){
                if( contact_id == json.data[i].id){
                    var person = json.data[i].contact_person,
                        position = json.data[i].contact_position,
                        phone = json.data[i].contact_phone,
                        tel = json.data[i].contact_tel,
                        wechat = json.data[i].contact_wechat,
                        qq = json.data[i].contact_qq,
                        email = json.data[i].contact_email,
                        other = json.data[i].contact_other
                    $("#contact_person").val(person);
                    $("#contact_position").val(position);
                    $("#contact_phone").val(phone);
                    $("#contact_tel").val(tel);
                    $("#contact_wechat").val(wechat);
                    $("#contact_qq").val(qq);
                    $("#contact_email").val(email);
                    $("#contact_other").val(other);
                }
            }
        });
    });
}

// 修改联系人提交
function update_contact_wechat(name_id,$id,$relation_type){
    var id = $id;
    var contact_id = name_id;
    var a = $('#contact_position').val();
    var b = $('#contact_person').val();
    var c = $('#contact_phone').val() ;
    var d = $('#contact_email').val();
    var e = $('#contact_tel').val();
    var f = $('#contact_qq').val();
    var w = $('#contact_wechat').val();
    if (c == "" &&  w== "" && f == "") {
        alert("手机、微信或QQ,请至少填写一项");
        return false;
    }
    if (b == "") {
        alert("输入不能为空");
        return false;
    }
    if (c && ! is_phone(c)){
        alert("请输入正确格式的手机号码");
        return false
    }
    if( d &&(! is_mail(d))){
        alert("请输入正确的email格式");
        return false
    }
    if( e &&(! is_tel(e))){
        alert("请输入正确的电话格式");
        return false
    }
    if( f &&(! is_qq(f))){
        alert("请输入正确的qq格式");
        return false
    }
    dicArgs = {
        'id':id,
        'contact_id':contact_id,
        'contact_person': b,
        'contact_position': a,
        'contact_phone': c,
        'contact_tel': e,
        'contact_wechat': $('#contact_wechat').val(),
        'contact_qq': f,
        'contact_email': d,
        'contact_other': $('#contact_other').val(),
        'relation_type': $relation_type
    };
    $.ajax({
        url: "/media/common?a=update_contact",
        method: "post",
        dataType:'json',
        data: dicArgs,
        success: function (result) {
            console.log(result)
            if (result.status == 200){
                // window.location.href="/media/wechat?a=detail&id=" + $media_id ;
                location.reload();
            }else if (result.status == 403) {
                alert("该用户无操作权限！");
                return false;
            }else {
                alert("更新失败请重新操作！");
                return false;
            }
        }
    });
}

// 添加联系人
function add_contact($media_id,$relation_type){
    var person = $("#add_contact_person").val(),
        position = $("#add_contact_position").val(),
        phone = $("#add_contact_phone").val(),
        tel = $("#add_contact_tel").val(),
        wechat = $("#add_contact_wechat").val(),
        qq = $("#add_contact_qq").val(),
        email = $("#add_contact_email").val(),
        other = $("#add_contact_other").val()
    if (phone == "" && wechat == "" && qq == "") {
        alert("手机、微信或QQ,请至少填写一项");
        return false;
    }
    if (person == "") {
        alert("联系人不能为空");
        return false;
    }
    if (phone && (!is_phone(phone)) ){
        alert("请输入正确格式的手机号码");
        return false
    }
    if( email &&(! is_mail(email)) ){
        alert("请输入正确的email格式");
        return false
    }
   
    if( qq &&(! is_qq(qq))){
        alert("请输入正确的qq格式");
        return false
    }
    var dicArgs = {
        'id': $media_id,
        'contact_person': person,
        'contact_position': position,
        'contact_phone': phone,
        'contact_tel': tel,
        'contact_wechat': wechat,
        'contact_qq': qq,
        'contact_email': email,
        'contact_other': other,
        'relation_type': $relation_type
    }

    $.ajax({
        url: "/media/common?a=add_contact",
        method: "post",
        dataType:'json',
        data: dicArgs,
        success: function (result) {
            var status = result.status
            switch (status) {
                case 200:
                    location.reload();
                    break;
                case 401:
                    alert("缺少必要联系方式，手机、微信、QQ至少填写一项");
                    break;
                case 403:
                    alert("用户无权限操作");
                    break;
                case 500:
                    alert("请求失败，请重新操作");
                    break;
                case 603:
                    alert('该联系人已存在，补充额外信息请使用“修改”');
                    location.reload();
                    break;
            }
        }
    })
}

// 删除联系人
function delete_contact($media_id,$relation_type){
    $(".btn-delete").click(function(event) {
        var $this = $(this);
        if(confirm("您确定要删除此联系人吗")){
            var $id = $(this).attr('name');
            var dicArgs = {
                'contact_id': $id,
                'relation_type': $relation_type,
                'relation_id':$media_id
            }
            
            $.ajax({
                url: '/media/common?a=del_contact',
                method: 'post',
                dataType: 'json',
                data: dicArgs,
                success: function(json){

                    if(json.status == 200){
                        $this.parent("div").parent("td").parent("tr").remove();
                    }
                }
            })
        }
    });
}  
