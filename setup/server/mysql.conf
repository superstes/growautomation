create database IF NOT EXISTS ga;
use ga;
create table IF NOT EXISTS AgentDataSensors (
	id int unsigned not null auto_increment,
	created timestamp not null default current_timestamp,
	controller varchar(10) not null,
	data1 varchar(10) not null,
	data2 varchar(10) null,
	data3 varchar(10) null,
	data4 varchar(10) null,
	data5 varchar(10) null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentDataActions (
	id int unsigned not null auto_increment,
	created timestamp not null default current_timestamp,
	controller varchar(10) not null,
	state varchar(20) not null,
	data1 varchar(10) null,
	data2 varchar(10) null,
	data3 varchar(10) null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigActionSectors (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	controller varchar(10) not null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigSensorTypes (
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

create table IF NOT EXISTS AgentConfigActionTypes (
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

create table IF NOT EXISTS AgentConfigSensorTypes (
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

create table IF NOT EXISTS AgentConfigDownlinkTypes (
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

create table IF NOT EXISTS AgentConfigDownlinks (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	controller varchar(10) not null,
	name varchar(10) not null unique key,
	downlinktype varchar(10) not null,
	port tinyint unsigned not null default 0,
	enabled tinyint unsigned not null default 1,
	primary key (id),
	foreign key (downlinktype)
	references AgentConfigDownlinkTypes (name)
	on update cascade on delete restrict
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigSensors (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	controller varchar(10) not null,
	name varchar(10) not null unique key,
	sensortype varchar(10) not null,
	actionsector smallint unsigned not null default 1,
	downlink varchar(10) null,
	port tinyint unsigned not null default 0,
	enabled tinyint unsigned not null default 1,
	data1info varchar(20) not null,
	data2info varchar(20) null,
	data3info varchar(20) null,
	data4info varchar(20) null,
	data5info varchar(20) null,
	primary key (id),
	foreign key (sensortype)
	references AgentConfigSensorTypes (name)
	on update cascade on delete restrict,
	foreign key (downlink)
	references AgentConfigDownlinks (name)
	on update cascade on delete restrict,
	foreign key (actionsector)
	references AgentConfigActionSectors (id)
	on update cascade on delete restrict
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigActions (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	controller varchar(10) not null,
	name varchar(10) not null unique key,
	actiontype varchar(10) not null,
	actionsector smallint unsigned not null default 1,
	downlink varchar(10) null,
	downlinktype varchar(10) not null,
	port tinyint unsigned not null default 0,
	enabled tinyint unsigned not null default 1,
	setting1 varchar(40) null,
	setting2 varchar(40) null,
	setting3 varchar(20) null,
	setting4 varchar(20) null,
	setting5 varchar(20) null,
	setting6 varchar(20) null,
	setting7 varchar(20) null,
	data1info varchar(20) null,
	data2info varchar(20) null,
	data3info varchar(20) null,
	primary key (id),
	foreign key (actiontype)
	references AgentConfigActionTypes (name)
	on update cascade on delete restrict,
	foreign key (downlink)
	references AgentConfigDownlinks (name)
	on update cascade on delete restrict,
	foreign key (actionsector)
	references AgentConfigActionSectors (id)
	on update cascade on delete restrict
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS AgentConfigActionLinks (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	sensortype1 varchar(10) not null,
	sensortype2 varchar(10),
	sensortype3 varchar(10),
	sensortype4 varchar(10),
	sensortype5 varchar(10),
	actiontype1 varchar(10) not null,
	actiontype2 varchar(10),
	actiontype3 varchar(10),
	actiontype4 varchar(10),
	actiontype5 varchar(10),
	primary key (id),
	foreign key (sensortype1)
	references AgentConfigSensorTypes (name)
	on update cascade on delete restrict,
	foreign key (sensortype2)
	references AgentConfigSensorTypes (name)
	on update cascade on delete restrict,
	foreign key (sensortype3)
	references AgentConfigSensorTypes (name)
	on update cascade on delete restrict,
	foreign key (sensortype4)
	references AgentConfigSensorTypes (name)
	on update cascade on delete restrict,
	foreign key (sensortype5)
	references AgentConfigSensorTypes (name)
	on update cascade on delete restrict,
	foreign key (actiontype1)
	references AgentConfigSensorTypes (name)
	on update cascade on delete restrict,
	foreign key (actiontype2)
	references AgentConfigSensorTypes (name)
	on update cascade on delete restrict,
	foreign key (actiontype3)
	references AgentConfigSensorTypes (name)
	on update cascade on delete restrict,
	foreign key (actiontype4)
	references AgentConfigSensorTypes (name)
	on update cascade on delete restrict,
	foreign key (actiontype5)
	references AgentConfigSensorTypes (name)
	on update cascade on delete restrict
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table AgentConfigMain (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(10) not null,
	controller varchar(10) not null,
	name varchar(30) not null,
	data varchar(100) not null,
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
	name varchar(30) not null,
	data varchar(100) not null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;