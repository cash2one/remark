$(function(){
    //获取全局ID 
    var $id = $("#ad_id").attr("ad-id");

    uediter('plan_brief');

    uediter('advertiser_brief');
    
    var companyInfo = {"company":'公司全称',"company_short":'公司简称',"brief":'公司介绍',"link":'官网信息',"category":'行业信息',"area":'地区信息',"advertiser_status":'广告主状态',"sub_status":'二级状态'};
    var contact = {"contact_person":'联系人',"contact_position":'职位',"contact_phone":'手机',"contact_tel":'座机',"contact_wechat":'微信',"contact_qq":'QQ',"contact_email":'邮件',"contact_other":'其他',"operate":'操作'};
    var advertiser = {"requirement":'需求',"progress":'广告主跟踪',"product_info":'产品分析',"audience_info":'受众分析',"remark":'备注'};
    var follower = {"follower":'负责人'}
    //根据权限获取相应表格信息
    $(".table-info").each(function(index, el) {
        var $this = $(this);
        switch (index) {
            // 基本信息
            case 0:
            ajaxUrl('basic',$this,companyInfo,$id,"基本信息");
            break;

            // 联系方式
            case 1:
            $.ajax({
                url: '/admin_user/advertiser_follow?a=get_contact&id=' + $id,
                method: 'get',
                dataType: 'json',
                // data: $id,
                beforeSend: function(){
                    $(".loading").show();
                },
                success: function(json){
                    if(json.status == 200){
                        var $html = '';
                        var detail = json.data.detail_info_value;                            
                        $html += '<tr>'
                        for(var i in contact) {
                             $html += '<td>' + contact[i] + '</td>'
                        }
                        $html += '</tr>'
                        for(var j in detail){
                            var $div = '<div><button class="btn btnColor btn-info btn-xs contact_revise" name="' + detail[j].id + '">修改</button>&nbsp;<button class="btn btnColor btn-danger btn-xs" name="' + detail[j].id +'">删除</button></div>'
                            $html += '<tr>'
                            for(var i in contact){
                                for(var k in detail[j]){
                                    if(i == k){
                                        if (detail[j][k]) {
                                            $html += '<td>' + detail[j][k] + '</td>'
                                        }else{
                                            $html += '<td>' + '无' + '</td>'
                                        }
                                    }
                                }
                            }
                            $html += '<td>' + $div + '</td>'
                        }
                    }else if(json.status == 403){
                        $($this).hide();
                    }else if(json.status == 500){
                        alert("联系人数据获取失败");
                    }
                    $this.find('tbody').append($html);
                    contact_revise($id);       //修改联系方式
                    delete_contact($id);       //删除联系人
                },
                complete: function(){
                    $(".loading").hide();
                }
            })
            break;
            
            // 公司信息
            case 2:
            ajaxUrl('text',$this,advertiser,$id,"公司信息");
            break;

            // 增加计划
            case 3:
            ajaxUrl('plan',$this,'',$id,"计划");
            break;
        }
    });
    // 修改广告主基本信息
    $("#advertiser_basic_revise").click(function(event) {
        advertiser_basic_revise($id);
    });

    // 修改广告主基本信息提交
    $("#on_advertiser_basic_commit").click(function(event) {
        on_advertiser_basic_commit($id);
    });

    // 添加联系方式
    $("#add_contact_btn").click(function(){
        add_contact($id);
    })

    //修改联系方式提交
    $("#update_contact").click(function(event) {
        var name_id = $("#advertiser_contact_revise").attr('name');
        update_contact_advertiser(name_id,$id);
    });

    // 修改广告主跟踪人
    $("#advertiser_follow_btn").click(function(event) { 
        $.getJSON("/admin_user/advertiser_follow?a=get_user&id=" + $id,function(json){
            if(json.status == 200){
                $("#advertiser_follower_revise").modal();
                $("#advertiser_follower_revise_form ul").empty();
                var $html = "";
                $(json.data).each(function(index, el) {
                    if (json.data[index].checked == 1) {
                        $html += '<li><input type="checkbox" name="follower"  value=' + json.data[index].id + ' checked />';
                    }
                    else {
                        $html += '<li><input type="checkbox" name="follower" value=' + json.data[index].id + '>';
                    }
                    if(json.data[index].nickname){
                        $html += '&nbsp' + json.data[index].nickname + '</li>'
                    }else{
                         $html += '&nbsp' + json.data[index].name + '</li>'
                    }
                });
            }else{
                alert("获取数据失败");
            }
            
            $("#advertiser_follower_revise_form ul").append($html);
        });
    });

    // 修改广告主跟踪人提交
    $("#updata_advertiser_follower").click(function(event) {
        updata_follower($id);
    });

    // 增加计划
    $("#add_plan").click(function(event) {
        on_plan_commit($id);
    });
});

