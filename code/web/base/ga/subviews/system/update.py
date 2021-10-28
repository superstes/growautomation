from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
import requests
from threading import Thread

from core.utils.test import test_tcp_stream

from ...user import authorized_to_read, authorized_to_write
from ..handlers import Pseudo404
from ...config import shared as config
from ...utils.helper import get_server_config, web_subprocess
from ...utils.basic import str_to_list

FORCE_UPDATE = False


@user_passes_test(authorized_to_read, login_url=config.DENIED_URL)
def update_view(request):
    current_version = get_server_config(setting='version')
    # todo: let user supply 'migrate-db' and other flags

    if request.method == 'GET':
        if 'type' in request.GET:
            config_type = request.GET['type']

            if config_type == 'online':
                releases = []
                online = test_tcp_stream(host='github.com', port=443)

                if online:
                    for tag in requests.get('https://api.github.com/repos/superstes/growautomation/tags').json():
                        version = tag['name']

                        if float(version) > float(current_version):
                            releases.append(version)

                return render(request, 'system/update/online.html', context={
                    'request': request, 'title': 'System Update', 'releases': releases, 'current_version': current_version, 'online': online, 'config': config,
                })

            elif config_type == 'offline':
                return render(request, 'system/update/offline.html', context={'request': request, 'title': 'System Update', 'config': config})

            else:
                raise Pseudo404(ga={'request': request, 'msg': "Got unsupported update method."})

        return render(request, 'system/update/method.html', context={'request': request, 'title': 'System Update'})

    elif request.method == 'POST':
        if 'type' in request.POST:
            return update_start(request=request, current_version=current_version)

        raise Pseudo404(ga={'request': request, 'msg': "Got no update method."})


@user_passes_test(authorized_to_write, login_url=config.DENIED_URL)
def update_start(request, current_version):
    try:
        update_method = request.POST['type']
        repo_path = request.POST['path'] if 'path' in request.POST else None

        if update_method not in ['online', 'offline']:
            raise KeyError('Got unsupported update method')

        update_release = request.POST['release']
        update_commit = None

        if request.POST['commit'] != config.WEBUI_EMPTY_CHOICE:
            update_type = 'commit'
            update_commit = request.POST['commit']

        elif request.POST['release'] not in config.NONE_RESULTS:
            update_type = 'release'

            # checking if release version is valid (if possible for current scope)
            if float(update_release) <= float(current_version):
                raise KeyError('Got unsupported target version!')

        else:
            update_type = 'none'

        with open(config.UPDATE_CONFIG_FILE, 'w') as file:
            file.write(
                f"ga_update_type={update_type}\n"
                f"ga_update_method={update_method}\n"
                f"ga_update_release={update_release}\n"
                f"ga_update_release_current={current_version}\n"
                f"ga_update_commit_current={get_server_config(setting='version_detail')}\n"
                f"ga_update_commit={update_commit}\n"
                f"ga_update_path_repo={repo_path}\n"
                f"ga_update_path_core={get_server_config(setting='path_core')}\n"
                f"ga_update_path_web={get_server_config(setting='path_web')}\n"
                f"ga_update_path_web_static={get_server_config(setting='path_web_static')}\n"
                f"ga_update_path_log={get_server_config(setting='path_log')}\n"
            )

        def start():
            web_subprocess(f'sudo systemctl start {config.UPDATE_SERVICE}.service')

        Thread(target=start()).start()
        return redirect('/system/update/status/')

    except KeyError as error:
        raise Pseudo404(ga={'request': request, 'msg': str(error)})


@user_passes_test(authorized_to_read, login_url=config.DENIED_URL)
def update_status_view(request):
    status = 'Running'
    reload_time = 5
    redirect_time = 30
    log_data = str_to_list(web_subprocess(f"{config.LOG_SERVICE_LOG_STATUS % config.UPDATE_SERVICE} | grep ' {config.UPDATE_SERVICE}\\['"))
    update_status = web_subprocess(command=f"systemctl is-active {config.UPDATE_SERVICE}.service")

    if update_status.find('activating') == -1:
        reload_time = 0
        redirect_time = 0
        status = 'Finished with unidentified result'

        for line in log_data[-6:-2]:
            if line.find('Update failed') != -1:
                status = 'Failed'
                break

            elif line.find('Update succeeded') != -1:
                status = 'Finished successfully'
                break

        if status != 'Failed':
            if log_data[-1].find('failed=0') == -1:
                status = 'Finished with errors'

            elif log_data[-1].find('failed=0') != -1:
                status = 'Finished successfully'

    return render(request, 'system/update/status.html', context={
        'request': request, 'title': 'System Update Status', 'log_data': log_data, 'reload_time': reload_time, 'status': status, 'redirect_time': redirect_time,
    })
