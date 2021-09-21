from django.http import JsonResponse

from ....utils.helper import init_core_config, develop_log
from ....user import authorized_to_write
from ....utils.main import method_user_passes_test

init_core_config()
from core.sock.connect import Client


mapping = {
    'inputobject': 'device.input',
    'outputobject': 'device.output',
    'connectionobject': 'device.connection',
    'inputgroup': 'group.input',
    'outputgroup': 'group.output',
    'connectiongroup': 'group.connection',
}


@method_user_passes_test(authorized_to_write, login_url='/accounts/login/')
def api_sock(request):
    mapping_key = request.POST['type']
    path_id = request.POST['id']
    path = f'ga.core.{mapping[mapping_key]}.{path_id}'
    data = request.POST['do']

    response = Client(path).post(data)

    develop_log(request, output=f"Got socket response '{response}' by executing '{path} = {data}'", level=6)
    return JsonResponse({'response': response})
