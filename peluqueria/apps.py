from django.apps import AppConfig


class PeluqueriaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'peluqueria'

    def ready(self):
        import peluqueria.signals