//增加投放计划、提交
function on_plan_commit($id){
    var a = $('#plan_advertiser_id').val();
    var b = $('#plan_title').val();
    var c = $('#plan_money').val();
    var d = $('#plan_time_begin').val();
    var e = $('#plan_time_end').val();
    if (a == "" || b == "" || c == ""|| d == ""|| e == "") {
        alert("输入不能为空");
        return false;
    }
    if(d>=e){
        alert("结束时间需在起始时间之后");
        return false;
    }
    var dicArgs = {
        'plan_advertiser_id': a,
        'plan_title': b,
        'plan_money': c,
        'plan_time_begin': d,
        'plan_time_end': e,
        'plan_brief': $('#plan_brief').val()
    };
    $.ajax({
        url: "/project/plan?a=create",
        method: "post",
        dataType:'json',
        data: dicArgs,
        success: function (result) {
            //console.log("result = "+result);
            if (result.status ==200){
                window.location.href="/admin_user/advertiser_follow?a=detail&id=" + $id + "&type=look";
            }else if (result.status ==403) {
                alert("该用户无操作权限！");
                return false;
            }else if (result.status ==500) {
                alert("更新失败请重新操作！");
                return false;
            }
        }
    });    
}

function start_end_add_compare(){
    //a , b 格式為 yyyy-MM-dd
    var a=document.getElementById("plan_time_begin").value;
    var b=document.getElementById("plan_time_end").value;
    time_compare(a, b)
}

function display(level){
    var sub_status = document.getElementById("sub_status");
    // if (level=="4"){
    //     sub_status.options[0].text = '1 执行中';
    //     sub_status.options[1].text = '2 暂停调整';
    // }
    if (level=="4"){
        sub_status.options[0].text = '1 稳定客户';
        sub_status.options[1].text = '2 短期客户';
    }
}

function advertiser() {
    var status = "{{detail_info_value['advertiser_status'] }}";
    var sub_status = "{{detail_info_value['sub_status'] }}";
    $("#advertiser_status").val(status);
    if (status=="4"){
        document.getElementById("status").style.display="" ;
        display(status);
        $("#sub_status").val(sub_status);
    }else{
        document.getElementById("status").style.display="none" ;
    }
}

function process(obj){
    var level = parseInt(obj.value);
    if (level=="4"){
        document.getElementById("status").style.display="" ;
        display(level);
    }else{
        document.getElementById("status").style.display="none" ;
    }
}

function on_advertiser_basic_commit($id){
    var id = $id;
    var follower = [];
    $('input[name="follower"]:checked').each(function () {
        follower.push($(this).val());
    });
    dicArgs = {
        'advertiser_status': $('#advertiser_status').val(),
        'follower': follower.join(','),
        'id':id,
        'advertiser_company': $('#advertiser_company').val(),
        'advertiser_company_short': $('#advertiser_company_short').val(),
        'advertiser_brief': $('#advertiser_brief').val(),
        'advertiser_category': $('#advertiser_category').val(),
        'advertiser_area': $('#advertiser_area').val(),
        'sub_status': $('#sub_status').val(),
        'advertiser_link': $('#advertiser_link').val()
    };
    $.ajax({
        url: "/admin_user/advertiser_follow?a=update_basic",
        method: "post",
        dataType:'json',
        data: dicArgs,
        success: function (result) {
            //console.log("result = "+result);
            if (result.status ==200){
                window.location.href="/admin_user/advertiser_follow?a=detail&id="+ $id +"&type=look";
            }else if (result.status ==403) {
                alert("该用户无操作权限！");
                return false;
            }else if (result.status ==500) {
                alert("更新失败请重新操作！");
                return false;
            }
        }
    });
}

