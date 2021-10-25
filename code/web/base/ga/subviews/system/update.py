from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
import requests
from datetime import datetime
from threading import Thread

from core.utils.test import test_tcp_stream

from ...user import authorized_to_read, authorized_to_write
from ..handlers import Pseudo404, Pseudo500
from ...config import shared as config
from ...utils.helper import get_server_config, web_subprocess, develop_log
from ...utils.basic import str_to_list

FORCE_UPDATE = False


@user_passes_test(authorized_to_read, login_url=config.DENIED_URL)
def update_view(request):
    current_version = get_server_config(setting='version')

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
    config_type = request.POST['type']
    clone_directory = f"{config.UPDATE_PATH_CLONE}/{datetime.now().strftime(config.UPDATE_TIMESTAMP)}"
    backup_directory = f"{config.UPDATE_PATH_BACKUP}/{datetime.now().strftime(config.UPDATE_TIMESTAMP)}"

    def start_update_service(clone_dir: str):
        with open(config.UPDATE_CONFIG_FILE, 'w') as file:
            file.write(
                f"METHOD={config_type}\n"
                f"VERSION={update_release}\n"
                f"COMMIT={update_commit}\n"
                f"FORCE={FORCE_UPDATE}\n"
                f"PATH_BACKUP={backup_directory}\n"
                f"PATH_UPDATE={clone_dir}\n"
                f"PATH_CORE={get_server_config(setting='path_core')}\n"
                f"PATH_HOME_CORE={get_server_config(setting='path_home_core')}\n"
                f"PATH_WEB={get_server_config(setting='path_web')}\n"
                f"PATH_WEB_STATIC={get_server_config(setting='path_web_static')}\n"
                f"PATH_HOME_WEB={get_server_config(setting='path_home_web')}\n"
                f"PATH_LOG={get_server_config(setting='path_log')}\n"
                f"SQL_DB={get_server_config(setting='sql_database')}\n"
            )
        web_subprocess(f'sudo systemctl start {config.UPDATE_SERVICE}.service')

    if config_type == 'online':
        update_release = request.POST['release']
        update_commit = request.POST['commit'] if request.POST['commit'] != config.WEBUI_EMPTY_CHOICE else None
        update = False
        update_fail_msg = 'Unable to download source code.'

        if update_commit is not None:
            _clone = web_subprocess(f"git clone https://github.com/superstes/growautomation.git --single-branch {clone_directory}", out_error=True)[1]
            develop_log(request, f"Downloading source-code: \"{_clone}\"")
            if _clone.find('fatal') == -1 and _clone.find('error') == -1:
                _set_commit = web_subprocess(f"cd {clone_directory} && git reset --hard {update_commit}")
                develop_log(request, f"Setting commit: \"{_set_commit}\"")
                if _set_commit.startswith('HEAD is now'):
                    update = True

                else:
                    update_fail_msg = f"Unable to get commit {update_commit}."

        elif float(update_release) != float(current_version):
            _clone = web_subprocess(f"git clone https://github.com/superstes/growautomation.git --depth 1 --branch {update_release} --single-branch {clone_directory}", out_error=True)[1]
            develop_log(request, f"Downloading source-code: \"{_clone}\"")
            if _clone.find('fatal') == -1 and _clone.find('error') == -1:
                update = True

        if update:
            Thread(target=start_update_service(clone_dir=clone_directory)).start()
            return redirect('/system/update/status/')

        else:
            raise Pseudo500(ga={'request': request, 'msg': update_fail_msg})

    elif config_type == 'offline':
        Thread(target=start_update_service(clone_dir=request.POST['path'])).start()
        return redirect('/system/update/status/')

    else:
        raise Pseudo404(ga={'request': request, 'msg': "Got unsupported update method."})


@user_passes_test(authorized_to_read, login_url=config.DENIED_URL)
def update_status_view(request):
    status = 'Running'
    reload_time = 5
    redirect_time = 30
    log_data = str_to_list(web_subprocess(config.LOG_SERVICE_LOG_STATUS % config.UPDATE_SERVICE))

    if log_data[2].find('inactive') != -1:
        reload_time = 0
        redirect_time = 0
        status = 'Finished'

        if log_data[-3].find('Succeeded') != -1:
            status = 'Finished successfully!'

        elif log_data[-3].find('Failed') != -1:
            status = 'Failed!'

    return render(request, 'system/update/status.html', context={
        'request': request, 'title': 'System Update Status', 'log_data': log_data, 'reload_time': reload_time, 'status': status, 'redirect_time': redirect_time,
    })
