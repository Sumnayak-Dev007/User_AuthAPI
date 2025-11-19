from django.utils.deprecation import MiddlewareMixin

class CaptureIPMiddleware(MiddlewareMixin):
    """
    Middleware to capture user's IP address and make it available on request.
    If the user is authenticated, update their last_login_ip on each request.
    """
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def process_request(self, request):
        ip = self._get_client_ip(request)
        # store on request for views to access
        request._client_ip = ip

        # if user is authenticated, optionally update the last_login_ip
        try:
            user = getattr(request, "user", None)
            if user and user.is_authenticated:
                # Save only when changed to reduce writes
                if getattr(user, "last_login_ip", None) != ip:
                    user.last_login_ip = ip
                    user.save(update_fields=["last_login_ip"])
        except Exception:
            # don't block request if save fails
            pass
