/**
 * 省市区的操作
 */

//var city = function(){
//    var self = this;
//    self.basicUrl = '/city?a=get_list';
//    self.cityList = [-1, -1, -1];
//    self.changeParent = '';
//    self.isAuto = false;
//
//    self.select = function(){
//        $('select').change(function(){
//            var target = $(this).attr('name');
//            var id = $(this).val();
//            if(id==''){
//                if(target=='province'){
//                    $('#city').empty().append('<option value="">城市</option>');
//                    $('#county').empty().append('<option value="">区县</option>');
//                    cityList = [-1,-1,-1];
//                }else if(target=='city'){
//                    $('#county').empty().append('<option value="">区县</option>');
//                    cityList[1] = cityList[2] = -1;
//                }else{
//                    cityList[2] = -1;
//                }
//                return;
//            }
//            if(target!='county'){
//                getSelectList(id,target);
//                if(target=='province'){
//                    cityList[0] = id;
//                }else{
//                    cityList[1] = id;
//                }
//            }else{
//                cityList[2] = id;
//            }
//        });
//    }
//
//    self.getSelectList = function(id, idfrom){
//        change_parent = idfrom;
//        var obj = {};
//        obj.method='get';
//        obj.url = basic_url + '&parent_id='+id;
//        obj.dataType = 'json';
//        obj.success = function(data){
//            var target;
//            var tarWord;
//            var tarId;
//            var tar2 = '';
//            switch (change_parent){
//                case 'province':
//                    target = 'city';
//                    tarWord = '城市';
//                    tarId = cityList[1];
//                    tar2 = 'county';
//                    break;
//                case 'city':
//                    target = 'county';
//                    tarWord = '区县';
//                    tarId = cityList[2];
//                    break;
//                case 'main':
//                    target = 'province';
//                    tarWord = '省份';
//                    tarId = cityList[0];
//                    break;
//            }
//            var main = $('#' + target);
//            main.empty();
//            main.append('<option value="">' + tarWord + '</option>');
//            if(!isAuto && target=='city')cityList[1]=-1;
//            if(tar2!=''){
//                $('#' + tar2).empty().append('<option value="">区县</option>');
//                if(isAuto){
//                    isAuto = !isAuto;
//                }else{
//                    cityList[2] = -1;
//                }
//            }
//
//            var list = data.data;
//            for(var i=0;i<list.length;i++){
//                main.append('<option value="' + list[i].id + '">' + decodeURIComponent(list[i].name) + '</option>');
//            }
//            if(tarId!=-1){
//                main.val(tarId);
//            }
//            if(change_parent!='city' && main.val()!=''){
//                getSelectList(main.val(),target);
//            }
//        };
        $.ajax(obj)
    }

}
$(function(){
    var basic_url = '/city?a=get_list';
    var cityList = [-1,-1,-1];
    var change_parent;
    var isAuto = false;

    $('select').change(function(){
        var target = $(this).attr('name');
        var id = $(this).val();
        if(id==''){
            if(target=='province'){
                $('#city').empty().append('<option value="">城市</option>');
                $('#county').empty().append('<option value="">区县</option>');
                cityList = [-1,-1,-1];
            }else if(target=='city'){
                $('#county').empty().append('<option value="">区县</option>');
                cityList[1] = cityList[2] = -1;
            }else{
                cityList[2] = -1;
            }
            return;
        }
        if(target!='county'){
            getSelectList(id,target);
            if(target=='province'){
                cityList[0] = id;
            }else{
                cityList[1] = id;
            }
        }else{
            cityList[2] = id;
        }
    });
    
    function getSelectList(id,idfrom){
        change_parent = idfrom;
        var obj = {};
        obj.method='get';
        obj.url = basic_url + '&parent_id='+id;
        obj.dataType = 'json';
        obj.success = function(data){
            var target;
            var tarWord;
            var tarId;
            var tar2 = '';
            switch (change_parent){
                case 'province':
                    target = 'city';
                    tarWord = '城市';
                    tarId = cityList[1];
                    tar2 = 'county';
                    break;
                case 'city':
                    target = 'county';
                    tarWord = '区县';
                    tarId = cityList[2];
                    break;
                case 'main':
                    target = 'province';
                    tarWord = '省份';
                    tarId = cityList[0];
                    break;
            }
            var main = $('#' + target);
            main.empty();
            main.append('<option value="">' + tarWord + '</option>');
            if(!isAuto && target=='city')cityList[1]=-1;
            if(tar2!=''){
                $('#' + tar2).empty().append('<option value="">区县</option>');
                if(isAuto){
                    isAuto = !isAuto;
                }else{
                    cityList[2] = -1;
                }
            }

            var list = data.data;
            for(var i=0;i<list.length;i++){
                main.append('<option value="' + list[i].id + '">' + decodeURIComponent(list[i].name) + '</option>');
            }
            if(tarId!=-1){
                main.val(tarId);
            }
            if(change_parent!='city' && main.val()!=''){
                getSelectList(main.val(),target);
            }

        };
        $.ajax(obj)
    }
});
