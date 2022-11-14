from multiprocessing import allow_connection_pickling
from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve, reverse
from django.urls.conf import path


def check_request_allowed(request, allow_urls, allow_apps):
    path_data = resolve(request.path_info)

    url_allowed = False

    for url_name in allow_urls:
        url_allowed = url_allowed or (path_data.url_name == url_name)
        url_allowed = url_allowed or (request.path_info.startswith(url_name))

    if len(path_data.namespaces) > 0:
        url_allowed = url_allowed or (
            f"{path_data.namespaces[0]}:{path_data.url_name}" in allow_urls
        )

    for app_name in allow_apps:
        url_allowed = url_allowed or (app_name in path_data.app_names)

    return url_allowed


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.login_url = settings.LOGIN_URL
        self.open_urls = [self.login_url] + getattr(settings, "OPEN_URLS", [])
        self.open_apps = getattr(settings, "OPEN_APPS", [])

        self.std_urls = getattr(settings, "STD_URLS", [])
        self.std_apps = getattr(settings, "STD_APPS", [])
        # One-time configuration and initialization.

    def __call__(self, request):
        url_is_open = check_request_allowed(request, self.open_urls, self.open_apps)
        url_is_std = check_request_allowed(request, self.std_urls, self.std_apps)

        if url_is_open:
            # pass through wihtout checking auth
            return self.get_response(request)
        else:
            # knock out unauthenticated and inactive users
            if not request.user.is_authenticated or not request.user.is_active:
                return redirect(reverse(self.login_url) + "?next=" + request.path)

            # check standard user
            if url_is_std:
                return self.get_response(request)
            else:
                if not request.user.is_staff:
                    return redirect(reverse(self.login_url) + "?next=" + request.path)
                else:
                    return self.get_response(request)
