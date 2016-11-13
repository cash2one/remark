function is_phone(num){
    num =num.toString();
    // var re = /^\d{11}$/;
    var re = /^1[3|4|5|8][0-9]\d{8}$/
    return re.test(num)
}
function is_mail(email){
    email = email.toString();
    var  re = /^\w+([-+._]\w+)*@\w+([-.]\w+)*\.\w+([-.]w+)*$/;
    return re.test(email)
}
function is_qq(qq){
    qq = qq.toString();
    // var re = /[1-9][0-9]{4,}/;
    var re = /^[1-9][0-9]{4,9}$/;
    return re.test(qq)
}
function is_tel(tel){
    tel = tel.toString();
    var re = /^\(?0\d{2}\)?[-]?\d{8}$|^0\d{2}[-]?\d{8}$|^\(?0\d{3}\)?[-]?\d{7}$|^0\d{3}[-]?\d{7}$|^\d{7,8}$/;
    return re.test(tel)
}