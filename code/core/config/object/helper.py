# helper functions for object initialization

from core.utils.debug import censor

SETTING_DICT_ERROR = "The required setting %s for instance \"%s\" (id \"%s\") of the object \"%s\" was not defined " \
                     "in its settings: \"%s\""
SETTING_DICT_EXCEPTION = KeyError


def set_property(obj, key: str) -> None:
    """
    Dynamically creates properties for classes (not instances of classes)
    Checks if property is already set and applies getter/setter if not so
    Used to update child-instance attributes so they are up-to-date to their parent-instance

    :param obj:
    :param key:
    :return:
    """

    try:
        _ = getattr(obj, key)
        if isinstance(_, property):
            return None

        from core.config.object.base import GaBase
        if key in GaBase.reserved:
            return None

    except AttributeError:
        pass

    def _getter(self):
        if key in self.setting_dict:
            return self.setting_dict[key]

        # allow parent instance to be set later in the factory-process
        if self.parent_instance is None:
            return None

        return getattr(self.parent_instance, key)

    _property = property(fget=_getter)
    exec(f"obj.{key} = _property")


def set_attribute(setting_dict: dict, setting_list: list, instance, obj) -> None:
    """
    convert setting_dict key:values to instance attributes

    :param setting_dict:
    :param setting_list:
    :param instance:
    :param obj:
    :return:
    """
    try:
        for key in setting_list:
            if key not in setting_list:
                raise SETTING_DICT_EXCEPTION(f"Setting \"{key}\" was not provided")
            else:
                setattr(instance, key, setting_dict[key])

    except SETTING_DICT_EXCEPTION as error_msg:
        raise SETTING_DICT_EXCEPTION(censor(SETTING_DICT_ERROR % (error_msg, instance.name, instance.object_id, obj, setting_dict)))


def overwrite_inherited_attribute(child_setting_dict: dict, setting_list: list, child_instance, obj) -> None:
    """
    use value from child, take parent value as fallback

    :param child_setting_dict:
    :param setting_list:
    :param child_instance:
    :param obj:
    :return:
    """
    try:
        for key in setting_list:
            if key in child_setting_dict:
                try:
                    if not hasattr(child_instance, key):
                        setattr(child_instance, key, child_setting_dict[key])
                    elif getattr(child_instance, key) == child_setting_dict[key]:
                        pass
                    else:
                        raise AttributeError(censor(f"Unable to set attribute since it already exists: current value \"{getattr(child_instance, key)}\", new value \"{child_setting_dict[key]}\""))
                except NameError:  # if it already exists as property and should be overwritten
                    setattr(child_instance, key, child_setting_dict[key])
            else:
                set_property(obj=obj, key=key)

    except SETTING_DICT_EXCEPTION as error_msg:
        raise SETTING_DICT_EXCEPTION(censor(SETTING_DICT_ERROR % (error_msg, child_instance.name, child_instance.object_id, obj, child_setting_dict)))


def set_inherited_attribute(child_setting_dict: dict, setting_list: list, child_instance, obj) -> None:
    """
    use value from parent, take child value as fallback

    :param child_setting_dict:
    :param setting_list:
    :param child_instance:
    :param obj:
    :return:
    """
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
                    raise AttributeError(censor(f"Unable to set attribute since it already exists: current value \"{getattr(child_instance, key)}\", new value \"{child_setting_dict[key]}\""))
            else:
                raise AttributeError("Unable to set attribute since it doesn't exist on neither child nor parent!")

    except SETTING_DICT_EXCEPTION as error_msg:
        raise SETTING_DICT_EXCEPTION(censor(SETTING_DICT_ERROR % (error_msg, child_instance.name, child_instance.object_id, obj, child_setting_dict)))


def set_parent_attribute(child_instance, setting_list: list, obj) -> None:
    """
    inherit all parent instance attributes listed in setting_list (via properties)

    :param child_instance:
    :param setting_list:
    :param obj:
    :return:
    """
    try:
        for key in setting_list:
            set_property(obj=obj, key=key)

    except SETTING_DICT_EXCEPTION as error_msg:
        raise SETTING_DICT_EXCEPTION(censor(SETTING_DICT_ERROR % (error_msg, child_instance.name, child_instance.object_id, obj, setting_list)))
