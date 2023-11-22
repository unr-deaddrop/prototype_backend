import uuid
import datetime

from django.contrib.auth.models import User, Group
from django.db import models
from django.urls import reverse


class Agent(models.Model):
    name = models.CharField(
        max_length=100, unique=True, help_text="Human-readable name for the agent."
    )
    # Local path to agent definition root
    definition_path = models.FilePathField()

    def get_absolute_url(self):
        return reverse("agent-detail", args=[str(self.id)])


class Protocol(models.Model):
    # Human-readable name
    name = models.CharField(
        max_length=100, unique=True, help_text="Human-readable name for the protocol."
    )
    # Local path to protocol handler binary (may make sense as a FileField?)
    handler_path = models.FilePathField()

    def get_absolute_url(self):
        return reverse("protocol-detail", args=[str(self.id)])


class Endpoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Human-readable name, device hostname, and remote address
    name = models.CharField(max_length=100)
    hostname = models.CharField(max_length=100)
    address = models.CharField(max_length=32)
    # Does this device actually have an agent installed?
    is_virtual = models.BooleanField()
    # What protocol and agent does this endpoint use, if any?
    # Also, block endpoints from destruction if an agent or protocol is deleted
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT, related_name="endpoints")
    protocol = models.ForeignKey(
        Protocol, on_delete=models.PROTECT, related_name="endpoints"
    )
    # Encryption key used in communications, if any
    encryption_key = models.CharField(max_length=64, blank=True, null=True)
    # HMAC key used in communications, if any
    hmac_key = models.CharField(max_length=64, blank=True, null=True)
    # Additional JSON configuration object
    agent_cfg = models.JSONField(blank=True, null=True)
    # What other endpoints does this endpoint have direct access to?
    upstream_connections = models.ManyToManyField("self")
    downstream_connections = models.ManyToManyField("self")

    def get_absolute_url(self):
        return reverse("endpoint-detail", args=[str(self.id)])


class Task(models.Model):
    # What user and endpoint, if any, is this task associated with?
    # Theoretically, every task was caused by *someone*, even if it's
    # a periodic task
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="tasks")
    endpoint = models.ForeignKey(
        Endpoint, on_delete=models.PROTECT, related_name="tasks"
    )
    # When was this task started/finished?
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    # Is the task still in progress? What was the task? (How do we tie this to Celery?)
    in_progress = models.BooleanField()
    # Arbitrary data that may be associated with the task. Should be plaintext.
    data = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("task-detail", args=[str(self.id)])


class TaskResult(models.Model):
    # What task is this result associated with?
    task = models.ForeignKey(Task, on_delete=models.PROTECT, related_name="results")
    # Arbitrary data field; may contain files, a raw message, etc. (Note that
    # if a file is present, it *should* be stored with File and not this field.)
    data = models.BinaryField(blank=True, null=True)
    # Timestamp. May or may not be different from the end time of the task.
    timestamp = models.DateTimeField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("taskresult-detail", args=[str(self.id)])


class Credential(models.Model):
    # Task responsible for creating this credential entry, if any
    task = models.ForeignKey(
        Task,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="credentials",
    )
    # Enum field, probably something like "session_token", "userpw", etc
    # Again, it may make sense to create an arbitrary tag model for this
    credential_type = models.CharField(max_length=32)

    # The actual value of the session token, username/password combo, etc -
    # in case the credential is composed of multiple things, it should have a
    # clear delimiter based on credential_type
    credential_value = models.CharField(max_length=255)

    # When this credential becomes invalid
    expiry = models.DateTimeField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("credential-detail", args=[str(self.id)])


class File(models.Model):
    # Task responsible for creating this credential entry, if any
    task = models.ForeignKey(
        Task, on_delete=models.PROTECT, blank=True, null=True, related_name="files"
    )
    # Path to file; location to be determined
    file = models.FileField()

    def get_absolute_url(self):
        return reverse("file-detail", args=[str(self.id)])


class Log(models.Model):
    # Is the log tied to a specific endpoint? (If blank, it's assumed to be
    # the server)
    source = models.ForeignKey(
        Endpoint, blank=True, null=True, on_delete=models.PROTECT, related_name="logs"
    )
    # Is the log tied to a user?
    user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.PROTECT, related_name="logs"
    )
    # Is the log tied to a specific task?
    task = models.ForeignKey(
        Task, blank=True, null=True, on_delete=models.PROTECT, related_name="logs"
    )
    # Is the log tied to a single task result object?
    task_result = models.ForeignKey(
        TaskResult, blank=True, null=True, on_delete=models.PROTECT, related_name="logs"
    )
    # Enumerable field; may make sense to create a "Tag" model and allow
    # it to be associated with arbitrary models, could help with organization
    category = models.CharField(max_length=32, blank=True, null=True)
    # Enum field, levels are likely to be 0 - 5
    level = models.IntegerField(max_length=1, blank=True, null=True)
    # Time of log (ideally, relative to server time; these should be timezone aware)
    timestamp = models.DateTimeField()
    # Actual log message
    data = models.TextField()

    def get_absolute_url(self):
        return reverse("log-detail", args=[str(self.id)])
