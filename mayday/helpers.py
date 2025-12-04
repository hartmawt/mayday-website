import os
from functools import wraps

SESSION_COOKIE_NAME = os.environ.get("SESSION_COOKIE_NAME", "MAYDAY")


def fetch_session_cookie(func):
    @wraps(func)
    async def wrapper(request):
        cookie = request.cookies.get(SESSION_COOKIE_NAME)
        return await func(request, cookie)
    return wrapper