// $(function(){
//     //修改联系方式
//     contact_edit();

//     //修改联系方式提交
//     $("#media_contact_update").click(function(event) {
//         var name_id = $("#contact_update_dialog").attr('name');
//         update_contact_wechat(name_id);
//     });

//     //删除联系方式
//     delete_contact();
// })

// // 修改联系人
// function contact_edit(){
//     $(".contact_edit").click(function() {
//         var contact_id = $(this).attr('name');
//         $("#contact_update_dialog").attr('name', contact_id);
//         $("#contact_update_dialog").modal();
//         $.getJSON('/media/relation?a=get_data',function(json) {
//             for(var i in json.data.index_info){
//                 if( contact_id == json.data.index_info[i].contact_id){
//                     var person = json.data.index_info[i].contact_person,
//                         position = json.data.index_info[i].contact_position,
//                         phone = json.data.index_info[i].contact_phone,
//                         tel = json.data.index_info[i].contact_tel,
//                         wechat = json.data.index_info[i].contact_wechat,
//                         qq = json.data.index_info[i].contact_qq,
//                         email = json.data.index_info[i].contact_email,
//                         other = json.data.index_info[i].contact_other
//                     $("#contact_person").val(person);
//                     $("#contact_position").val(position);
//                     $("#contact_phone").val(phone);
//                     $("#contact_tel").val(tel);
//                     $("#contact_wechat").val(wechat);
//                     $("#contact_qq").val(qq);
//                     $("#contact_email").val(email);
//                     $("#contact_other").val(other);
//                 }
//             }
//         });
//     });
// }

// // 修改联系人提交
// function update_contact_wechat(name_id){
//     var $contact_id = name_id;
//     var a = $('#contact_position').val();
//     var b = $('#contact_person').val();
//     var c = $('#contact_phone').val() ;
//     var d = $('#contact_email').val();
//     var e = $('#contact_tel').val();
//     var f = $('#contact_qq').val();
//     var w = $('#contact_wechat').val();
//     if (c == "" &&  w== "" && f == "") {
//         alert("手机、微信或QQ,请至少填写一项");
//         return false;
//     }
//     if (b == "") {
//         alert("输入不能为空");
//         return false;
//     }
//     if (c && ! is_phone(c)){
//         alert("请输入正确格式的手机号码");
//         return false
//     }
//     if( d &&(! is_mail(d))){
//         alert("请输入正确的email格式");
//         return false
//     }
//     if( e &&(! is_tel(e))){
//         alert("请输入正确的电话格式");
//         return false
//     }
//     if( f &&(! is_qq(f))){
//         alert("请输入正确的qq格式");
//         return false
//     }
//     dicArgs = {
//         'contact_id':$contact_id,
//         'contact_person': b,
//         'contact_position': a,
//         'contact_phone': c,
//         'contact_tel': e,
//         'contact_wechat': $('#contact_wechat').val(),
//         'contact_qq': f,
//         'contact_email': d,
//         'contact_other': $('#contact_other').val(),
//     };
//     $.ajax({
//         url: "/media/common?a=update_contact",
//         method: "post",
//         dataType:'json',
//         data: dicArgs,
//         success: function (result) {
//             console.log(result)
//             if (result.status == 200){
//                 location.reload();
//             }else if (result.status == 403) {
//                 alert("该用户无操作权限！");
//                 return false;
//             }else {
//                 alert("更新失败请重新操作！");
//                 return false;
//             }
//         }
//     });
// }

// // 删除联系人
// function delete_contact(){
//     $(".btn-delete").click(function(event) {
//         var $this = $(this);
//         if(confirm("您确定要删除此联系人吗")){
//             var $contact_id = $(this).attr('name');
//             var $relation_type = $(this).attr('relation_type')
//             var dicArgs = {
//                 'contact_id': $contact_id,
//                 'relation_type': $relation_type,
//             }
//             $.ajax({
//                 url: '/media/common?a=del_contact',
//                 method: 'post',
//                 dataType: 'json',
//                 data: dicArgs,
//                 success: function(json){
//                     if(json.status == 200){
//                         $this.parent("div").parent("td").parent("tr").remove();
//                     }
//                 }
//             })
//         }
//     });
// }  
