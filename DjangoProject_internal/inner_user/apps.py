from django.apps import AppConfig


class InnerUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inner_user'
