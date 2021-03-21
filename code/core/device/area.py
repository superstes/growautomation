# function to get all nested areas and filter a list of devices on it


def _subarea_nesting(areas: list) -> list:
    subareas = []
    for area in areas:
        if area.nested_list is not None:
            subareas.extend(_subarea_nesting(areas=area.nested_list))

        subareas.append(area)

    return subareas


def _get_members(areas: list) -> list:
    # todo: move to shared_vars
    attr_list = ['connection_group_list', 'connection_obj_list', 'input_group_list', 'input_obj_list', 'output_group_list', 'output_obj_list']
    members = []

    for area in _subarea_nesting(areas=areas):
        for attr in attr_list:
            member_list = getattr(area, attr)
            if member_list is not None:
                members.extend(member_list)

    return members


def area_filter(areas: list, devices: list) -> list:
    if areas is None or len(areas) == 0:
        return devices

    filtered_devices = devices.copy()
    members = _get_members(areas=areas)

    for device in devices:
        if 'downlink' in device:
            if device['downlink'] not in members or device['device'] not in members:
                filtered_devices.pop(device)

        elif device['device'] not in members:
            filtered_devices.pop(device)

    return filtered_devices
