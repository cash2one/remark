$(function() {
	/*console.log("jQuery working")*/
	var $doc = $(document);
	$doc.on("change", "input[type='checkbox']" ,function(e) {
		var _self = $(this);
		var _getAttr = _self.attr("toggleElement");
		if ( _getAttr ) {
			if (_self.prop("checked")  === true ) {
				$(_getAttr).removeClass("hide")
			} else {
				$(_getAttr).addClass("hide")
			}
		}
	}).on("click", ".show-more-tip-033", function(e) {
		var obj = $(this);
		var target = obj.closest("td").find(".input-txa-2");
		target.toggleClass("hide");
		if (obj.html() == "展开") {
			obj.html("收起")
		} else {
			obj.html("展开")
		}
	});
	
	$(".datepicker").datepicker({
		language:"zh-CN",
		format: 'mm/dd/yyyy'
	})
	
})