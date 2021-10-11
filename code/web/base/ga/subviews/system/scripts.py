from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from os import listdir as os_listdir
from os import path as os_path
from os import remove as os_remove
from datetime import datetime

from ...user import authorized_to_read, authorized_to_write
from ...utils.basic import str_to_list
from ...utils.helper import get_script_dir
from ...forms import SystemScriptForm
from ..handlers import Pseudo404
from ...config.shared import DATETIME_TS_FORMAT


TITLE = 'System scripts'


def _get_script_list(request, typ) -> list:
    script_list = os_listdir(get_script_dir(request, typ=typ))
    return script_list


def _get_script_dict(request, typ) -> dict:
    script_dict = {}
    script_list = _get_script_list(request, typ)
    script_dir = get_script_dir(request, typ=typ)

    for element in script_list:
        ts = os_path.getmtime(f"{script_dir}/{element}")
        ts_hr = datetime.fromtimestamp(ts).strftime(DATETIME_TS_FORMAT)
        script_dict[element] = ts_hr

    return script_dict


@user_passes_test(authorized_to_write, login_url='/denied/')
def _handle_uploaded_file(request, typ: str, upload, name: str):
    script_path = get_script_dir(request, typ=typ)

    with open(f"{script_path}/{name}", 'wb+') as destination:
        for chunk in upload.chunks():
            destination.write(chunk)


@user_passes_test(authorized_to_read, login_url='/denied/')
def ScriptView(request):
    script_type_options = ['Input', 'Output', 'Connection']

    script_type = None
    script_dict = None
    script_dir = None

    if 'script_type' in request.GET:
        script_type = request.GET['script_type']

        if script_type in script_type_options:
            script_dict = _get_script_dict(request, typ=script_type)
            script_dir = get_script_dir(request, typ=script_type)

    return render(request, 'system/script/list.html', context={
        'request': request, 'script_type': script_type, 'script_dict': script_dict, 'script_type_options': script_type_options,
        'script_dir': script_dir, 'title': TITLE,
    })


@user_passes_test(authorized_to_read, login_url='/denied/')
def ScriptChangeView(request):
    script_type_options = ['Input', 'Output', 'Connection']
    form = SystemScriptForm(request.POST, request.FILES)

    if request.method == 'POST':
        script_type = request.POST['script_type']

        if script_type in script_type_options:
            script_name = request.POST['script_name']

            if form.is_valid():
                _handle_uploaded_file(request, typ=script_type, upload=request.FILES['script_file'], name=script_name)

        return redirect(f"/system/script/?script_type={script_type}")

    else:
        if 'script_type' in request.GET and request.GET['script_type'] in script_type_options:
            script_type = request.GET['script_type']
            script_dir = get_script_dir(request, typ=script_type)
        else:
            raise Pseudo404(ga={'request': request, 'msg': 'A script type must be defined.'})

        return render(request, 'system/script/change.html', context={
            'request': request, 'script_type': script_type, 'form': form, 'script_dir': script_dir, 'title': TITLE,
        })


@user_passes_test(authorized_to_write, login_url='/denied/')
def ScriptDeleteView(request):
    script_type_options = ['Input', 'Output', 'Connection']

    if request.method == 'POST':
        script_type = request.POST['script_type']

        if script_type in script_type_options:
            script_name = request.POST['script_name']

            if script_name in _get_script_list(request, typ=script_type):
                os_remove(f"{get_script_dir(request, typ=script_type)}/{script_name}")

        return redirect(f"/system/script/?script_type={script_type}")


@user_passes_test(authorized_to_read, login_url='/denied/')
def ScriptShow(request):
    if 'script_type' in request.GET and 'script_name' in request.GET:
        script_type = request.GET['script_type']
        script_name = request.GET['script_name']
        script_content = None

        script_dir = get_script_dir(request, typ=script_type)

        script_path = f"{script_dir}/{script_name}"

        if os_path.exists(script_path):
            with open(script_path, 'r') as script:
                script_content = str_to_list(data=script.readlines())

    elif 'script_type' in request.GET:
        script_type = request.GET['script_type']
        return redirect(f"/system/script/?script_type={script_type}")

    else:
        return redirect("/system/script/")

    return render(request, 'system/script/show.html', context={
        'request': request, 'script_type': script_type, 'script_content': script_content, 'script_path': script_path, 'title': TITLE,
    })
