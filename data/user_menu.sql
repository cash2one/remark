
-- source user_menu.sql 运行
-- 数据库对应 yidao_admin_new：

insert into module (label,parent_id,access_level,access_id,class_active,menu_route) values('权限模块',7,2,35,'manager_module','/admin_user/module_manager');

alter table module
  add sort int(10) not null default '0' comment '排序' after is_exsit_child;