// 请求所有表格数据
function ajaxUrl(getUrl,_this,dataName,$id,infoName){
    $.ajax({
        url: '/admin_user/advertiser_follow?a=get_' + getUrl + '&id='+ $id,
        method: 'post',
        dataType: 'json',
        data: $id,
        beforeSend: function(){
            $(".loading").show();
        },
        success: function(json){
            if (json.status == 200) {
                var $html = '';
                for(var j in dataName){
                    for(var i in json.data.detail_info_value){
                        if(j == i){
                            if(json.data.detail_info_value[i]){
                                if (j == 'advertiser_status'){
                                    var as = json.data.detail_info_value.advertiser_status;
                                    switch (as) {
                                        case 1:
                                            $html += '<tr>';
                                            $html += '<td>' + dataName[i] + '</td>' + '<td>' + "销售线索" + '</td>';
                                            $html += '</tr>'
                                            break;
                                        case 2:
                                            $html += '<tr>';
                                            $html += '<td>' + dataName[i] + '</td>' + '<td>' + "接触中" + '</td>';
                                            $html += '</tr>'
                                            break;
                                        case 3:
                                            $html += '<tr>';
                                            $html += '<td>' + dataName[i] + '</td>' + '<td>' + "意向客户" + '</td>';
                                            $html += '</tr>'
                                            break;
                                        default:
                                            $html += '<tr>';
                                            $html += '<td>' + dataName[i] + '</td>' + '<td>' + "成交客户" + '</td>';
                                            $html += '</tr>'
                                            break;
                                    }
                                }else if(j == 'sub_status'){
                                    var ss = json.data.detail_info_value.sub_status;
                                    switch (ss) {
                                        case 1:
                                            $html += '<tr>';
                                            $html += '<td>' + dataName[i] + '</td>' + '<td>' + "稳定客户" + '</td>';
                                            $html += '</tr>'
                                            break;
                                        default:
                                            $html += '<tr>';
                                            $html += '<td>' + dataName[i] + '</td>' + '<td>' + "短期客户" + '</td>';
                                            $html += '</tr>'
                                            break;
                                    }
                                }else{
                                    $html += '<tr>';
                                    $html += '<td>' + dataName[i] + '</td>' + '<td>' + json.data.detail_info_value[i] + '</td>';
                                    $html += '</tr>' 
                                }
                            }else{
                                $html += '<tr>';
                                $html += '<td>' + dataName[i] + '</td>' + '<td>' + '无' + '</td>';
                                $html += '</tr>'
                            }
                        }
                    }
                }
            }else if(json.status == 403){
                $(_this).hide();
            }else if(json.status == 500){
                alert(infoName + "数据获取失败");
            }
            $(_this).find('tbody').append($html);
        },
        complete: function(){
            $(".loading").hide();
        }
    }) 
}

// 修改基本信息
function advertiser_basic_revise($id) {
    $.getJSON('/admin_user/advertiser_follow?a=get_basic&id='+ $id, function(json) {
        var value = json.data.detail_info_value
        var company = value.company,
            company_short = value.company_short,
            brief = value.brief,
            link = value.link,
            category = value.category,
            area = value.area,
            advertiser_status = value.advertiser_status,
            sub_status = value.sub_status;
        $("#advertiser_company").val(company);
        $("#advertiser_company_short").val(company_short);
        $("#advertiser_brief").html(brief);
        $("#advertiser_brief").siblings(".edui-body-container").html(brief);
        $("#advertiser_link").val(link);
        $("#advertiser_category").val(category);
        $("#advertiser_area").val(area);
        $("#advertiser_status option").each(function(index, el) {
            if($(el).val() == advertiser_status){
                $(this).attr("selected","selected");
            }
        });
        $("#sub_status option").each(function(index, el) {
            if($(el).val() == sub_status){
                $(this).attr("selected","selected");
            }
        });
        if (advertiser_status == "4"){
            $("#status").show();
        }else{
            $("#status").hide();
        }
    });
    process();
}

