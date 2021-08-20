from django.apps import AppConfig


class NodesConfig(AppConfig):
    name = 'nodes'
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from . import signals
        return super().ready()
