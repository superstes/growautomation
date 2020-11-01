create database IF NOT EXISTS ga;
use ga;

create table IF NOT EXISTS Object (
	created timestamp not null default current_timestamp,
	updated timestamp not null default current_timestamp on update current_timestamp,
	ObjectID bigint unsigned not null auto_increment,
	ObjectName varchar(255) not null,
	ObjectDescription varchar(255) null default null,
	primary key (ObjectID)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

--- settings

create table IF NOT EXISTS ValueType (
	created timestamp not null default current_timestamp,
	updated timestamp not null default current_timestamp on update current_timestamp,
	ValueID varchar(255) not null,
	ValueName varchar(255) not null,
	ValueUnit varchar(255) not null,
	ValueDescription varchar(255) null default null,
	primary key (ValueID)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS SettingType (
	created timestamp not null default current_timestamp,
	updated timestamp not null default current_timestamp on update current_timestamp,
	TypeID bigint unsigned not null auto_increment,
	TypeKey varchar(255) not null,
	TypeDescription varchar(255) null default null,
	TypeValueID varchar(255) not null,
	primary key (TypeID),
	foreign key st_fk_typevalueid (TypeValueID) references ValueType (ValueID) on update cascade on delete cascade
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS ObjectSetting (
	created timestamp not null default current_timestamp,
	updated timestamp not null default current_timestamp on update current_timestamp,
	SettingID bigint unsigned not null auto_increment,
	ObjectID bigint unsigned null default null,
	SettingTypeID bigint unsigned not null,
	SettingValue varchar(255),
	primary key (SettingID),
	foreign key os_fk_objectid (ObjectID) references Object (ObjectID) on update cascade on delete cascade,
	foreign key os_fk_settingtypeid (SettingTypeID) references SettingType (TypeID) on update cascade on delete cascade,
    unique key os_uk_settingtypeid_objectid (SettingTypeID, ObjectID)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

-- groups

create table IF NOT EXISTS GrpType (
	created timestamp not null default current_timestamp,
	updated timestamp not null default current_timestamp on update current_timestamp,
	TypeID bigint unsigned not null auto_increment,
	TypeName varchar(255) not null,
	TypeCategory varchar(255) not null,
	TypeDescription varchar(255) null default null,
	primary key (TypeID)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS Grp (
	created timestamp not null default current_timestamp,
	updated timestamp not null default current_timestamp on update current_timestamp,
	GroupID bigint unsigned not null auto_increment,
	GroupName varchar(255) not null,
	GroupParent bigint unsigned null default null,
	GroupDescription varchar(255) null default null,
	GroupTypeID bigint unsigned null default null,
	primary key (GroupID),
	foreign key g_fk_grouptypeid (GroupTypeID) references GrpType (TypeID) on update cascade on delete cascade
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS GrpSetting (
	created timestamp not null default current_timestamp,
	updated timestamp not null default current_timestamp on update current_timestamp,
	SettingID bigint unsigned not null auto_increment,
	GroupID bigint unsigned not null,
	SettingTypeID bigint unsigned not null,
	SettingValue varchar(255),
	primary key (SettingID),
	foreign key gs_fk_grpid (GroupID) references Grp (GroupID) on update cascade on delete cascade,
	foreign key gs_fk_settingtypeid (SettingTypeID) references SettingType (TypeID) on update cascade on delete cascade,
    unique key gs_uk_settingtypeid_groupid (SettingTypeID, GroupID)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS SettingGroupMember (
	created timestamp not null default current_timestamp,
	updated timestamp not null default current_timestamp on update current_timestamp,
	ChainID bigint unsigned not null auto_increment,
	GroupID bigint unsigned not null,
	SettingID bigint unsigned not null,
	primary key (ChainID),
	foreign key sgm_fk_settingid (SettingID) references ObjectSetting (SettingID) on update cascade on delete cascade,
	foreign key sgm_fk_groupid (GroupID) references Grp (GroupID) on update cascade on delete cascade,
	unique key sgm_uk_settingid_groupid (SettingID, GroupID)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS ObjectGroupMember (
	created timestamp not null default current_timestamp,
	updated timestamp not null default current_timestamp on update current_timestamp,
	ChainID bigint unsigned not null auto_increment,
	GroupID bigint unsigned not null,
	ObjectID bigint unsigned not null,
	primary key (ChainID),
	foreign key ogm_fk_objectid (ObjectID) references Object (ObjectID) on update cascade on delete cascade,
	foreign key ogm_fk_groupid (GroupID) references Grp (GroupID) on update cascade on delete cascade,
	unique key ogm_uk_objectid_groupid (ObjectID, GroupID)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

--- input/output handling

create table IF NOT EXISTS InputData (
	created timestamp not null default current_timestamp,
	DatasetID bigint unsigned not null auto_increment,
	ObjectID bigint unsigned not null,
	DataValue varchar(255) not null,
	DataValueID varchar(255) not null,
	primary key (DatasetID),
	foreign key id_fk_objectid (ObjectID) references Object (ObjectID) on update cascade on delete cascade,
	foreign key id_fk_datavalueid (DataValueID) references ValueType (ValueID) on update cascade on delete cascade
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS TaskLog (
	created timestamp not null default current_timestamp,
	LogID bigint unsigned not null auto_increment,
	TaskCategory varchar(255) not null,
	TaskResult varchar(255) not null,
	TaskMessage varchar(255) not null,
	ObjectID bigint unsigned not null,
	primary key (LogID),
	foreign key tl_fk_objectid (ObjectID) references Object (ObjectID) on update cascade on delete cascade
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

-- conditions
--   conditions themself are groups with type id set to 'condition'

create table IF NOT EXISTS ConditionObject (
	created timestamp not null default current_timestamp,
	updated timestamp not null default current_timestamp on update current_timestamp,
	ConditionID bigint unsigned not null auto_increment,
	ConditionName varchar(255) not null,
	ConditionOperator varchar(255) not null,
	ConditionValue varchar(255) not null,
	ConditionPeriod bigint unsigned not null default 600,
	ConditionObject varchar(255) not null,
	ConditionDescription varchar(255) null default null,
	primary key (ConditionID)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS ConditionLink (
	created timestamp not null default current_timestamp,
	updated timestamp not null default current_timestamp on update current_timestamp,
	LinkID bigint unsigned not null auto_increment,
	LinkOperator varchar(255) not null,
	primary key (LinkID)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

create table IF NOT EXISTS ConditionLinkMember (
	created timestamp not null default current_timestamp,
	updated timestamp not null default current_timestamp on update current_timestamp,
	ChainID bigint unsigned not null auto_increment,
	GroupID bigint unsigned default null,
	ConditionID bigint unsigned default null,
	LinkID bigint unsigned not null,
	primary key (ChainID),
	foreign key clm_fk_linkid (LinkID) references ConditionLink (LinkID) on update cascade on delete cascade,
	foreign key clm_fk_groupid (GroupID) references Grp (GroupID) on update cascade on delete cascade,
	foreign key clm_fk_conditionid (ConditionID) references ConditionObject (ConditionID) on update cascade on delete cascade,
	unique key clm_uk_linkid_conditionid_groupid (LinkID, ConditionID, GroupID)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;

-- check that either GroupID or ConditionID is set

DELIMITER //
CREATE TRIGGER clm_tr_insert_groupid_conditionid_notnull BEFORE INSERT ON ConditionLinkMember
FOR EACH ROW BEGIN
  IF (NEW.GroupID IS NULL AND NEW.ConditionID IS NULL) THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = '\'GroupID\' and \'ConditionID\' cannot both be null';
  END IF;
END//
CREATE TRIGGER clm_tr_update_groupid_conditionid_notnull BEFORE UPDATE ON ConditionLinkMember
FOR EACH ROW BEGIN
  IF (NEW.GroupID IS NULL AND NEW.ConditionID IS NULL) THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = '\'GroupID\' and \'ConditionID\' cannot both be null';
  END IF;
END//
DELIMITER ;

create table IF NOT EXISTS ConditionMember (
	created timestamp not null default current_timestamp,
	updated timestamp not null default current_timestamp on update current_timestamp,
	ChainID bigint unsigned not null auto_increment,
	GroupID bigint unsigned not null,
	LinkID bigint unsigned not null,
	primary key (ChainID),
	foreign key cm_fk_linkid (LinkID) references ConditionLink (LinkID) on update cascade on delete cascade,
	foreign key cm_fk_groupid (GroupID) references Grp (GroupID) on update cascade on delete cascade,
	unique key cm_uk_linkid_groupid (LinkID, GroupID)
)engine innodb,
 character set utf8,
 collate utf8_unicode_ci;