// 修改基本信息中一级状态
function process(){
    $("#advertiser_status").change(function(event) {
        var level = $(this).children("option:selected").val();
        if (level == 4){
            $("#status").show();
        }else{
            $("#status").hide();
        }
    });
}

// 修改基本信息提交
function on_advertiser_basic_commit($id){
    var id = $id;
    var follower = [];
    $('input[name="follower"]:checked').each(function () {
        follower.push($(this).val());
    });
    dicArgs = {
        'advertiser_status': $('#advertiser_status').val(),
        'follower': follower.join(','),
        'id':id,
        'advertiser_company': $('#advertiser_company').val(),
        'advertiser_company_short': $('#advertiser_company_short').val(),
        'advertiser_brief': $('#advertiser_brief').val(),
        'advertiser_category': $('#advertiser_category').val(),
        'advertiser_area': $('#advertiser_area').val(),
        'sub_status': $('#sub_status').val(),
        'advertiser_link': $('#advertiser_link').val()
    };
    $.ajax({
        url: "/admin_user/advertiser_follow?a=update_basic",
        method: "post",
        dataType:'json',
        data: dicArgs,
        success: function (result) {
            //console.log("result = "+result);
            if (result.status ==200){
                window.location.href="/admin_user/advertiser_follow?a=detail&id="+ $id +"&type=look";
            }else if (result.status ==403) {
                alert("该用户无操作权限！");
                return false;
            }else if (result.status ==500) {
                alert("更新失败请重新操作！");
                return false;
            }
        }
    });
}

// 添加联系方式
function add_contact($id){
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
        'id': $id,
        'advertiser_contact_person': person,
        'advertiser_contact_position': position,
        'advertiser_contact_phone': phone,
        'advertiser_contact_tel': tel,
        'advertiser_contact_wechat': wechat,
        'advertiser_contact_qq': qq,
        'advertiser_contact_email': email,
        'advertiser_contact_other': other
    }
    $.ajax({
        url: "/admin_user/advertiser_follow?a=add_contact",
        method: "get",
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
                    alert("联系人已存在");
                    location.reload();
                    break;
            }
        }
    })
}

// 修改联系方式
function contact_revise($id){
    $(".contact_revise").click(function() {
        var contact_id = $(this).attr('name');
        $("#advertiser_contact_revise").attr('name', contact_id);
        $("#advertiser_contact_revise").modal();
        $.getJSON('/admin_user/advertiser_follow?a=get_contact&id=' + $id,function(json) {
            for(var i in json.data.detail_info_value){
                if( contact_id == json.data.detail_info_value[i].id){
                    var person = json.data.detail_info_value[i].contact_person,
                        position = json.data.detail_info_value[i].contact_position,
                        phone = json.data.detail_info_value[i].contact_phone,
                        tel = json.data.detail_info_value[i].contact_tel,
                        wechat = json.data.detail_info_value[i].contact_wechat,
                        qq = json.data.detail_info_value[i].contact_qq,
                        email = json.data.detail_info_value[i].contact_email,
                        other = json.data.detail_info_value[i].contact_other
                    $("#advertiser_contact_person").val(person);
                    $("#advertiser_contact_position").val(position);
                    $("#advertiser_contact_phone").val(phone);
                    $("#advertiser_contact_tel").val(tel);
                    $("#advertiser_contact_wechat").val(wechat);
                    $("#advertiser_contact_qq").val(qq);
                    $("#advertiser_contact_email").val(email);
                    $("#advertiser_contact_other").val(other);
                }
            }
        });
    });
}

