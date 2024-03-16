"""
Generic reusable statistics modules intended to aid in rendering summary graphs
for the frontend.

Yes, this is the only reason why Pandas is a requirement.
"""

from typing import Any
import uuid

from pandas.tseries.offsets import DateOffset
from pandas.core.groupby import DataFrameGroupBy
import pandas as pd


from backend.models import Agent, Endpoint, Message
from django_celery_results.models import TaskResult
from django.db.models import Count


def get_agent_stats() -> dict[str, int]:
    """
    Get the number of endpoints currently in use for each agent.
    """
    agents = Agent.objects.annotate(num_endpoints=Count("endpoints"))
    return {str(agent): agent.num_endpoints for agent in agents}


def get_endpoint_communication_stats() -> dict[str, int]:
    """
    Get the number of messages associated with each endpoint.

    This simply adds the number of messages sent to an endpoint by the server
    to the number of messages received by the server from that same endpoint,
    performing the operation for each.
    """
    # https://stackoverflow.com/questions/51701091/django-annotate-with-multiple-count
    endpoints = Endpoint.objects.annotate(
        num_source=Count("messages_sources", distinct=True),
        num_dest=Count("messages_destinations", distinct=True),
    )
    return {
        str(endpoint): int(endpoint.num_source) + int(endpoint.num_dest)
        for endpoint in endpoints
    }

def replace_null_uuid(val: Any) -> Any:
    """
    Replace null UUIDs with None for the sake of calculation.
    
    Certain older implementations of the DeadDrop messaging system used
    null UUIDs to refer to the server.
    """
    
    if val == str(uuid.UUID(int=0)):
        return None
    
    return val
    
def get_recent_global_message_stats() -> DataFrameGroupBy:
    """
    Get the number of messages sent each hour for the last 24 hours. 
    
    Note that the first item in the list represents the number of messages
    sent in the last hour; the last item in the list represents the number of
    messages sent between 23 and 24 hours ago.
    
    Additionally, note that the time ranges are from "right now" and working
    in intervals of one hour back. This is consistent with what a user would
    expect, and is why this function does not simply take the hour component
    of all messages within the last 24 hours and bin them that way.
    """
    # https://stackoverflow.com/questions/35437733/pandas-date-range-starting-from-the-end-date-to-start-date
    
    # Start by getting the current time, less 24 hours
    end = pd.Timestamp.utcnow()
    start = end - DateOffset(hours=24)
    
    # Get all recent messages, selecting relevant fields, and convert as necessary.
    # For our purposes, replace any null UUIDs with None in either the source or
    # destination columns.
    recent_messages = Message.objects.filter(timestamp__gte=start.to_pydatetime())
    df = pd.DataFrame(recent_messages.values("message_id", "timestamp", "source", "destination"))
    df.timestamp = pd.to_datetime(df.timestamp)
    df.source = df.source.apply(replace_null_uuid)
    df.destination = df.destination.apply(replace_null_uuid)
    
    # Create a DatetimeIndex relative to end, then reverse so that it is 
    # monotonically increasing (required by pd.cut). Assume UTC.
    date_idx = pd.DatetimeIndex([end-DateOffset(hours=e) for e in range(0, 25)])
    date_idx = date_idx.tz_localize('UTC')
    
    # Categorize timestamps and use this as the groupby. With observed=False,
    # this includes categories for which their value was 0.
    res = df.groupby([pd.cut(df['timestamp'], date_idx)], observed=False)
    
    # The result is a groupby result whose columns are message_id, timestamp, 
    # source, destination. At this point, the immediate result can be returned.
    # Because of our operations, it just so happens that message_id and timestamp
    # refer to the number of non-null values for each hour, which is always 
    # equal to the number of combined messages.
    #
    # But `source` refers to the number of messages with non-null values, indicating
    # an agent sent them. `destination` being non-null indicates the server sent them.
    # We can use this to our advantage to calculate finer statistics.
    return res
    
def get_task_stats() -> dict[str, int]:
    """
    Count the following:
    - the number of running tasks (PENDING)
    - the number of open callbacks, assumed to be those that are associated with
      backend.tasks.receive_messages (and therefore not "instant")
    - the total number of tasks
    - the number of completed tasks (not PENDING, so either SUCCESS or FAILURE)
    """
    
    # Note that we assume if something's not PENDING, it must be done. This is
    # not *strictly* true within the Celery API, but (to the best of my knowledge)
    # it is true of TaskResult. 
    return {
        "running": TaskResult.objects.filter(status="PENDING").count(),
        "callbacks":TaskResult.objects.filter(task_name="backend.tasks.receive_messages").count(),
        "total":TaskResult.objects.count(),
        "completed":TaskResult.objects.exclude(status="PENDING").count() 
    }
    
    