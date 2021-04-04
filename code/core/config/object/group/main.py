# group objects (used to group/filter devices generically)
#   hold the information of their members

from core.config.object.base import GaBase

# todo: area filtering => Ticket#10


class GaAreaGroup(GaBase):
    def __init__(self, connection_group_list: list, connection_obj_list: list, input_group_list: list, input_obj_list: list,
                 output_group_list: list, output_obj_list: list, nested_list: list, **kwargs):
        super().__init__(**kwargs)
        self.connection_group_list = connection_group_list
        self.connection_obj_list = connection_obj_list
        self.input_group_list = input_group_list
        self.input_obj_list = input_obj_list
        self.output_group_list = output_group_list
        self.output_obj_list = output_obj_list
        self.nested_list = nested_list
