# objects
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('sensor-dht22','Air Humidity and Temperature sensor');
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('sensor-ceh','Capacitive earth humidity sensor');
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('sensor-wind','Wind speed and direction sensor');
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('actor-pump','Water pump actor');
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('actor-heat','Air heater actor');
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('actor-win','Window opener actor');
INSERT IGNORE INTO ga.Object (ObjectName, ObjectDescription) VALUES ('controller','Controller system object');

# grp type
INSERT IGNORE INTO ga.GrpType (TypeName, TypeCategory, TypeDescription) VALUES ('input','device','Input device aka sensor');
INSERT IGNORE INTO ga.GrpType (TypeName, TypeCategory, TypeDescription) VALUES ('output','device','Input device aka actor');
INSERT IGNORE INTO ga.GrpType (TypeName, TypeCategory, TypeDescription) VALUES ('controller','core','Controller system');

# groups
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('model-dht22','DHT22 sensor model', '1');
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('model-ceh','Capacitive earth humidity sensor model', '1');
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('model-wind','Wind speed and direction sensor model', '1');
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('model-pump','Water pump actor model', '2');
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('model-heat','Air heater actor model', '2');
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('model-win','Window opener actor model', '2');
INSERT IGNORE INTO ga.Grp (GroupName, GroupDescription, GroupTypeID) VALUES ('system-controller','Controller system group', '3');

# object group member
INSERT IGNORE INTO ga.ObjectGroupMember (GroupID, ObjectID) VALUES ('1','1');
INSERT IGNORE INTO ga.ObjectGroupMember (GroupID, ObjectID) VALUES ('2','2');
INSERT IGNORE INTO ga.ObjectGroupMember (GroupID, ObjectID) VALUES ('3','3');
INSERT IGNORE INTO ga.ObjectGroupMember (GroupID, ObjectID) VALUES ('4','4');
INSERT IGNORE INTO ga.ObjectGroupMember (GroupID, ObjectID) VALUES ('5','5');
INSERT IGNORE INTO ga.ObjectGroupMember (GroupID, ObjectID) VALUES ('6','6');
INSERT IGNORE INTO ga.ObjectGroupMember (GroupID, ObjectID) VALUES ('7','7');

# settingvaluetype
INSERT IGNORE INTO ga.SettingValueType (ValueName, ValueUnit) VALUES ('String','str');
INSERT IGNORE INTO ga.SettingValueType (ValueName, ValueUnit) VALUES ('Bool','file');
INSERT IGNORE INTO ga.SettingValueType (ValueName, ValueUnit) VALUES ('List','list');
INSERT IGNORE INTO ga.SettingValueType (ValueName, ValueUnit) VALUES ('Integer','int');
INSERT IGNORE INTO ga.SettingValueType (ValueName, ValueUnit) VALUES ('JSON array','json');

# settingtype
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('GPIO or downlink pin','connection','4');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Enabled state','enabled','2');
# inputdevices
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Downlink','downlink','1');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Timer','timer','4');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Function','function','1');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Function argument','function_arg','1');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Binary path','function_bin','1');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Unit','unit','1');
# outputdevices
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Reverse','reverse','2');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Reverse type','reverse_type','4');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Reverse function','reverse_function','1');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Reverse function argument','reverse_function_arg','1');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Reverse binary path','reverse_function_bin','1');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('Reverse timer','reverse_timer','4');
# system
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System root path','path_root','1');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System log path','path_log','1');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System backup path','path_backup','1');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System sql server','sql_server','1');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System sql port','sql_port','1');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System sql user','sql_user','1');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System sql password','sql_secret','1');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System sql database','sql_database','1');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System log level','log_level','4');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System debug mode','debug','2');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System security mode','security','2');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System backup','backup','2');
INSERT IGNORE INTO ga.SettingType (TypeDescription, TypeKey, TypeValueID) VALUES ('System timezone','timezone','1');

# object settings
# select * from ObjectSetting INNER JOIN SettingType ON ObjectSetting.SettingTypeID = SettingType.TypeID;
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('1','2','1');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('1','1','21');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('1','3',Null);

INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('2','2','1');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('2','1','3');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('2','3',Null);
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('2','4','500');

INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('3','2','1');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('3','1','12');
INSERT IGNORE INTO ga.ObjectSetting (ObjectID, SettingTypeID, SettingValue) VALUES ('3','3',Null);

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

# group settings
# select * from GrpSetting INNER JOIN SettingType ON GrpSetting.SettingTypeID = SettingType.TypeID;
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('1','2','1');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('1','5','dht22.py');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('1','6',Null);
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('1','7','/usr/bin/python3');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('1','4','60');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('1','8','°C');

INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('2','2','0');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('2','5','ceh.py');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('2','6',Null);
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('2','7','/usr/bin/python3');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('2','4','600');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('2','8','RH');

INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('3','2','1');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('3','5','wind.py');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('3','6',Null);
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('3','7','/usr/bin/python3');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('3','4','900');
INSERT IGNORE INTO ga.GrpSetting (GroupID, SettingTypeID, SettingValue) VALUES ('3','8','km/h');

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
