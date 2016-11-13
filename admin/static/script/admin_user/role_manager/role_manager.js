$(document).ready(function(){
    $.ajax({
        type:"get",
        dataType:"json",
        url:"/admin_user/role_manage?a=getRole",
        success:function(result) {
            //var obj = JSON.parse(result);
            var $show_authority_array = Array();
            var $authority_num = result.data.userRole.length;

            for (i=0;i<$authority_num;i++)
            {
                var $label = result.data.userRole[i].role_label;
                var $id = result.data.userRole[i].id;
                
                $show_authority_array[i] = result.data.userRole[i].permission;

                $show_authority_table = '<div class="authority_role role_manager_list" id="'+$id+'" label="'+$label+'">'
                + $label;
                
                $("#show_list").append($show_authority_table);

                var $role_id= $(".role_id").attr("id");
            }

            //点击传相对应数组给方法
            $(".authority_role").click(function(){
                $(this).addClass("role_click").siblings().removeClass('role_click');
                var $authority_role_id = $(this).attr("id");
                var $label = $(this).attr("label");
                for (n=0;n<$authority_num;n++) {
                    var $find_id=result.data.userRole[n].id;
                    if ($authority_role_id==$find_id) {
                        var $authority_content = $show_authority_array[n];
                        show_authority_function($authority_content,$authority_role_id,$label);
                        break;
                    }
                }
            //编辑按钮
                $change_authority = '<a class="btn btn-primary change_authority_button">编辑权限</a>'
            
                $(".change_authority").append($change_authority);


                //获取编辑信息
                $(".change_authority_button").click(function(){
                    var $role_id = $(".role_manager_head").attr("role_id");

                    var $label = $(".role_manager_head").attr("role_label");

                    authority_detail($role_id,$label);
                });
            })
        }
    })

    //模块
    $.ajax({
        type: "get",
        contentType: "application/json",
        url: "/admin_user/role_manage?a=getModule",
        //data: "{}",
        success: function (result) {
            var obj = JSON.parse(result);
            var module_tab = "";
            var strID = "module_";
            var tab = '&#12288&#12288';
            $("#role_module_id").empty();
            for (var i = 0; i < obj.data.length; i++) {
                if (obj.data[i].access_level == 1){
                    module_tab += '<div><span>';
                    module_tab += '<input type="checkbox" name="role_module_id" father_id='+strID+ obj.data[i].parent_id+' id='+strID+ obj.data[i].access_id +'  value=' + obj.data[i].id + ' onclick="oncheck(this)" /> ';
                    module_tab += obj.data[i].label;
                    module_tab += '</span></div>';
                    if (obj.data[i].is_exsit_child == 1) {
                        module_tab += '<div><span>';
                        module_tab += show (obj, obj.data[i].access_id, strID, 0, tab);
                        module_tab += '</span></div>';
                    }
                }
            }
            $("#role_module_id").append(module_tab);
        }
    });

    $("a[name='update_btn']").click(function(){
        var str_id = this.id;
        var id = str_id.split("_").pop();
        //模块
        $.ajax({
            type: "get",
            contentType: "application/json",
            url: "/admin_user/role_manage?a=getModule&id="+id,
            //data: "{}",
            success: function (result) {
                var module_cb = "";
                var strID = "role_module_";
                var tab = '&#12288&#12288';
                // 放置重复
                $("#role_module_id"+id).empty();
                for (var i = 0; i < obj.data.length; i++) {
                    if (obj.data[i].access_level == 1){
                        module_cb += '<div>';
                        if (obj.data[i].checked == 1){
                            module_cb += '<input type="checkbox" name="role_module_id" father_id='+strID+ obj.data[i].parent_id+' id='+strID+ obj.data[i].access_id +'  value=' + obj.data[i].id + ' onclick="oncheck(this)" checked /> ';
                        }
                        else {
                            module_cb += '<input type="checkbox" name="role_module_id" father_id='+strID+ obj.data[i].parent_id+' id='+strID+ obj.data[i].access_id +'  value=' + obj.data[i].id + ' onclick="oncheck(this)" > ';
                        }
                        module_cb += obj.data[i].label;
                        module_cb += '<button name="access_group" onclick="access(this)" id='+obj.data[i].access_id+' > +</button>';
                        if (obj.data[i].is_exsit_child == 0){
                            module_cb += '<div id=access'+obj.data[i].access_id+' style="display: none;">';
                            module_cb += tab;
                            module_cb += '<input type="checkbox" name="role_access_id">';module_cb += "读";module_cb += tab;
                            module_cb += '<input type="checkbox" name="role_access_id">';module_cb += "写";module_cb += tab;
                            module_cb += '<input type="checkbox" name="role_access_id">';module_cb += "增";module_cb += tab;
                            module_cb += '<input type="checkbox" name="role_access_id">';module_cb += "删";
                            module_cb += '</div>';
                        }
                        module_cb += '</div>';

                        if (obj.data[i].is_exsit_child == 1) {
                            module_cb += '<div>';
                            module_cb += show(obj, obj.data[i].access_id, strID, 1, tab);
                            module_cb += '</div>';
                        }
                    }
                }
                $("#role_module_id"+id).append(module_cb);
            }
        });
    });
});

