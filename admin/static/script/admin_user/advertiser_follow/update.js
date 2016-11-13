$(function(){
    var $id = $("#ad_id").attr("ad-id");

    window.UMEDITOR_HOME_URL = "../../static/ueditor/";
    window.um = UM.getEditor('advertiser_requirement',{
        initialFrameWidth : 1000,
        initialFrameHeight: 300
    });
    window.um = UM.getEditor('advertiser_progress',{
        initialFrameWidth : 1000,
        initialFrameHeight: 300
    });
    window.um = UM.getEditor('advertiser_product_info',{
        initialFrameWidth : 1000,
        initialFrameHeight: 300
    });
    window.um = UM.getEditor('advertiser_audience_info',{
        initialFrameWidth : 1000,
        initialFrameHeight: 300
    });
    window.um = UM.getEditor('advertiser_remark',{
        initialFrameWidth : 1000,
        initialFrameHeight: 300
    });

    // 修改广告主提交
    $("#on_advertiser_text_commit").click(function(event) {
        on_advertiser_text_commit($id);
    });

    // 获取公司全称
    $.getJSON('/admin_user/advertiser_follow?a=get_basic&id='+ $id,function(json) {
        var company = json.data.detail_info_value.company;
        $("#advertiser_company").val(company);
    });

    //获取已填写内容
    $.getJSON('/admin_user/advertiser_follow?a=get_text&id='+ $id,function(json){
        var requirement = json.data.detail_info_value.requirement,
            progress = json.data.detail_info_value.progress,
            product_info = json.data.detail_info_value.product_info,
            audience_info = json.data.detail_info_value.audience_info,
            remark = json.data.detail_info_value.remark
        $("#advertiser_requirement").text(requirement);
        $("#advertiser_requirement").siblings('.edui-body-container').html(requirement);
        $("#advertiser_progress").text(progress);
        $("#advertiser_progress").siblings('.edui-body-container').html(progress);
        $("#advertiser_product_info").text(product_info);
        $("#advertiser_product_info").siblings('.edui-body-container').html(product_info);
        $("#advertiser_audience_info").text(audience_info);
        $("#advertiser_audience_info").siblings('.edui-body-container').html(audience_info);
        $("#advertiser_remark").text(remark);
        $("#advertiser_remark").siblings('.edui-body-container').html(remark);
    })
});

// 修改广告主提交
function on_advertiser_text_commit($id){
    dicArgs = {
        'id':$id,
        'advertiser_company': $('#advertiser_company').val(),
        'advertiser_requirement': $('#advertiser_requirement').val(),
        'advertiser_progress': $('#advertiser_progress').val(),
        'advertiser_product_info': $('#advertiser_product_info').val(),
        'advertiser_audience_info': $('#advertiser_audience_info').val(),
        'advertiser_remark': $('#advertiser_remark').val()
    };
    console.log($('#advertiser_requirement').val())
    $.ajax({
        url: "/admin_user/advertiser_follow?a=update_text",
        method: "post",
        dataType:'json',
        data: dicArgs,
        success: function (result) {
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