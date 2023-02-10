from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self, *args, **kwargs):
        super().ready(*args, **kwargs)
        # Import actions so that all the actions are registered appropriately
        import apps.core.actions  # noqa
