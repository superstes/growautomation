# helper functions for supply

def converter_lot_list(lot: list, reference_list: list) -> list:
    # converts list of tuples to list of dicts
    data_dict_list = []

    for tup in lot:
        data_dict_list.append(dict(zip(reference_list, tup)))

    return data_dict_list


def filter_dict(data_dict: dict, key_list: list) -> dict:
    new_dict = {}

    for key in key_list:
        if key in data_dict:
            new_dict[key] = data_dict[key]

    return new_dict
