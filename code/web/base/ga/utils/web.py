from urllib.parse import urlencode

from django.shortcuts import redirect


def get_form_prefill(request):
    form_prefill = {}

    for key, value in request.GET.items():
        if value is not None:
            form_prefill[key] = value

    return form_prefill


def get_url_divider(url: str):
    if url.endswith('/'):
        return ''
    else:
        return '/'


def get_client_ip(request):
    ip_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_forwarded:
        client_ip = ip_forwarded.split(',')[0]
    else:
        client_ip = request.META.get('REMOTE_ADDR')

    censored_client_ip = f"{client_ip.rsplit('.', 1)[0]}.0"

    return censored_client_ip


def get_as_string(get_params: dict, add: bool = False) -> str:
    if add:
        return str(urlencode(get_params))

    return f"?{urlencode(get_params)}"


def redirect_if_hidden(request, target: str):
    redirect_url = f"/config/list/{ target }/{ get_as_string(request.GET) }"

    return redirect(redirect_url)


def append_to_url(url: str, append: dict) -> str:
    append = urlencode(append)

    if url.find('?') != -1:
        return f'{url}&{append}'

    return f'{url}?{append}'
