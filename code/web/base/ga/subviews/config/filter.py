from ...models import BaseDeviceGroupModel


def get_filter_dict(filter_dict: dict, dataset, group_hide_list=None, group_show_list=None) -> dict:
    output_dict = {}

    for typ, data in filter_dict.items():
        any_usable = False
        pretty = data['pretty']

        try:
            obj = data['obj']
        except KeyError:
            field = data['field']
            # todo: add filtering on own fields
            # output_dict[typ] = {'obj': 'self', 'dataset': field, 'pretty': pretty}
            continue

        possible_option_list = obj.objects.all()
        usable_option_list = []

        for option in possible_option_list:
            usable = False

            if isinstance(option, BaseDeviceGroupModel):
                if group_hide_list is not None and option.name in group_hide_list:
                    continue
                if group_show_list is not None and option.name not in group_show_list:
                    continue

            if type(dataset) == dict:
                for data_typ, data_list in dataset.items():
                    for single_set in data_list:
                        if getattr(single_set, typ) == option:
                            usable = True
                            any_usable = True
                            break
            else:
                for single_set in dataset:
                    if getattr(single_set, typ) == option:
                        usable = True
                        any_usable = True
                        break

            if usable:
                usable_option_list.append(option)

        if any_usable:
            output_dict[typ] = {'obj': obj, 'dataset': usable_option_list, 'pretty': pretty}

    return output_dict


def apply_filter(request, dataset) -> tuple:
    if request.method == 'POST':
        filter_acceptable = False
        filter_obj = None
        filter_typ = None

        raw_filter = request.POST.getlist('filter')
        raw_filter_typ = request.POST.getlist('filter_typ')

        for obj, typ in zip(raw_filter, raw_filter_typ):
            if obj == '---------':
                continue

            filter_obj = obj
            filter_typ = typ
            filter_acceptable = True

            break

        if not filter_acceptable:
            return dataset, None

        if type(dataset) == dict:
            output_data = {}
            for data_typ, data_list in dataset.items():
                _list = []

                for obj in data_list:
                    if str(getattr(obj, filter_typ)) == filter_obj:
                        _list.append(obj)

                if len(_list) > 0:
                    output_data[data_typ] = _list
        else:
            output_data = []

            for obj in dataset:
                if str(getattr(obj, filter_typ)) == filter_obj:
                    output_data.append(obj)

        return output_data, filter_obj

    else:
        return dataset, None
