# prepares data for factory
#  gets db connection data from config file object
#  gets information on what to load from load module
#  loads data from db

from core.utils.debug import debugger
from core.config.object.data.db import GaDataDb
from core.config.db.template import SUPPLY_DICT
from core.config.object.factory.helper import factory as factory_helper
from core.config.object.factory.helper import supply as helper
from core.config.object.factory.subsupply.obj import Go as SupplyObject


class Go:
    COMMAND_KEY = 'command'

    def __init__(self):
        # loading data from db
        self.database = GaDataDb()
        self.setting_list = []
        self.raw_member_dict = {}

    def get(self) -> dict:
        self._get_member_data()
        self._get_setting_data()
        return self._process()

    def _process(self) -> dict:
        output_dict = {}
        work_dict = {
            factory_helper.FACTORY_OBJECT_KEY,
            factory_helper.FACTORY_GROUP_KEY,
            factory_helper.SUPPLY_GROUPTYPE_KEY,
            factory_helper.FACTORY_CONDITION_SINGLE_KEY,
            factory_helper.FACTORY_CONDITION_GROUP_KEY,
            factory_helper.FACTORY_CONDITION_LINK_KEY
        }

        for key in work_dict:
            if SUPPLY_DICT[key]['setting']:
                setting_data = self.setting_list
            else:
                setting_data = None

            if SUPPLY_DICT[key]['member']:
                member_data = self.raw_member_dict
            else:
                member_data = None

            data = SupplyObject(
                raw_data_lot=self.database.get(SUPPLY_DICT[key][self.COMMAND_KEY]),
                obj_type=key,
                setting_data=setting_data,
                member_data=member_data
            ).get()

            output_dict[key] = data

        self.database.disconnect()

        debugger("config-obj-factory-supply | get | output object:\n'%s'\n\n" % output_dict)

        return output_dict

    def _get_setting_data(self):
        # builds list of setting dicts

        setting_key_list = SUPPLY_DICT[factory_helper.SUPPLY_SETTING_KEY]['key_list']

        raw_lot = self.database.get(SUPPLY_DICT[factory_helper.SUPPLY_SETTING_KEY][self.COMMAND_KEY])

        self.setting_list = helper.converter_lot_list(lot=raw_lot, reference_list=setting_key_list)

    def _get_member_data(self):
        # builds member dict in form like we see it in the db-template
        #   groups with sub-member-lists will be nested

        for key, value_dict in SUPPLY_DICT[factory_helper.SUPPLY_MEMBER_KEY].items():
            if self.COMMAND_KEY in value_dict:
                self.raw_member_dict[key] = self.database.get(value_dict[self.COMMAND_KEY])
            else:
                tmp_dict = {}

                for sub_key, sub_value_dict in value_dict.items():
                    if self.COMMAND_KEY in sub_value_dict:
                        tmp_dict[sub_key] = self.database.get(sub_value_dict[self.COMMAND_KEY])
                    else:
                        # log error or whatever
                        pass

                self.raw_member_dict[key] = tmp_dict
