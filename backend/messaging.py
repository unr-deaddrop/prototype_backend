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

from typing import Any, Optional

from deaddrop_meta.protocol_lib import (
    DeadDropMessage, 
    CommandRequestPayload, 
    CommandResponsePayload,
)

from backend.models import Endpoint, Log

def send_message(
    endpoint: Endpoint,
) -> dict[str, Any]:
    """
    Send the provided message to an endpoint.
    """

def receive_messages(
    endpoint: Endpoint,
    request_id: Optional[str]
) -> list[DeadDropMessage]:
    """
    Receive messages from an endpoint.
    
    In general, it is ultimately up to an upstream component to determine if any
    messages should be dropped. The protocol *may* choose to accept and return
    protocol_state.json, which is used to keep track of internal information across
    calls to the protocol handler. However, upstream components should note the 
    following:
    - All log messages contain a UUIDv4, which can be used to distinguish between
      elements in log bundles.
    - All individual messages contain a UUIDv4, which can be used to distinguish
      between received messages.
      
    Therefore, it should be possible to ignore 
    
    If specified, request_id may be used to filter incoming messages to just
    the message specified. This only works if the message has a 
    CommandResponsePayload; all other messages are unconditionally dropped
    when request_id is specified.
    """