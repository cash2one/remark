/* To avoid CSS expressions while still supporting IE 7 and IE 6, use this script */
/* The script tag referencing this file must be placed before the ending body tag. */

/* Use conditional comments in order to target IE 7 and older:
	<!--[if lt IE 8]><!-->
	<script src="ie7/ie7.js"></script>
	<!--<![endif]-->
*/

(function() {
	function addIcon(el, entity) {
		var html = el.innerHTML;
		el.innerHTML = '<span style="font-family: \'yidao\'">' + entity + '</span>' + html;
	}
	var icons = {
		'yd-logo': '&#xe600;',
		'yd-notification': '&#xe601;',
		'yd-user': '&#xe602;',
		'yd-nav': '&#xe603;',
		'yd-search': '&#xe604;',
		'yd-list': '&#xe900;',
		'yd-close': '&#xe605;',
		'yd-add': '&#xe606;',
		'yd-delete': '&#xe607;',
		'yd-select': '&#xe608;',
		'yd-checked': '&#xe609;',
		'yd-up': '&#xe60a;',
		'yd-right': '&#xe60b;',
		'yd-down': '&#xe60c;',
		'yd-left': '&#xe60d;',
		'yd-more': '&#xe60e;',
		'yd-link': '&#xe610;',
		'yd-money': '&#xe611;',
		'yd-information': '&#xe612;',
		'yd-find': '&#xe613;',
		'yd-history': '&#xe614;',
		'yd-dot': '&#xe60f;',
		'0': 0
		},
		els = document.getElementsByTagName('*'),
		i, c, el;
	for (i = 0; ; i += 1) {
		el = els[i];
		if(!el) {
			break;
		}
		c = el.className;
		c = c.match(/yd-[^\s'"]+/);
		if (c && icons[c[0]]) {
			addIcon(el, icons[c[0]]);
		}
	}
}());