// 修改联系人提交
function update_contact_advertiser(name_id,$id){
    var id = $id;
    var contact_id = name_id;
    var a = $('#advertiser_contact_position').val();
    var b = $('#advertiser_contact_person').val();
    var c = $('#advertiser_contact_phone').val() ;
    var d = $('#advertiser_contact_email').val();
    var e = $('#advertiser_contact_tel').val();
    var f = $('#advertiser_contact_qq').val();
    var w = $('#advertiser_contact_wechat').val();
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
        'advertiser_contact_person': b,
        'advertiser_contact_position': a,
        'advertiser_contact_phone': c,
        'advertiser_contact_tel': e,
        'advertiser_contact_wechat': $('#advertiser_contact_wechat').val(),
        'advertiser_contact_qq': f,
        'advertiser_contact_email': d,
        'advertiser_contact_other': $('#advertiser_contact_other').val()
    };
    $.ajax({
        url: "/admin_user/advertiser_follow?a=update_contact",
        method: "post",
        dataType:'json',
        data: dicArgs,

        success: function (result) {
            if (result.status == 200){
                // window.location.href="/admin_user/advertiser_follow?a=detail&id=" + $id + "&type=look";
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

// 删除联系人
function delete_contact($id){
    $(".btn-danger").click(function(event) {
        var $this = $(this);
        if(confirm("您确定要删除此联系人吗")){
            var data = {"id": $(this).attr('name'), "relation_id":$id };
            $.ajax({
                url: '/admin_user/advertiser_follow?a=delete_contact',
                method: 'get',
                dataType: 'json',
                data: data,
                success: function(json){
                    if(json.status == 200){
                        $this.parent("div").parent("td").parent("tr").remove();
                    }
                }
            })
        }
    });
}  

// 修改广告主跟踪人提交
function updata_follower($id){
    var follower_id = [];
    $("#advertiser_follower_revise_form input:checked").each(function(index,el) {
        var $follower = $(el).val();
        follower_id[index] = $follower;
    });
    var dicArgs = {
        "id":$id,
        "follower":follower_id.join(',')
    };
    $.ajax({
        url: '/admin_user/advertiser_follow?a=update_follower',
        dataType: 'json',
        data: dicArgs,
        success: function(result){
            if (result.status == 200){
                window.location.href="/admin_user/advertiser_follow?a=detail&id=" + $id + "&type=look";
            }else if (result.status == 403) {
                alert("该用户无操作权限！");
                return false;
            }else {
                alert("更新失败请重新操作！");
                return false;
            }
        }
    })
}

// 添加计划起止时间判断
function start_end_add_compare(){
    //a , b 格式為 yyyy-MM-dd
    var a=document.getElementById("plan_time_begin").value;
    var b=document.getElementById("plan_time_end").value;
    time_compare(a, b)
}

//增加投放计划、提交
function on_plan_commit($id){
    var a = $('#plan_advertiser_id').val();
    var b = $('#plan_title').val();
    var c = $('#plan_money').val();
    var d = $('#plan_time_begin').val();
    var e = $('#plan_time_end').val();
    if (a == "" || b == "" || c == ""|| d == ""|| e == "") {
        alert("填写内容不能为空");
        return false;
    }
    if(d>=e){
        alert("结束时间需在起始时间之后");
        return false;
    }
    var dicArgs = {
        'plan_advertiser_id': a,
        'plan_title': b,
        'plan_money': c,
        'plan_time_begin': d,
        'plan_time_end': e,
        'plan_brief': $('#plan_brief').val()
    };
    $.ajax({
        url: "/project/plan?a=create",
        method: "post",
        dataType:'json',
        data: dicArgs,
        success: function (result) {
            //console.log("result = "+result);
            if (result.status ==200){
                window.location.href="/admin_user/advertiser_follow?a=detail&id=" + $id + "&type=look";
            }else if (result.status ==403) {
                alert("该用户无操作权限！");
                return false;
            }else if (result.status ==500) {
                alert("更新失败请重新操作！");
                return false;
            }
        }
    });    
}
