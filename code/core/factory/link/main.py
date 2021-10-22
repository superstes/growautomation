# creates links between objects

from core.factory import config
from core.utils.debug import log
from core.config.object.base import GaBase


class Go:
    LINK_TARGET_TYPES = (GaBase, dict, list, set, type(None))

    def __init__(self, factory_data: dict, supply_data: dict):
        self.factory_data = factory_data
        self.supply_data = supply_data

    def set(self) -> None:
        """
        Checks what links to build and starts the methods accordingly.

        :return: None
        """
        log(f'Linking objects', level=8)
        log(f'Building one-to-many links', level=8)

        for key, otm_config in config.MEMBERS.items():
            log(f'Building member links for type \"{key}\"', level=8)
            self._one_to_many(instances=self.factory_data[key], otm_config=otm_config)

        log(f'Building one-to-one links', level=8)

        for key, oto_config in config.LINKS.items():
            log(f'Building one-to-one links for type \"{key}\"', level=8)

            for field, _oto_config in oto_config.items():
                if type(_oto_config) == list:
                    log(f'Processing complex one-to-one linking of type \"{key}\" with options: \"{[key for key in oto_config.keys()]}\"', level=8)
                    self._one_to_one_options(instances=self.factory_data[key], oto_config=oto_config, type_key=key)

                else:
                    log(f'Processing simple one-to-one linking of type \"{key}\"', level=8)
                    self._one_to_one(instances=self.factory_data[key], oto_config=oto_config)

    def _one_to_many(self, instances: list, otm_config: dict) -> None:
        """
        Builds a member-list/dict to link to the current instance.
        It supports lists and numbered dicts (key=number,value=member)

        :param instances: The currently processed object instances - only one type at a time
        :param otm_config: Link config sub-dict as configured in factory config file
        :return: None
        """

        for instance in instances:
            for member_attr, search_key in otm_config.items():
                raw_member_data = getattr(instance, member_attr)
                possible_members = self.factory_data[search_key]

                if type(raw_member_data) == list:
                    log(f'Building member list for instance \"{instance}\"', level=8)
                    members = []
                    for member in raw_member_data:
                        for possible_member in possible_members:
                            if possible_member.object_id == member:
                                members.append(possible_member)
                                break

                else:
                    # numbered members -> p.e. condition link
                    log(f'Building numbered member dict for instance \"{instance}\"', level=8)

                    members = {}
                    for numbered_data, member in raw_member_data.items():
                        for possible_member in possible_members:
                            if possible_member.object_id == member:
                                members[numbered_data] = possible_member
                                break

                log(f'Object \"{instance}\" has the following members for attribute \"{member_attr}\": \"{members}\"', level=8)
                setattr(instance, member_attr, members)

    def _one_to_one(self, instances: list, oto_config: dict) -> None:
        """
        Links two object instances.
        Either links them via object_id [config=simple key:value pair] or some custom mapping [config=dict]

        :param instances: The currently processed object instances - only one type at a time
        :param oto_config: Link config sub-dict as configured in factory config file
        :return: None
        """

        for key, link_config in oto_config.items():
            if type(link_config) == dict:
                # this instance is a member of the targets member list
                search_key = link_config[config.LINK_KEY_SEARCH_KEY]
                search_attr = link_config[config.LINK_KEY_SEARCH_ATTR]
                set_attr = link_config[config.LINK_KEY_SET_ATTR]

                for instance in instances:
                    for target_instance in self.factory_data[search_key]:
                        if instance in getattr(target_instance, search_attr):
                            log(f'Object \"{instance}\" has the following link target for attribute \"{set_attr}\": \"{target_instance}\"', level=8)
                            setattr(instance, set_attr, target_instance)
                            break

                    self._check(attribute=set_attr, instance=instance)

            else:
                # simple id to id link
                search_key = link_config
                search_attr = config.CORE_ID_ATTRIBUTE
                set_attr = key

                for instance in instances:
                    try:
                        # get the raw id of the target object
                        to_compare = int(getattr(instance, set_attr))

                    except TypeError:
                        if set_attr != 'downlink':
                            log(f'Unable to get value for attribute \"{set_attr}\" from object \"{instance}\"', level=5)

                        continue

                    for target_instance in self.factory_data[search_key]:
                        if getattr(target_instance, search_attr) == to_compare:
                            log(f'Object \"{instance}\" has the following link target for attribute \"{set_attr}\": \"{target_instance}\"', level=8)
                            setattr(instance, set_attr, target_instance)
                            break

                    self._check(attribute=set_attr, instance=instance)

    def _one_to_one_options(self, instances: list, oto_config: dict, type_key: str) -> None:
        """
        Links two object instances if there is the option to choose one of X target types.
        Will check which target type is configured, find and link it [only object_id linking supported]

        Example:
        - condition match can be linked to one of [input object, input model, special match]
        - one will/must be linked

        :param instances: The currently processed object instances - only one type at a time
        :param oto_config: Link config sub-dict as configured in factory config file
        :param type_key: The type that is currently processed - needed to get the correct raw data from the supply data
        :return: None
        """

        for instance in instances:
            _id = getattr(instance, config.CORE_ID_ATTRIBUTE)
            raw_instance_data = [data_dict for data_dict in self.supply_data[type_key].values() if int(data_dict['id']) == _id][0]

            for set_attr, options in oto_config.items():
                for option in options:
                    search_attr = option[config.LINK_KEY_SEARCH_ATTR]
                    query_attr = config.CORE_ID_ATTRIBUTE
                    search_key = option[config.LINK_KEY_SEARCH_KEY]

                    if raw_instance_data[search_attr] is not None:
                        to_compare = int(raw_instance_data[search_attr])

                        for target_instance in self.factory_data[search_key]:
                            if getattr(target_instance, query_attr) == to_compare:
                                setattr(instance, set_attr, target_instance)
                                log(f'Object \"{instance}\" has the following link target for attribute \"{set_attr}\": \"{target_instance}\"', level=8)
                                break

                        break

                self._check(attribute=set_attr, instance=instance)

    def _check(self, attribute: str, instance) -> None:
        """
        Will check if the link was successfully created.
        Else it will log an error.

        :param attribute: Instance attribute that should be checked
        :param instance: Instance to check
        :return: None
        """
        to_check = getattr(instance, attribute)
        if not isinstance(to_check, self.LINK_TARGET_TYPES):
            log(f'Failed to create \"{attribute}\" link for object \"{instance}\"', level=4)
