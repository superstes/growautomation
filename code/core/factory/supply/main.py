# from core.utils.debug import debugger
from core.config.object.data.db import GaDataDb
from core.factory.supply import config as supply_config
from core.factory import config as factory_config
from core.utils.crypto import AESCipher
from core.utils.key import get as get_key

crypto = AESCipher(get_key())


class Go:
    SUPPLY_SQL_DICT = supply_config.supply_sql_dict
    SQL_DEFAULTS = SUPPLY_SQL_DICT['*']
    
    def __init__(self):
        self.database = GaDataDb()
        
    def get(self) -> dict:
        data_dict = {}

        for typ, config in self.SUPPLY_SQL_DICT.items():
            if typ == '*':
                continue

            _data_dict = self._get_data(config=config, typ=typ)
            data_dict[typ] = _data_dict

        # self._test(data_dict=data_dict)

        return data_dict

    def _get_data_list(self, query_typ: str, config: dict) -> list:
        query = config['queries'][query_typ]
    
        fields = self.SQL_DEFAULTS['fields']['*'] + config['fields'][query_typ]
        data_tuple_list = self.database.get(query)
    
        data_list = []

        if data_tuple_list is not None:
            for data_tuple in data_tuple_list:
                _data = dict(zip(fields, data_tuple))
                data_list.append(self._decrypt(data_dict=_data))
    
        return data_list

    @staticmethod
    def _decrypt(data_dict: dict) -> dict:
        output_dict = {}

        for key, value in data_dict.items():
            if key in factory_config.DB_ENCRYPTED_SETTING_LIST:
                output_dict[key] = crypto.decrypt(str.encode(value))

            else:
                output_dict[key] = value

        return output_dict

    @staticmethod
    def _add_settings(config: dict, query_typ: str, data_list: list) -> list:
        if 'setting_fields' in config and query_typ in config['setting_fields']:
            setting_dict = {}
    
            for data_dict in data_list:
                for field in config['setting_fields'][query_typ]:
                    setting_dict[field] = data_dict.pop(field)
    
                data_dict[factory_config.SUPPLY_KEY_SETTING_DICT] = setting_dict
    
        return data_list

    def _add_members(self, config: dict, data_list: list) -> list:
        query_typ = 'member'
        id_key = factory_config.DB_ALL_KEY_ID
        supply_member_key = factory_config.SUPPLY_KEY_MEMBER_DICT

        for query_key in config['queries'].keys():

            if query_key.find(query_typ) != -1:
                group_key = config[query_typ][query_key]['group']
                member_key = config[query_typ][query_key]['member']
                member_list = self._get_data_list(query_typ=query_key, config=config)

                for data_dict in data_list:
                    _list = []

                    for member_dict in member_list:
                        if member_dict[member_key] is None:
                            continue

                        if data_dict[id_key] == member_dict[group_key]:
                            _list.append(member_dict[member_key])

                    if supply_member_key in data_dict:
                        data_dict[supply_member_key].update({query_key: _list})
                    else:
                        data_dict[supply_member_key] = {query_key: _list}
    
        return data_list

    def _add_numbered_members(self, config: dict, data_list: list) -> list:
        query_typ = 'member'
        id_key = factory_config.DB_ALL_KEY_ID
        supply_member_key = factory_config.SUPPLY_KEY_MEMBER_DICT

        for query_key in config['queries'].keys():

            if query_key.find(query_typ) != -1:
                setting_list = config['setting_fields'][query_key]

                if len(setting_list) == 1:
                    numbered_key = setting_list[0]
                else:
                    # log error or whatever ?
                    numbered_key = False

                group_key = config[query_typ][query_key]['group']
                member_key = config[query_typ][query_key]['member']
                member_list = self._get_data_list(query_typ=query_key, config=config)

                for data_dict in data_list:
                    _dict = {}  # needed for order of condition link members

                    for member_dict in member_list:
                        if member_dict[member_key] is None:
                            continue

                        if data_dict[id_key] == member_dict[group_key]:
                            if numbered_key:
                                numbered_data = member_dict[numbered_key]
                            else:
                                numbered_data = len(_dict) + 1

                            _dict[numbered_data] = member_dict[member_key]

                    if supply_member_key in data_dict:
                        data_dict[supply_member_key].update({query_key: _dict})
                    else:
                        data_dict[supply_member_key] = {query_key: _dict}

        return data_list

    def _get_data(self, config: dict, typ: str) -> list:
        query_typ = 'base'
    
        data_list = self._get_data_list(query_typ=query_typ, config=config)
        data_list = self._add_settings(data_list=data_list, config=config, query_typ=query_typ)
        if typ == factory_config.KEY_OBJECT_CONDITION_LINK:
            data_list = self._add_numbered_members(data_list=data_list, config=config)
        else:
            data_list = self._add_members(data_list=data_list, config=config)
    
        return data_list

    @staticmethod
    def _test(data_dict: dict):
        print("#########################\nOUTPUT\n\n")
        for typ, results in data_dict.items():
            print("####\nTYP: %s" % typ)
            for data in results:
                print(data)
        print("#########################\n\nEND OUTPUT")

