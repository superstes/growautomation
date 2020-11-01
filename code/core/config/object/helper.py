# helper functions for object initialization

SETTING_DICT_ERROR = "A required setting for instance '%s' (id '%s') of the object '%s' was not defined: %s"
SETTING_DICT_EXCEPTION = KeyError


# dynamic creation of class properties
# used to update child_instance attributes so they are up-to-date to their parent_instance
def set_property(obj, key):
    getter = lambda self: (self.setting_dict[key] if key in self.setting_dict else getattr(self.parent_instance, key))
    setter = lambda self, data: set_property_setter(instance=self, key=key, data=data)

    prop = property(fget=getter, fset=setter)

    exec("obj.%s = prop" % key)


def set_property_setter(instance, key: str, data):
    instance.setting_dict[key] = data


# convert setting_dict key:values to instance attributes
def set_attribute(setting_dict: dict, setting_list: list, instance, obj):
    try:
        for key in setting_list:
            if key not in setting_list:
                raise SETTING_DICT_EXCEPTION("Setting '%s' was not provided" % key)
            else:
                setattr(instance, key, setting_dict[key])

    except SETTING_DICT_EXCEPTION as error_msg:
        raise SETTING_DICT_EXCEPTION(SETTING_DICT_ERROR % (instance.name, instance.object_id, obj, error_msg))


# use value from child, take parent value as fallback
def overwrite_inherited_attribute(child_setting_dict: dict, setting_list: list, child_instance, obj):
    try:
        for key in setting_list:
            if key in child_setting_dict:
                try:
                    if not hasattr(child_instance, key):
                        setattr(child_instance, key, child_setting_dict[key])
                    elif getattr(child_instance, key) == child_setting_dict[key]:
                        pass
                    else:
                        raise AttributeError("Unable to set attribute since it already exists: "
                                             "current value '%s', new value '%s'"
                                             % (getattr(child_instance, key), child_setting_dict[key]))
                except NameError:  # if it already exists as property and should be overwritten
                    setattr(child_instance, key, child_setting_dict[key])
            else:
                set_property(obj=obj, key=key)

    except SETTING_DICT_EXCEPTION as error_msg:
        raise SETTING_DICT_EXCEPTION(SETTING_DICT_ERROR % (child_instance.name, child_instance.object_id,
                                                           obj, error_msg))


# use value from parent, take child value as fallback
def set_inherited_attribute(child_setting_dict: dict, setting_list: list, child_instance, obj):
    try:
        for key in setting_list:
            if hasattr(child_instance.parent_instance, key):
                set_property(obj=obj, key=key)
            elif key in child_setting_dict:
                if not hasattr(child_instance, key):
                    setattr(child_instance, key, child_setting_dict[key])
                elif getattr(child_instance, key) == child_setting_dict[key]:
                    pass
                else:
                    raise AttributeError("Unable to set attribute since it already exists: "
                                         "current value '%s', new value '%s'"
                                         % (getattr(child_instance, key), child_setting_dict[key]))
            else:
                raise AttributeError("Unable to set attribute since it doesn't exist on neither child nor parent!")

    except SETTING_DICT_EXCEPTION as error_msg:
        raise SETTING_DICT_EXCEPTION(SETTING_DICT_ERROR % (child_instance.name, child_instance.object_id,
                                                           obj, error_msg))


# inherit all parent instance attributes listed in setting_list (via properties)
def set_parent_attribute(child_instance, setting_list: list, obj):
    try:
        for key in setting_list:
            set_property(obj=obj, key=key)

    except SETTING_DICT_EXCEPTION as error_msg:
        raise SETTING_DICT_EXCEPTION(SETTING_DICT_ERROR % (child_instance.name, child_instance.object_id,
                                                           obj, error_msg))
