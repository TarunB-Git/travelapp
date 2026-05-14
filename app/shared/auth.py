from functools import wraps
from flask import redirect, session, url_for


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("access_granted"):
            return redirect(url_for("auth_bp.login"))
        return view_func(*args, **kwargs)

    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("auth_bp.admin_login"))
        return view_func(*args, **kwargs)

    return wrapper
