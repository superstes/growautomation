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

create table IF NOT EXISTS Category (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(20) not null,
	name varchar(30) not null unique key,
	description varchar(50) null,
	primary key (id)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS ObjectReference (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(20) not null,
	name varchar(30) not null unique key,
	description varchar(50) null,
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
	primary key (id),
	foreign key (class) references ObjectReference (name) on update cascade on delete cascade,
	foreign key (parent) references ObjectReference (name) on update cascade on delete cascade,
	foreign key (type) references Category (name) on update cascade on delete cascade
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS Setting (
	id smallint unsigned not null auto_increment,
	changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(20) not null,
    type varchar(30) not null,
	belonging varchar(20) not null,
    setting varchar(30) not null,
	data varchar(100) not null,
	description varchar(50) null,
    primary key (id),
    foreign key (belonging) references Object (name) on update cascade on delete cascade,
    foreign key (type) references Category (name) on update cascade on delete cascade,
    unique key unique_type_belonging_setting (type, belonging, setting)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS Grouping (
    id smallint unsigned not null auto_increment,
    changed timestamp not null default current_timestamp on update current_timestamp,
	author varchar(20) not null,
    gid smallint unsigned not null,
	type varchar(30) not null,
    member varchar(20) not null,
	description varchar(50) null,
    primary key (id),
    foreign key (member) references Object (name) on update cascade on delete cascade,
    foreign key (type) references Category (name) on update cascade on delete cascade,
    unique key unique_gid_type_member (gid, type, member)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;
