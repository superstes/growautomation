from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test

from ....models import ChartGraphModel, ChartDatasetModel, ChartDashboardModel, ObjectInputModel, GroupInputModel, ChartGraphLinkModel, ChartDatasetLinkModel
from ...handlers import handler400_api
from ....utils.helper import get_instance_from_id
from ....user import authorized_to_read
from ..data.main import ApiData


@user_passes_test(authorized_to_read, login_url='/api/denied/')
def ApiChart(request):
    if request.method == 'GET':
        if 'id' not in request.GET:
            return handler400_api(msg='Need to specify id')

        if 'type' not in request.GET:
            return handler400_api(msg='Need to specify type')

        try:
            chart_id = int(request.GET['id'])

        except ValueError:
            return handler400_api(msg="Need to specify a valid id; got '%s'" % request.GET['id'])

        chart_type = request.GET['type']

        if chart_type == 'graph':
            typ = ChartGraphModel

        elif chart_type == 'dataset':
            typ = ChartDatasetModel

        elif chart_type == 'dbe':
            typ = ChartDashboardModel

        else:
            return handler400_api(msg="Specified type '%s' not found" % chart_type)

        chart_obj = get_instance_from_id(typ=typ, obj=chart_id)

        if chart_obj is None:
            return handler400_api(msg="No object found with id '%s'; available: '%s'" % (chart_id, [_.id for _ in list(typ.objects.all())]))

        data_dict = {}
        input_obj = None

        for field in chart_obj.field_list:
            value = getattr(chart_obj, field)

            if type(value) in [ObjectInputModel, GroupInputModel]:
                input_obj = value
                value = value.id

            elif field == 'options_json' and value == 'None':
                value = None

            data_dict[field] = value

        if chart_type == 'dataset':
            if input_obj is None:
                return handler400_api(msg='No data found')

            filter_params = None

            if data_dict['period'] is not None and data_dict['period_data'] is not None:
                filter_params = {'period': data_dict['period'], 'period_data': data_dict['period_data']}

            else:
                if data_dict['start_ts'] is not None and data_dict['stop_ts'] is not None:
                    filter_params = {'start_ts': data_dict['start_ts'], 'stop_ts': data_dict['stop_ts']}

                elif data_dict['start_ts'] is not None:
                    filter_params = {'start_ts': data_dict['start_ts']}

            if filter_params is None:
                return handler400_api(msg='No suitable data filter found')

            # todo: input group support => Ticket#15
            api_params = {'input_id': input_obj.id, 'input_type': ObjectInputModel}
            api_params.update(filter_params)

            data_dict['data'] = ApiData(request, **api_params, return_dict=True).go()

            if type(data_dict['data']) == JsonResponse:
                return data_dict['data']

        elif chart_type == 'dbe':
            dataset_list = []

            for link in ChartDatasetLinkModel.objects.all():
                if link.group.id == chart_id:
                    dataset_list.append(link.obj.id)

            graph_id = None

            for link in ChartGraphLinkModel.objects.all():
                if link.group.id == chart_id:
                    graph_id = link.obj.id

            data_dict['dataset'] = dataset_list
            data_dict['graph'] = graph_id

        return JsonResponse(data={
            'chart_id': int(chart_id), 'data_dict': data_dict,
        })

    else:
        return handler400_api(msg='Only GET method supported')
