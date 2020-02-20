create database IF NOT EXISTS ga;
use ga;
create table IF NOT EXISTS AgentDataDevice (
	id int unsigned not null auto_increment,
	created timestamp not null default current_timestamp,
	controller varchar(10) not null,
	data varchar(10) not null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigSector (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	controller varchar(10) not null,
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
	datatype varchar(20) not null,
	function varchar(30) not null,
	enabled tinyint unsigned not null default 1,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigDevice (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	controller varchar(10) not null,
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
    foreign key (name) references AgentConfigDevice (name) on update cascade on delete restrict
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

create table IF NOT EXISTS AgentConfigMain (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	controller varchar(10) not null,
	name varchar(30) not null,
	data varchar(100) not null,
	description varchar(50) null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS ServerConfigMain (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	name varchar(30) not null,
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
	name varchar(30) not null,
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
	controller varchar(10) not null,
	description varchar(50) null,
	enabled tinyint unsigned not null default 1,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;