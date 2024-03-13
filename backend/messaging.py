"""
The DeadDrop messaging system.

A longer description can be found at the following link:
https://github.com/unr-deaddrop/backend/issues/15

The messaging system works by assuming that a package contains a message_entry
recipe exists in the agent's Makefile. The entire package is copied to a temporary
directory before execution.

The following conventions are assumed:
- That a Makefile exists, and that a `message_entry` recipe exists;
- That the called script leverages a `message_config.json` that is used to call
  the appropriate protocol handler bundled with the agent and configure it
  to reach out to the agent, where `message_config.json` contains the 
  *agent's* configuration data
- That if indicated in `message_config.json` to SEND, an additional file called
  `message.json` contains the serialized DeadDropMessage to be sent.
- That once the script returns, the following contents are made available in the
  temporary directory:
  - message-log.txt, the immediate result of the task
  - if RECEIVING a message, messages.json, one or more messages retrieved from the
    protocol handler
  - protocol_state.json, an optional JSON document that allows for state maintenace
    across different calls to the protocol handler. The structure of this JSON
    document is agent-specific, and may be used (for example) to keep track of 
    messages that have already been seen.
    
Note that when sending (message.json) and receiving (messages.json), these messages
must be directly serializable to DeadDropMessage. If encryption, signing, or 
fragmentation must be performed, this *must* be done at the protocol level.
That is, all messages entering or exiting this component must already be in 
plaintext and are assumed to be *valid* messages. No signature verification is
done in this component.

In general, it is assumed that a Docker environment is spun up to allow the agent
messaging code to execute in a platform-independent manner.
"""

from pathlib import Path
from typing import Any, Optional, Union, Literal
import logging

from pydantic import BaseModel

from deaddrop_meta.protocol_lib import DeadDropMessage
from deaddrop_meta.interface_lib import MessagingObject

from django.contrib.auth.models import User
from backend.models import Endpoint, Log

logger = logging.getLogger(__name__)

def send_message(
    msg: DeadDropMessage,
    endpoint: Endpoint,
    task_id: Optional[str],
    user: Optional[User]
) -> dict[str, Any]:
    """
    Send the provided message to an endpoint.
    """
    # Copy the entire package into a temporary directory (note that we don't need
    # to resolve the package path, since it's already correct relative to wherever
    # Django and the workers are running)
    temp_dir = endpoint.agent.copy_to_temp_dir()
    temp_dir_path = Path(temp_dir.name).resolve()
    logger.info(f"Using {temp_dir_path} for build")
    
    # Construct our MessageObject, then dump it out to the temporary directory as
    # message_config.json
    
    # Dump the DeadDropMessage as message.json into the temporary directory
    
    # Assert that the Makefile is present and invoke the message_entry recipe
    
    # Take message-log.txt and use that as the result, also converting it into a 
    # LogMessage
    
    # If present, read protocol_state.json and update the endpoint accordingly
    
    # Blow up the temporary directory
    
    # Return the contents of message-log.txt as the task's result
    raise NotImplementedError

def receive_messages(
    endpoint: Endpoint,
    request_id: Optional[str]
) -> list[DeadDropMessage]:
    """
    Receive messages from an endpoint.
      
    Filtering of duplicate messages is done at this stage by checking all 
    incoming DeadDropMessages against the list of Message instances currently
    contained in the database. If a message ID has already been seen, it is 
    assumed to be a duplicate message and dropped; otherwise, it is returned
    as part of the result. 
    
    Note that this function *does not* return Message instances (as declared 
    in models.py), but rather DeadDropMessage instances.
    
    If specified, request_id may be used to filter incoming messages to just
    the message specified. This only works if the message has a 
    CommandResponsePayload; all other messages are unconditionally dropped
    when request_id is specified.
    """
    # Copy the entire package into a temporary directory (note that we don't need
    # to resolve the package path, since it's already correct relative to wherever
    # Django and the workers are running)
    temp_dir = endpoint.agent.copy_to_temp_dir()
    temp_dir_path = Path(temp_dir.name).resolve()
    logger.info(f"Using {temp_dir_path} for build")
    
    # Construct our MessageObject, then dump it out to the temporary directory as
    # message_config.json
    
    # Assert that the Makefile is present and invoke the message_entry recipe
    
    # Take message-log.txt and use that as the result, also converting it into a 
    # LogMessage
    
    # If present, read protocol_state.json and update the endpoint accordingly
    
    # Take messages.json and construct DeadDrop messages from it
    
    # Blow up the temporary directory
    
    # Return the result
    raise NotImplementedError