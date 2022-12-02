from django.apps import AppConfig


class FileConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.file"

    def ready(self):
        import apps.file.receivers  # noqa
