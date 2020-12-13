from core.utils.debug import debugger


class Go:
    def __init__(self, object_list: list, member_list: list, member_attribute: str, member_typ: str = None):
        self.object_list = object_list
        self.member_list = member_list
        self.member_attribute = member_attribute
        self.member_typ = member_typ

    def add(self) -> list:
        for group in self.object_list:
            raw_member_data = getattr(group, self.member_attribute)

            if type(raw_member_data) == list:
                group_member_data = []
                for member in raw_member_data:
                    for possible_member in self.member_list:
                        if possible_member.object_id == member:
                            group_member_data.append(possible_member)
                            break

            else:
                # p.e. condition link

                if len(raw_member_data) > 1 and self.member_typ is None:
                    # log error or whatever -> member_typ must be set so we can know which list to process
                    continue

                elif len(raw_member_data) == 1:
                    member_data = list(raw_member_data.values())[0]

                else:
                    member_data = raw_member_data[self.member_typ]

                group_member_data = {}
                for numbered_data, member in member_data.items():
                    for possible_member in self.member_list:
                        if possible_member.object_id == member:
                            group_member_data[numbered_data] = possible_member
                            break

            setattr(group, self.member_attribute, group_member_data)

        return self.object_list
