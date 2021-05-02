from django.http import JsonResponse

from ....config.site import type_dict
from ...handlers import handler400_api, handler500_api
from ....utils.main import method_user_passes_test
from ....utils.helper import develop_log, get_instance_from_id
from ....user import authorized_to_read

# Ticket #35


class ApiDevice:
    MEASURE_TS_FORMAT = '%H:%M:%S:%f'

    MAX_DATA_POINTS_SHORT = 150
    MAX_DATA_POINTS_MEDIUM = 500
    MAX_DATA_POINTS_LONG = 1000
    MAX_DATA_POINTS_HUGE = 3000

    THIN_OUT_FUNCTIONS = ['avg', 'max', 'min']

    def __init__(self, request):
        self.request = request
        self.data = request.GET
        self.action = None
        self.device_type = None
        self.device_id = None
        self.device_obj = None

    @method_user_passes_test(authorized_to_read, login_url='/accounts/login/')
    def go(self) -> JsonResponse:
        """
        Can execute output devices
        :return: True/False in JsonResponse if actor was executed successfully
        :rtype: JsonResponse
        """

        if self.request.method == 'GET':
            return handler400_api(msg='Only POST method supported')

        else:
            return self.post()

    def post(self):
        try:
            self.action = self.data['do']
            self.device_type = self.data['type']
            self.device_id = self.data['id']
            self.device_obj = type_dict[self.device_type]['model']

        except KeyError:
            return handler500_api(f'One or more parameters (type,id,do) were not supported or are not valid!')

        result = self._execute()
        return JsonResponse(data=result)

    def _execute(self) -> dict:
        # todo: create web/core shared socket codebase for inter-process and network communications
        result = False

        if result is True:
            result_msg = 'The action was successfully executed.'

        else:
            result_msg = 'An error occurred while executing the device.'

        return {'result': result, 'msg': result_msg}
