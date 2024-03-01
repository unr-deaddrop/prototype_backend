from pathlib import Path

from django.apps import AppConfig
from django.conf import settings

class BackendConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend"
    
    def ready(self):
        # Generate the configured package folders if they do not already exist, 
        # which are not committed to the repo by default.
        Path(settings.AGENT_PACKAGE_DIR).mkdir(parents=True, exist_ok=True)
        Path(settings.PROTOCOL_PACKAGE_DIR).mkdir(parents=True, exist_ok=True)