//显示权限列表
function show_authority_function($authority_content,$authority_role_id,$label){
    $("#authority_content").empty();
    $(".change_authority").empty();
    $("#edit_authority").empty();
    $(".save_authority").empty();

    var content = '' ;

    $.each($authority_content,function(index,value){
        var $authority_label = value[0];
        var $authority_level = value[1];
        var $authority_id = value[2];
        var $authority_father_id = value[3];

        if($authority_level==1) {
            content += '<div class="first_level" id="'+$authority_id+'">'+$authority_label+'</div>';
        }
    })

    $(".role_manager_head").attr("role_id",$authority_role_id);

    $(".role_manager_head").attr("role_label",$label)

    $("#authority_content").append(content);

    show_second_authority_function($authority_content);
};

//显示二级权限列表
function show_second_authority_function($authority_content){
    var authority_content=$authority_content;

    for (var i = authority_content.length - 1; i >= 0; i--) {
        $authority_label = authority_content[i][0];
        $authority_level = authority_content[i][1];
        $authority_id = authority_content[i][2];
        $authority_father_id = authority_content[i][3];

        if($authority_level==2) {
            var first_level = $(".first_level");
                for (var r = first_level.length - 1; r >= 0; r--) {
                    if(first_level[r].id==$authority_father_id) {
                        $(first_level[r]).after('<ul class="second_level" id="'+$authority_id+'"><li>'+$authority_label+'</li></ul>');
                    }
                }
        } else {continue;}
    }
    show_third_authority_function($authority_content);    
}

function show_third_authority_function($authority_content){
    var authority_content=$authority_content;
    for (var i = authority_content.length - 1; i >= 0; i--) {
        $authority_label = authority_content[i][0];
        $authority_level = authority_content[i][1];
        $authority_id = authority_content[i][2];
        $authority_father_id = authority_content[i][3];

        if($authority_level==3) {
            var second_level = $(".second_level");
                for (var r = second_level.length - 1; r >= 0; r--) {
                    if(second_level[r].id==$authority_father_id) {
                        $(second_level[r]).after('<ul class="third_level" id="'+$authority_id+'"><li>'+$authority_label+'</li></ul>');
                    }
                }
        } else {continue;}
    } 
    show_fourth_authority_function($authority_content);
}

function show_fourth_authority_function($authority_content){
    var authority_content=$authority_content;
    for (var i = authority_content.length - 1; i >= 0; i--) {
        $authority_label = authority_content[i][0];
        $authority_level = authority_content[i][1];
        $authority_id = authority_content[i][2];
        $authority_father_id = authority_content[i][3];

        if($authority_level==4) {
            var third_level = $(".third_level");
                for (var r = third_level.length - 1; r >= 0; r--) {
                    if(third_level[r].id==$authority_father_id) {
                        $(third_level[r]).after('<ul class="fourth_level" id="'+$authority_id+'" style="padding-left:80px"><li>'+$authority_label+'</li></ul>');
                    }
                }
        } else {continue;}
    } 
}
    
