from django.apps import AppConfig


class StoreConsultantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cupp.store_consultant'

    def ready(self):
        import cupp.store_consultant.signal
