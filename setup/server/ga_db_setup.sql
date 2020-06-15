create database IF NOT EXISTS ga;
use ga;

create table IF NOT EXISTS Data (
	id int unsigned not null auto_increment,
	created timestamp not null default current_timestamp,
	agent varchar(20) not null,
	data varchar(20) not null,
	device varchar(20) not null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS Object (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(20) not null,
	name varchar(20) not null unique key,
	parent varchar(20) default null,
	class varchar(20) default null,
	type varchar(30) not null,
	description varchar(50) null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS Setting (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(20) not null,
	belonging varchar(20) not null,
    setting varchar(30) not null,
	data varchar(100) not null,
	description varchar(50) null,
    primary key (id),
    foreign key 3_fk_object_name (belonging) references Object (name) on update cascade on delete cascade,
    unique key 3_uk_belonging_setting (belonging, setting)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS Grp (
    id smallint unsigned not null auto_increment,
    changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(20) not null,
	type varchar(30) not null,
	name varchar(20) not null,
    parent smallint unsigned null default null,
	description varchar(50) null default null,
    primary key (id),
    unique key 4_uk_name (name)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS Member (
    id smallint unsigned not null auto_increment,
    changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(20) not null,
    gid smallint unsigned not null,
    member varchar(20) not null,
	description varchar(50) null,
    primary key (id),
    foreign key 5_fk_object_name (member) references Object (name) on update cascade on delete cascade,
    foreign key 5_fk_grp_id (gid) references Grp (id) on update cascade on delete cascade,
    unique key 5_uk_gid_member (gid, member)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS GrpSetting (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(20) not null,
	belonging varchar(20) not null,
    setting varchar(30) not null,
	data varchar(100) not null,
	description varchar(50) null,
    primary key (id),
    foreign key 8_fk_grp_name (belonging) references Grp (name) on update cascade on delete cascade,
    unique key 8_uk_belonging_setting (belonging, setting)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS ProfileGrp (
    id smallint unsigned not null auto_increment,
    changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(20) not null,
	order_id tinyint unsigned not null default 1,
	parent smallint unsigned null default null,
	parent_id smallint unsigned not null,
	gid smallint unsigned not null,
	operator varchar(10) null default null,
	name varchar(20) not null,
	description varchar(50) null default null,
    primary key (id),
    foreign key 6_fk_grp_id (gid) references Grp (id) on update cascade on delete cascade,
    unique key 6_uk_parent_id (parent_id),
    unique key 6_uk_gid_name (gid, name),
    unique key 6_uk_gid_parent_order_id (gid, parent, order_id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS Profile (
    id smallint unsigned not null auto_increment,
    changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(20) not null,
	order_id tinyint unsigned not null default 1,
	parent smallint unsigned null default null,
	gid smallint unsigned not null,
	object varchar(20) not null,
	sector varchar(20) null default null,
	data_source varchar(20) not null,
	data_points smallint unsigned null default null,
	threshold varchar(20) not null,
	condi varchar(10) not null,
	operator varchar(10) null default null,
	name varchar(20) not null,
	description varchar(50) null default null,
    primary key (id),
    foreign key 7_fk_profilegrp_parent (parent) references ProfileGrp (parent_id) on update cascade on delete cascade,
    foreign key 7_fk_object_name (object) references Object (name) on update cascade on delete cascade,
    foreign key 7_fk_grp_name (sector) references Grp (name) on update cascade on delete cascade,
    foreign key 7_fk_grp_id (gid) references Grp (id) on update cascade on delete cascade,
    unique key 7_uk_gid_name (gid, name),
    unique key 7_uk_gid_parent_order_id (gid, parent, order_id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;
