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
def generate_payload(validated_data: dict[str, Any], user: Optional[User]) -> Endpoint:
    """
    Generate a new payload. This is intended to spin up a sibling Docker
    container.
    
    TODO: If another payload for the same agent is currently underway, this build
    is likely to fail due to an image name conflict. I don't know if we want
    to bother fixing this, but it is something to consider. It's not as simple
    as making anonymous images because we still need to copy out of them, and the
    scripts assume a specific name... as does Docker Compose. So I don't know
    if we *can* get away with this.
    
    One option could be to have the install scripts manually change the Docker
    Compose and build scripts' container name at runtime, but isn't that a litte
    flaky?
    """
    # It's assumed all of these are coming from the serializer. Flaky, but
    # it works.
    
    # Extract the fields used throughout the build process and remove them from
    # the dictionary. The remaining fields are passed into the Endpoint constructor
    # as-is.
    agent = Agent.objects.get(id=validated_data.pop('agent'))
    build_args = validated_data.pop('agent_cfg')
    
    # Get the current task.
    task_id = current_task.request.id
    return build_payload(agent, build_args, task_id, user, **validated_data)
    