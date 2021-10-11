from functools import wraps
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import resolve_url
from django.contrib.auth.views import logout_then_login


def logout_check(request, default, hard_logout: bool = False):
    if request.method == 'POST':
        if ('logout' in request.POST and int(request.POST['logout']) == 1) or hard_logout:
            return logout_then_login(request)

    return default


def method_user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    modified version of "django.contrib.auth.decorators.user_passes_test" for use on class methods
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(instance, *args, **kwargs):
            if test_func(instance.request.user):
                return view_func(instance, *args, **kwargs)
            path = instance.request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = instance.request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view
    return decorator
