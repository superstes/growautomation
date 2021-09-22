from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from ....utils.helper import init_core_config, develop_log
from ....utils.main import append_to_url
from ....user import authorized_to_write

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


@login_required
@user_passes_test(authorized_to_write, login_url='/accounts/login/')
def api_sock(request):
    mapping_key = request.POST['type']
    path_id = request.POST['id']
    path = f'ga.core.{mapping[mapping_key]}.{path_id}'
    data = request.POST['do']

    response = Client(path).post(data)

    develop_log(request, output=f"Got socket response '{response}' by executing '{path} = {data}'", level=6)

    if request.META['HTTP_REFERER'].find('/config/') != -1:
        result = 'Action failed!'

        if type(response) == bool and response is True:
            result = 'Action succeeded!'

        elif type(response) == dict:
            result = f"Action succeeded - got data: {response['data']}"

        return redirect(append_to_url(url=request.META['HTTP_REFERER'], append={'response': result}))

    return JsonResponse({'response': response})