function on_create_admin_role(){
    var label = document.getElementById('role_label').value;
    var name = document.getElementById('role_name').value;
    var reg = /^(\w|[\u4E00-\u9FA5])*$/;
    var rename = /^(\w|\d)*$/;
    var cks = document.getElementsByName('role_module_id');
    var uck = true;
    if (label.length < 2 || label.length > 10 || reg.test(label) == false) {
        alert("请输入正确格式的角色名称！\n由2-10位的中文、英文、数字组成！");
        return false;
    }
    if (name.length < 2 || name.length > 10 || rename.test(name) == false) {
        alert("请输入正确格式的标识！由2-10位的英文、数字组成！");
        return false;
    }
    for (var i=0;i<cks.length;i++) {
        if (cks[i].checked) {
            uck = false;
            break;
        }
    }
    if (uck) {
        alert("至少选择一项权限！");
        return false;
    }
    var role_module_id =[];
    $("input[name='role_module_id']:checked").each(function(){
        role_module_id.push($(this).val());
    })
    dicArgs = {
        'role_label': label,
        'role_name': name,
        'role_module_id': JSON.stringify(role_module_id)
    };
    $.ajax({
        url: "/admin_user/role_manage?a=create",
        method: "post",
        dataType:'json',
        data: dicArgs,
        success: function (result) {
            if (result.status ==200){
                window.location.href="/admin_user/role_manage";
            }else if (result.status ==401) {
                alert("信息已经存在！ 请重新输入！");
                return false;
            }else{
                alert("添加角色失败请重新操作！");
                return false;
            }
        }
    });
}

//请求编辑ajax
function authority_detail($role_id,$label){
    $.ajax({
        type:"get",
        dataType:"json",
        url: "/admin_user/role_manage?a=getModule&id="+$role_id,
        //data: "{}",
        success: function (result) {
            $("#authority_content").empty();
            $(".change_authority").empty();
            var module_tab = "";
            var strID = "module_";
            var tab = '&#12288&#12288&#12288';
            $("#edit_authority").empty();
            for (var i = 0; i < result.data.length; i++) {
                if (result.data[i].access_level == 1){
                    module_tab += '<div class="power"><span>';
                    if (result.data[i].checked == 1){
                        module_tab += '<input class="role_checkbox" type="checkbox" name="role_module_id" father_id='+strID+ result.data[i].parent_id+' id='+strID+ result.data[i].access_id +'  value=' + result.data[i].id + ' checked /> ';
                    }
                    else {
                        module_tab += '<input class="role_checkbox" type="checkbox" name="role_module_id" father_id='+strID+ result.data[i].parent_id+' id='+strID+ result.data[i].access_id +'  value=' + result.data[i].id + ' /> ';
                    }
                    module_tab += result.data[i].label;
                    module_tab += '&nbsp&nbsp<a class="morePower" name="access_group" onclick="access(this)" id='+result.data[i].id+' >+</a>';
                    module_tab += '</span></div>';
                    if (result.data[i].is_exsit_child == 1 || (result.data[i].is_exsit_child == 0&&result.data[i].tag == 0)) {
                        module_tab += '<div class="powerBox" id=access'+result.data[i].id+' style="display: none;"><span>';
                        module_tab += show_detail(result, result.data[i].access_id, strID, tab);
                        module_tab += '</span></div>';
                    }
                }
            }
            $("#edit_authority").append(module_tab);

            var change_label = '<input type="text" id="role_label_edit" name="role_label" class="form-control label_input" value='+$label+'>';
            $(".save_authority").append(change_label);

            var save_button = '<button class="btn btn-success" name="follow_btn" onclick="on_update_admin_role('+$role_id+')">保存</button>'
            $(".save_authority").append(save_button);

            $(".role_checkbox").click(function(event) {
                var father_id = $(this).attr("father_id");
                var access_id = $(this).attr("id");
                display_child(father_id, access_id);
            });

        }
    });
}

