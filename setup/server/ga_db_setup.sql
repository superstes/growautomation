create database IF NOT EXISTS ga;
use ga;
create table IF NOT EXISTS AgentDataDevice (
	id int unsigned not null auto_increment,
	created timestamp not null default current_timestamp,
	agent varchar(10) not null,
	data varchar(10) not null,
	unit tinyint unsigned not null default 1,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfig (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	agent varchar(10) not null,
	setting varchar(30) not null,
	data varchar(100) not null,
	description varchar(50) null,
	primary key (id),
	unique key unique_agent_setting (agent, setting)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigSector (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	description varchar(50) not null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigSectorGroup (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	description varchar(50) not null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigSectorGroupSetting (
    id smallint unsigned not null auto_increment,
    changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
    gid smallint unsigned not null default 1,
    sector smallint unsigned not null,
	description varchar(50) null,
    primary key (id),
    foreign key (gid) references AgentConfigSectorGroup (id) on update cascade on delete restrict,
    foreign key (sector) references AgentConfigSector (id) on update cascade on delete restrict,
    unique key unique_group_sector (group, sector)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigLink (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	description varchar(50) not null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigDeviceType (
	id tinyint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	description varchar(50) null,
	type varchar(10) not null unique key,
	category varchar(10) not null,
	primary key (id),
	index index_type_category (type, category)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigLinkSetting (
    id smallint unsigned not null auto_increment,
    changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
    link varchar(10) not null,
    type varchar(30) not null,
	description varchar(50) null,
    primary key (id),
    foreign key (link) references AgentConfigLink (id) on update cascade on delete restrict,
    foreign key (type) references AgentConfigDeviceType (type) on update cascade on delete restrict,
    unique key unique_link_type (link, type)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigDeviceTypeSetting (
    id smallint unsigned not null auto_increment,
    changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
    type varchar(10) not null,
    setting varchar(30) not null,
	data varchar(100) not null,
	description varchar(50) null,
    primary key (id),
    foreign key (type) references AgentConfigDeviceType (type) on update cascade on delete restrict,
    unique key unique_type_setting (type, setting)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigDevice (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	agent varchar(10) not null,
	device varchar(10) not null unique key,
	type varchar(10) not null,
	description varchar(50) null,
	primary key (id),
	foreign key (type) references AgentConfigDeviceType (device) on update cascade on delete restrict
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigDeviceSetting (
    id smallint unsigned not null auto_increment,
    changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
    device varchar(10) not null,
    setting varchar(30) not null,
	data varchar(100) not null,
	description varchar(50) null,
    primary key (id),
    foreign key (device) references AgentConfigDevice (device) on update cascade on delete restrict,
    unique key unique_device_setting (device, setting)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS ServerConfig (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	setting varchar(30) not null unique key,
	data varchar(100) not null,
	description varchar(50) null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS ServerConfigWeb (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	setting varchar(30) not null unique key,
	data varchar(100) not null,
	description varchar(50) null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS ServerConfigWebUser (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	username varchar(30) not null unique key,
	password varchar(200) not null,
	description varchar(50) null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS ServerConfigWebUserSetting (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	username varchar(30) not null,
	setting varchar(30) not null unique key,
	data varchar(100) not null,
	description varchar(50) null,
	primary key (id),
	foreign key (username) references ServerConfigWebUser (username) on update cascade on delete restrict,
    unique key unique_device_setting (username, setting)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS ServerConfigAgents (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null, 
	agent varchar(10) not null unique key,
	description varchar(50) null,
	version varchar(10) not null,
	enabled tinyint unsigned not null default 1,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;