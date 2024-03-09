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
    validated_data: dict[str, Any], user_id: Optional[int]
) -> Endpoint:
    """
    Generate a new payload. This is intended to spin up a sibling Docker
    container in a temporary folder with a random container name.

    Note that the keyword arguments `payload_file` and `connections` are ignored
    when generating physical payloads through this task.
    """
    # It's assumed all of these are coming from the serializer. Flaky, but
    # it works.

    # Extract the fields used throughout the build process and remove them from
    # the dictionary. The remaining fields are passed into the Endpoint constructor
    # as-is.
    agent = Agent.objects.get(id=validated_data.pop("agent"))
    user = None
    if user_id:
        user = User.objects.get(id=user_id)
    build_args = validated_data.pop("agent_cfg")

    # Get the current task.
    task_id = current_task.request.id
    return build_payload(agent, build_args, task_id, user, **validated_data)
