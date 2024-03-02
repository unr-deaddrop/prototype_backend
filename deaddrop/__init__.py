from .celery import app as celery_app

# init celery app so django tasks can see celery
__all__ = ("celery_app",)