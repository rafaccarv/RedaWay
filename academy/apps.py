from django.apps import AppConfig


class AcademyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "academy"
    verbose_name = "RedaWay Academy"

    def ready(self):
        from . import signals  # noqa: F401
