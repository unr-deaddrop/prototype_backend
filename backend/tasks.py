"""
All shared Celery tasks.
"""
from typing import Any, Optional
import time
import logging

from celery import shared_task, current_task

from backend.models import Agent, Endpoint
from backend.payloads import build_payload
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

@shared_task
def generate_payload(
    build_args: dict[str, Any], 
    agent: Agent, 
    user: Optional[User]
) -> Endpoint:
    """
    Generate a new payload. This spins up a sibling docker container.
    """
    task_id = current_task.request.id
    return build_payload(build_args, agent, task_id, user)
    