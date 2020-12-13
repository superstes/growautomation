from core.factory import config


class Go:
    def __init__(self, blueprint, supply_list: list):
        self.blueprint = blueprint
        self.supply_list = supply_list

        self.key_id = config.DB_ALL_KEY_ID
        self.key_name = config.DB_ALL_KEY_NAME
        self.key_desc = config.DB_ALL_KEY_DESCRIPTION
        self.key_setting = config.SUPPLY_KEY_SETTING_DICT
        self.key_member = config.SUPPLY_KEY_MEMBER_DICT
        self.key_member_generic = config.SUPPLY_GENERIC_KEY_MEMBER

        self.member_attribute = config.CORE_MEMBER_ATTRIBUTE
        self.downlink_attribute = config.CORE_DOWNLINK_ATTRIBUTE

    def get_model(self):
        output_list = []

        for data_dict in self.supply_list:
            instance = self.blueprint(
                setting_dict=data_dict[self.key_setting],
                member_list=data_dict[self.key_member][self.key_member_generic],
                object_id=data_dict[self.key_id],
                name=data_dict[self.key_name],
                description=data_dict[self.key_desc],
            )

            output_list.append(instance)

        return output_list

    def get_device(self, parent_list: list, downlink_list: list = None):
        output_list = []

        for data_dict in self.supply_list:
            parent = self._get_parent(parent_list=parent_list, data_dict=data_dict)
            if not parent:
                continue

            if self.downlink_attribute in data_dict:
                downlink = None
                downlink_data = data_dict[self.downlink_attribute]
                if downlink_data is not None:
                    for _ in downlink_list:
                        if _.object_id == data_dict[self.downlink_attribute]:
                            downlink = _

                instance = self.blueprint(
                    parent_instance=parent,
                    setting_dict=data_dict[self.key_setting],
                    object_id=data_dict[self.key_id],
                    name=data_dict[self.key_name],
                    description=data_dict[self.key_desc],
                    downlink=downlink,
                )


            else:
                instance = self.blueprint(
                    parent_instance=parent,
                    setting_dict=data_dict[self.key_setting],
                    object_id=data_dict[self.key_id],
                    name=data_dict[self.key_name],
                    description=data_dict[self.key_desc],
                )

            output_list.append(instance)

        return output_list

    def _get_parent(self, parent_list: list, data_dict: dict):
        for parent in parent_list:
            if data_dict[self.key_id] in getattr(parent, self.member_attribute):
                return parent

        # log error or whatever (no parent instance found)
        return False
