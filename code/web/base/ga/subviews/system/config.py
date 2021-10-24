from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test

from ...user import authorized_to_read
from ..handlers import Pseudo404
from ...config import shared as config
from ...utils.web import append_return


@user_passes_test(authorized_to_read, login_url=config.DENIED_URL)
def system_config_view(request):
    if 'type' in request.GET:
        config_type = request.GET['type']
        if config_type == 'agent':
            return redirect(append_return(request=request, url='/config/list/systemagent/'))

        elif config_type == 'server':
            return redirect(append_return(request=request, url='/config/update/systemserver/1'))

        else:
            raise Pseudo404(ga={'request': request, 'msg': "Got unsupported system config-type."})

    return render(request, 'system/config.html', context={'request': request, 'title': 'System Settings'})
