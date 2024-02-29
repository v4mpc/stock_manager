from functools import wraps

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.template import loader
from django.utils.http import urlquote


def permission_required(perm, login_url=None, redirect=REDIRECT_FIELD_NAME):
    """A replacement for django.contrib.auth.decorators.permission_required
    that doesn't ask authenticated users to log in."""

    if not login_url:
        login_url = settings.LOGIN_URL

    def decorator(view_fn):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.has_perm(perm):
                    return view_fn(request, *args, **kwargs)
                t = loader.get_template("403.html")
                # c = RequestContext(request, )
                return HttpResponseForbidden(t.render({"request_path": request.path}))
            path = urlquote(request.get_full_path)
            tup = login_url, redirect, path
            return HttpResponseRedirect("%s?%s=%s" % tup)

        return wraps(view_fn)(_wrapped_view)

    return decorator
