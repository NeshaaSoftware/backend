import re

from django.shortcuts import redirect


class AddTrailingSlashMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        should_redirect = (
            path != "/"
            and not path.endswith("/")
            and not re.match(r"^.*\?.*$", path)
            and not re.match(r"^\/(static\/.*|media\/.*|favicon\.ico)", path)
        )

        if should_redirect:
            return redirect(path + "/", permanent=True)
        return self.get_response(request)
