from django.apps import AppConfig

# from django.conf import settings


class AppTaskConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_task"

    def ready(self) -> None:
        from . import signals  # noqa
