# point/signals.py
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils.timezone import now
from .models import PPAccessLog
from .views import get_client_ip


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    PPAccessLog.objects.create(
        username=user.username,
        login_time=now(),
        action="Login",
        ip_address=get_client_ip(request),
        used_window="PP system"
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    latest_log = PPAccessLog.objects.filter(
        username=user.username,
        logout_time__isnull=True
    ).order_by('-login_time').first()
    if latest_log:
        latest_log.logout_time = now()
        latest_log.action = "Logout"
        latest_log.used_window = "PP system"
        latest_log.save()
