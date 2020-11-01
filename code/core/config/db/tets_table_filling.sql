-- objects
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('sensor-dht22-temp','Air Humidity and Temperature sensor');
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('sensor-dht22-humi','Capacitive earth humidity sensor');
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('sensor-wind','Wind speed and direction sensor');
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('actor-pump','Water pump actor');
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('actor-heat','Air heater actor');
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('actor-win','Window opener actor');
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('controller','Controller system object');
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('output-timer','System output timer');
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('backup-timer','System backup timer');

-- grp type
INSERT IGNORE INTO ga.GrpType (TypeName, TypeCategory, TypeDescription) VALUES ('input','device','Input device aka sensor');
INSERT IGNORE INTO ga.GrpType (TypeName, TypeCategory, TypeDescription) VALUES ('output','device','Input device aka actor');
INSERT IGNORE INTO ga.GrpType (TypeName, TypeCategory, TypeDescription) VALUES ('controller','core','Controller system');
INSERT IGNORE INTO ga.GrpType (TypeName, TypeCategory, TypeDescription) VALUES ('timer','core','System timers');
INSERT IGNORE INTO ga.GrpType (TypeName, TypeCategory, TypeDescription) VALUES ('condition','setting','Output conditions');

-- groups
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('model-dht22-temp','DHT22 temperature sensor model', '1');
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('model-dht22-humi','DHT22 humidity sensor model', '1');
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('model-wind','Wind speed and direction sensor model', '1');
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('model-pump','Water pump actor model', '2');
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('model-heat','Air heater actor model', '2');
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('model-win','Window opener actor model', '2');
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('system-controller','Controller system group', '3');
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('system-timer','System timer group', '4');
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('condi-grp1','Condition group 1', '5');
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID, GroupParent) VALUES ('condi-grp2','Condition group 2', '5', '9');

-- object group member
INSERT IGNORE INTO ga.ObjectGroupMember (GroupID, ObjectID) VALUES ('1','1');
INSERT IGNORE INTO ga.ObjectGroupMember (GroupID, ObjectID) VALUES ('2','2');
INSERT IGNORE INTO ga.ObjectGroupMember (GroupID, ObjectID) VALUES ('3','3');
INSERT IGNORE INTO ga.ObjectGroupMember (GroupID, ObjectID) VALUES ('4','4');
INSERT IGNORE INTO ga.ObjectGroupMember (GroupID, ObjectID) VALUES ('5','5');
INSERT IGNORE INTO ga.ObjectGroupMember (GroupID, ObjectID) VALUES ('6','6');
INSERT IGNORE INTO ga.ObjectGroupMember (GroupID, ObjectID) VALUES ('7','7');
INSERT IGNORE INTO ga.ObjectGroupMember (GroupID, ObjectID) VALUES ('8','8');

-- settingvaluetype
INSERT IGNORE INTO ga.ValueType (ValueID, ValueName, ValueUnit) VALUES ('str', 'String','str');
INSERT IGNORE INTO ga.ValueType (ValueID, ValueName, ValueUnit) VALUES ('bool', 'Bool','bool');
INSERT IGNORE INTO ga.ValueType (ValueID, ValueName, ValueUnit) VALUES ('list', 'List','list');
INSERT IGNORE INTO ga.ValueType (ValueID, ValueName, ValueUnit) VALUES ('int', 'Integer','int');
INSERT IGNORE INTO ga.ValueType (ValueID, ValueName, ValueUnit) VALUES ('json', 'JSON array','json');
INSERT IGNORE INTO ga.ValueType (ValueID, ValueName, ValueUnit) VALUES ('float', 'Floating point number','float');

-- settingtype
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('GPIO or downlink pin','connection','int');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Enabled state','enabled','bool');
-- inputdevices
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Downlink','downlink','str');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Timer','timer','int');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Function','function','str');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Function argument','function_arg','str');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Binary path','function_bin','str');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Unit','unit','str');
-- outputdevices
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Reverse','reverse','bool');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Reverse type','reverse_type','int');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Reverse function','reverse_function','str');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Reverse function argument','reverse_function_arg','str');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Reverse binary path','reverse_function_bin','str');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Reverse timer','reverse_timer','int');
-- system
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System root path','path_root','str');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System log path','path_log','str');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System backup path','path_backup','str');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System sql server','sql_server','str');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System sql port','sql_port','str');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System sql user','sql_user','str');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System sql password','sql_secret','str');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System sql database','sql_database','str');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System log level','log_level','int');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System debug mode','debug','bool');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System security mode','security','bool');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System backup','backup','bool');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System timezone','timezone','str');

INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Input data type','datatype','str');

-- object settings
-- select * from ObjectSetting INNER JOIN SettingType ON ObjectSetting.SettingTypeID = SettingType.TypeID;
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('1','2','1');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('1','1','4');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('1','3',Null);

INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('2','2','1');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('2','1','4');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('2','3',Null);

INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('3','2','1');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('3','1','12');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('3','3',Null);
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('3','4','500');

INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('4','2','1');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('4','1','7');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('4','3',Null);

INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('5','2','1');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('5','1','1');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('5','3','downlink-rand');

INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('6','2','1');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('6','1','3');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('6','3',Null);

INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('7','2','1');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('7','20','test');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('7','21','789TMP01!');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('7','23','3');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('7','24','1');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('7','25','0');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('7','27','MEZ');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('7','15','/etc/ga');

