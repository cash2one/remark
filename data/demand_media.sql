

-- source demand_media.sql 运行

-- 在yidao_profile_dev库

alter table follow_group
  modify category tinyint(2) NOT NULL comment '1自媒体, 2广告需求, 3文案, 4投放计划, 5策划, 6效果';

create table feedback_follow(
	id int(10) NOT NULL auto_increment comment '序号',
	user_id tinyint(4) NOT NULL default 0 comment '用户编号',
	feedback_id tinyint(4) NOT NULL default 0 comment '效果编号',
	group_id tinyint(4) NOT NULL default 0 comment '组编号',
	remark varchar(128) NOT NULL default '' comment '备注',
	createTime int(10) NOT NULL default 0 comment '创建时间',
	status tinyint(4) NOT NULL default 1 comment '有效性0 无效; 1有效',
	PRIMARY KEY  (id)
);