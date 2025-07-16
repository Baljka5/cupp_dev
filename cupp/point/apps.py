# point/apps.py
from django.apps import AppConfig

class PointConfig(AppConfig):
    name = 'cupp.point'

    def ready(self):
        import cupp.point.signal
