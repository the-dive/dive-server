import importlib.util
from .celery import app as celery_app  # noqa:F401

__all__ = ["celery_app"]

mypy_package = importlib.util.find_spec("mypy")
if mypy_package:
    from .checks import mypy  # noqa:F401
