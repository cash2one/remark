/*顶部菜单动态控制*/
$(function() {
    var isIE = !!window.ActiveXObject;
    var scrollTop = $(window).scrollTop();
    var headerHeight = 40;
    $(window).scroll(function(e) {
        scrollTop = $(window).scrollTop();
        if (scrollTop >= headerHeight) {
            $("#header").addClass("headerfixed")
        } else {
            if ($("#header").hasClass("headerfixed")) {
                $("#header").removeClass("headerfixed")
            }
        }
    })
});