function show_detail(result, parent_id, strID, tab){
        module_cb = "";
        index = 0;
        for (var i = 0; i < result.data.length; i++) {
            if (result.data[i].access_level >1 && result.data[i].parent_id ==parent_id){
                module_cb += '<div class="powerLi"><span>';
                module_cb +=tab;
                if (result.data[i].checked == 1){
                    module_cb += '<input class="role_checkbox" type="checkbox" name="role_module_id" father_id='+strID+ result.data[i].parent_id+' id='+strID+ result.data[i].access_id + ' value='+ result.data[i].id + ' checked /> ';
                }
                else {
                    module_cb += '<input class="role_checkbox" type="checkbox" name="role_module_id" father_id='+strID+ result.data[i].parent_id+' id='+strID+ result.data[i].access_id + ' value='+ result.data[i].id + ' /> ';
                }
                module_cb += result.data[i].label;
                if ((result.data[i].is_exsit_child == 1 && result.data[i].parent_id ==parent_id) || (result.data[i].is_exsit_child == 0&&result.data[i].tag == 0)) {
                    module_cb += '&nbsp&nbsp<a name="access_group" class="morePower" onclick="access(this)" id='+result.data[i].id+' >+</a>';
                    module_cb += '<div id=access'+result.data[i].id+' style="display: none;"><span>';
                    module_cb += show_detail(result, result.data[i].access_id, strID, tab+tab);
                    module_cb += '</span></div>';
                }
                module_cb += '</span></div>';
            }
        }
        return module_cb;
    }

//提交修改权限
function on_update_admin_role($role_id){
    console.log($role_id);
        var label = document.getElementById('role_label_edit').value;
        var reg = /^(\w|[\u4E00-\u9FA5])*$/;
        var cks = document.getElementsByName('role_module_id');
        var uck = true;
        if (label.length < 2 || label.length > 10 || reg.test(label) == false) {
            alert("请输入正确格式的身份名称！\n由2-10位的中文、英文、数字组成！");
            return false;
        }
        for (var i=0;i<cks.length;i++) {
            if (cks[i].checked) {
                uck = false;
                break;
            }
        }
        if (uck) {
            alert("至少选择一项权限！");
            return false;
        }
        var module_value = [];
        $('input[name="role_module_id"]:checked').each(function () {
            module_value.push($(this).val());
        });
        var access_value = [];
        $('input[name="role_access_id"]:checked').each(function () {
            access_value.push($(this).val());
        });

        $.ajax({
            type: "post",
            dataType: "json",
            url: "/admin_user/role_manage?a=update",
            data: {'role_id':$role_id, 'role_label':label, 'role_module_id': module_value.join(','), 'role_access_id': access_value.join(',')},
            success: function (d) {
                if (d.status == 200) {
                     window.location.href = "/admin_user/role_manage";
                } else {
                    alert('加入跟踪失败。。。');
                    return false;
                }
            }
        });
    }
function access(result){
    var id = result.id;
    $("#access"+id).toggle();
}

var $searth_value = $("#search_condition_value").attr("value");
$(".search_button").click(function() {
    alert("qq");
});

// 给相应父类和子类打钩
function display_child(father_id, access_id){
    var checked = true;
    var access_id_value = "#"+access_id;
    var father_id_value = "#"+father_id;

    $("#edit_authority").find(access_id_value).change(function(){
        if($(this).is(':checked')){
            $("#edit_authority").find("input[father_id="+access_id+"]").prop("checked",true);
            $("#edit_authority").find(father_id_value).prop("checked",true);

            //给父类的父类打钩
            var father_father_id = $("#edit_authority").find(father_id_value).attr("father_id");
            $("#edit_authority").find("#"+father_father_id).prop("checked",true);

            //给子类的子类打钩
            var child_id = $("#edit_authority").find("input[father_id="+access_id+"]").attr("id");
            $("#edit_authority").find("input[father_id="+child_id+"]").prop("checked",true);

        }else{
            $("#edit_authority").find("input[father_id="+access_id+"]").removeAttr("checked",true);

            //给父类的父类去钩
            var father_father_id = $("#edit_authority").find(father_id_value).attr("father_id");

            $("#edit_authority").find("input[father_id="+father_father_id+"]").each(function(){
            if (true == $(this).is(':checked')) {
                 checked = false;
            }});
            if (checked){
                $("#edit_authority").find("#"+father_father_id).removeAttr("checked",true);
            }

            //给子类的子类去钩
            var child_id = $("#edit_authority").find("input[father_id="+access_id+"]").attr("id");
            $("#edit_authority").find("input[father_id="+child_id+"]").removeAttr("checked",true);

            //去掉最后一个钩后，去掉父类的钩
            var checked1 = true;
            $("#edit_authority").find("input[father_id="+father_id+"]").each(function(){
            if (true == $(this).is(':checked')) {
                 checked1 = false;
            }});

            if (checked1){
                $("#edit_authority").find(father_id_value).removeAttr("checked",true);
            }
        }
    })
}