-- system timers
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('8','2','1');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('8','4','60');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('9','2','0');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('9','4','86400');

-- group settings
-- select * from GrpSetting INNER JOIN SettingType ON GrpSetting.SettingTypeID = SettingType.TypeID;
-- each group must have at least 1 setting for the supply query to catch it
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('1','2','1');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('1','5','dht22.py');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('1','6','temperature');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('1','7','/usr/bin/python3');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('1','4','60');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('1','8','°C');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('1','28','float');

INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('2','2','1');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('2','5','dht22.py');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('2','6','humidity');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('2','7','/usr/bin/python3');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('2','4','30');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('2','8','RH');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('2','28','float');

INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('3','2','1');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('3','5','wind.py');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('3','6',Null);
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('3','7','/usr/bin/python3');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('3','4','900');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('3','8','km/h');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('3','28','int');

INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('4','2','1');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('4','5','pump.py');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('4','6',Null);
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('4','7','/usr/bin/python3');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('4','9','0');

INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('5','2','1');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('5','5','heat.py');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('5','6',Null);
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('5','7','/usr/bin/python3');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('5','9','0');

INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('6','2','1');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('6','5','win.py');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('6','6','first');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('6','7','/usr/bin/python3');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('6','9','1');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('6','11','win.py');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('6','13','/usr/bin/python3');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('6','12','reverse');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('6','10','1');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('6','14','90');

INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('7','15','/etc/growautomation');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('7','16','/var/log/growautomation');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('7','17','/var/backups/growautomation');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('7','18','127.0.0.1');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('7','19','3306');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('7','20','gadmin');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('7','21','random');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('7','22','ga');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('7','23','1');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('7','24','0');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('7','25','1');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('7','26','1');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('7','27','UTC');

INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('8','4','600');

-- conditions
-- get groups including links:
-- select Grp.GroupID, Grp.GroupParent, Grp.GroupDescription, ConditionLink.LinkID, ConditionLink.LinkOperator from
-- ( ( Grp INNER JOIN ConditionMember ON ConditionMember.GroupID = Grp.GroupID) INNER JOIN ConditionLink ON ConditionLink.LinkID = ConditionMember.LinkID);
-- get links including objects
-- select ConditionLink.LinkID, ConditionLink.LinkOperator, ConditionLinkMember.ChainID, ConditionObject.ConditionName, ConditionObject.ConditionOperator,
-- ConditionObject.ConditionValue, ConditionObject.ConditionObject, ConditionObject.ConditionDescription, ConditionLinkMember.GroupID from ( ( ConditionLink
-- INNER JOIN ConditionLinkMember ON ConditionLinkMember.LinkID = ConditionLink.LinkID) LEFT JOIN ConditionObject ON ConditionLinkMember.ConditionID = ConditionObject.ConditionID);
INSERT IGNORE INTO ga.ConditionObject (ConditionName, ConditionOperator, ConditionValue, ConditionObject, ConditionDescription, ConditionPeriod)
VALUES ('condi1','>','24','sensor-dht22-temp','Air temp must be higher than 24 for an hour', '3600');
INSERT IGNORE INTO ga.ConditionObject (ConditionName, ConditionOperator, ConditionValue, ConditionObject, ConditionDescription, ConditionPeriod)
VALUES ('condi2','<','24','sensor-dht22-temp','Air temp must be lower than 24 for 15min', '900');
INSERT IGNORE INTO ga.ConditionObject (ConditionName, ConditionOperator, ConditionValue, ConditionObject, ConditionDescription, ConditionPeriod)
VALUES ('condi3','>','50','sensor-dht22-humi','Air humi must be higher than 50 for 90 sec', '90');
INSERT IGNORE INTO ga.ConditionObject (ConditionName, ConditionOperator, ConditionValue, ConditionObject, ConditionDescription, ConditionPeriod)
VALUES ('condi4','=','69.9','sensor-dht22-humi','Air humi must be at than 69.9 for an hour', '3600');

INSERT IGNORE INTO ga.ConditionLink (LinkOperator) VALUES ('and');
INSERT IGNORE INTO ga.ConditionLink (LinkOperator) VALUES ('or');
INSERT IGNORE INTO ga.ConditionLink (LinkOperator) VALUES ('xor');

INSERT IGNORE INTO ga.ConditionLinkMember (GroupID, ConditionID, LinkID) VALUES (null,'1','1');
INSERT IGNORE INTO ga.ConditionLinkMember (GroupID, ConditionID, LinkID) VALUES (null,'2','1');
INSERT IGNORE INTO ga.ConditionLinkMember (GroupID, ConditionID, LinkID) VALUES (null,'2','2');
INSERT IGNORE INTO ga.ConditionLinkMember (GroupID, ConditionID, LinkID) VALUES ('2',null,'2');
INSERT IGNORE INTO ga.ConditionLinkMember (GroupID, ConditionID, LinkID) VALUES (null,'3','3');
INSERT IGNORE INTO ga.ConditionLinkMember (GroupID, ConditionID, LinkID) VALUES (null,'4','3');

INSERT IGNORE INTO ga.ConditionMember (GroupID, LinkID) VALUES ('9','1');
INSERT IGNORE INTO ga.ConditionMember (GroupID, LinkID) VALUES ('9','2');
INSERT IGNORE INTO ga.ConditionMember (GroupID, LinkID) VALUES ('10','3');