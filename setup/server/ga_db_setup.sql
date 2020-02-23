create database IF NOT EXISTS ga;
use ga;
create table IF NOT EXISTS AgentDataDevice (
	id int unsigned not null auto_increment,
	created timestamp not null default current_timestamp,
	agent varchar(10) not null,
	data varchar(10) not null,
	type tinyint unsigned not null default 1,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigSector (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	agent varchar(10) not null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigDeviceType (
	id tinyint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	description varchar(50) null,
	name varchar(10) not null unique key,
	function varchar(30) not null,
	enabled tinyint unsigned not null default 1,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigSensor (
	id tinyint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	description varchar(50) null,
	name varchar(10) not null,
	data tinyint unsigned not null default 1,
	unit varchar(10) not null,
	primary key (id),
	foreign key (name) references AgentConfigDeviceType (name) on update cascade on delete restrict,
	unique key unique_name_data (name, data)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigDevice (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	agent varchar(10) not null,
	name varchar(10) not null unique key,
	type varchar(10) not null,
	sector smallint unsigned not null default 1,
	downlink varchar(10) null,
	port tinyint unsigned not null default 0,
	enabled tinyint unsigned not null default 1,
	primary key (id),
	foreign key (type) references AgentConfigDeviceType (name) on update cascade on delete restrict,
	foreign key (sector) references AgentConfigSector (id) on update cascade on delete restrict
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigDeviceSetting (
    id smallint unsigned not null auto_increment,
    name varchar(10) not null,
    setting varchar(30) not null,
	data varchar(100) not null,
	description varchar(50) null,
    primary key (id),
    foreign key (name) references AgentConfigDevice (name) on update cascade on delete restrict,
    unique key unique_name_setting (name, setting)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigLink (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	description varchar(50) null,
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

create table IF NOT EXISTS ServerConfig (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	setting varchar(30) not null unique key,
	data varchar(100) not null,
	description varchar(50) null,
	primary key (id),
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