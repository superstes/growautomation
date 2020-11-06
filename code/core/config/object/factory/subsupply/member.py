# supplies member list for objects

from core.utils.debug import debugger
from core.config.db.template import SUPPLY_DICT
from core.config.object.factory.helper import factory as factory_helper
from core.config.object.factory.helper import supply as helper


class Go:
    KEY_LIST_KEY = 'key_list'
    ID_KEY = 'id_key'
    MEMBER_GROUP_KEY = 'member_group_key'
    MEMBER_OBJECT_KEY = 'member_object_key'
    MEMBER_ORDER_KEY = 'member_order_key'

    def __init__(self, raw_member_dict: dict, obj_type: str, group_id: int):
        self.raw_member_dict = raw_member_dict
        self.obj_type = obj_type
        self.group_id = group_id
        self.MEMBER_SUPPLY_DICT = SUPPLY_DICT[factory_helper.SUPPLY_MEMBER_KEY][obj_type]
        self.member_dict_list = []

    def get(self) -> (list, dict):
        if self.obj_type == factory_helper.FACTORY_GROUP_KEY:
            return self._simple_list(supply_dict=self.MEMBER_SUPPLY_DICT)

        elif self.obj_type == factory_helper.FACTORY_CONDITION_GROUP_KEY:
            return self._nested_list(sub_list=factory_helper.SUPPLY_MEMBER_CONDITION_GROUP_SUBLIST)

        elif self.obj_type == factory_helper.FACTORY_CONDITION_LINK_KEY:
            return self._twin_list(supply_dict=self.MEMBER_SUPPLY_DICT, ordered=True)

        else:
            # log error or whatever
            pass

    def _get_data_dict(self, supply_dict: dict, raw_lot_search: None):
        if raw_lot_search is not None:
            raw_member_lot = self.raw_member_dict[self.obj_type][raw_lot_search]
        else:
            raw_member_lot = self.raw_member_dict[self.obj_type]

        key_list = supply_dict[self.KEY_LIST_KEY]

        self.member_dict_list = helper.converter_lot_list(
            lot=raw_member_lot,
            reference_list=key_list
        )

    def _simple_list(self, supply_dict: dict) -> list:
        # [ member1, member2 ]

        group_id_key = supply_dict[self.ID_KEY]
        member_list = []

        for member_dict in self.member_dict_list:
            if member_dict[group_id_key] == self.group_id:
                member_list.append(member_dict[group_id_key])

        return member_list

    def _twin_list(self, supply_dict: dict, ordered: bool = False) -> dict:
        # {
        #     objects: [list],
        #     groups: [list]
        # },
        #
        # if ordered:
        # {
        #     groups: {
        #         orderid: member
        #     },
        #     objects: {
        #         orderid: member
        #     },
        # }

        group_id_key = supply_dict[self.ID_KEY]

        member_group_key = supply_dict[self.MEMBER_GROUP_KEY]
        member_object_key = supply_dict[self.MEMBER_OBJECT_KEY]

        if ordered:
            member_order_key = supply_dict[self.MEMBER_ORDER_KEY]

            member_group = {}
            member_object = {}

            for member_dict in self.member_dict_list:
                if member_dict[group_id_key] == self.group_id:
                    if member_dict[member_group_key] is not None:
                        member_group[member_dict[member_order_key]] = int(member_dict[member_group_key])
                    else:
                        member_object[member_dict[member_order_key]] = int(member_dict[member_object_key])

        else:
            member_group = []
            member_object = []

            for member_dict in self.member_dict_list:
                if member_dict[group_id_key] == self.group_id:
                    if member_dict[member_group_key] is not None:
                        member_group.append(int(member_dict[member_group_key]))
                    else:
                        member_object.append(int(member_dict[member_object_key]))

        member_dict = {
            member_group_key: member_group,
            member_object_key: member_object
        }

        return member_dict

    def _nested_list(self, sub_list: list) -> dict:
        # {
        #     subkey1: {
        #             links: [list],
        #             conditiongroups: [list]
        #         },
        #     subkey2: {
        #             objects: [list],
        #             groups: [list]
        #         },
        # }

        output_dict = {}

        for sub_key in sub_list:
            member_sub_supply_dict = self.MEMBER_SUPPLY_DICT[sub_key]

            key_list = member_sub_supply_dict[self.KEY_LIST_KEY]
            raw_member_lot = self.raw_member_dict[factory_helper.FACTORY_CONDITION_GROUP_KEY][sub_key]

            self.member_dict_list = helper.converter_lot_list(
                lot=raw_member_lot,
                reference_list=key_list
            )

            data_dict = self._twin_list(supply_dict=member_sub_supply_dict)

            output_dict[sub_key] = data_dict

        return output_dict
