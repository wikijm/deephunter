from django.apps import AppConfig


class QmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'qm'

    def ready(self):
        # This will import the signals when the app is ready
        import qm.signals