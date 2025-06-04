import threading
from django.utils.deprecation import MiddlewareMixin


# Thread-local storage for request data
_thread_locals = threading.local()


class AuditMiddleware(MiddlewareMixin):
    """Middleware to capture request information for audit logging"""

    def process_request(self, request):
        """Store request information in thread-local storage"""
        _thread_locals.request = request
        _thread_locals.user = getattr(request, "user", None)
        _thread_locals.ip_address = self.get_client_ip(request)
        _thread_locals.user_agent = request.META.get("HTTP_USER_AGENT", "")

    def process_response(self, request, response):
        """Clean up thread-local storage"""
        if hasattr(_thread_locals, "request"):
            del _thread_locals.request
        if hasattr(_thread_locals, "user"):
            del _thread_locals.user
        if hasattr(_thread_locals, "ip_address"):
            del _thread_locals.ip_address
        if hasattr(_thread_locals, "user_agent"):
            del _thread_locals.user_agent
        return response

    @staticmethod
    def get_client_ip(request):
        """Get the client IP address from the request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


def get_current_request():
    """Get the current request from thread-local storage"""
    return getattr(_thread_locals, "request", None)


def get_current_user():
    """Get the current user from thread-local storage"""
    user = getattr(_thread_locals, "user", None)
    if user and user.is_authenticated:
        return user
    return None


def get_current_ip():
    """Get the current IP address from thread-local storage"""
    return getattr(_thread_locals, "ip_address", None)


def get_current_user_agent():
    """Get the current user agent from thread-local storage"""
    return getattr(_thread_locals, "user_agent", None)
