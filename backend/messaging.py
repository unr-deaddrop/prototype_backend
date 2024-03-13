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
    
Note that when sending (message.json) and receiving (messages.json), these messages
must be directly serializable to DeadDropMessage. If encryption, signing, or 
fragmentation must be performed, this *must* be done at the protocol level.
That is, all messages entering or exiting this component must already be in 
plaintext and are assumed to be *valid* messages. No signature verification is
done in this component.

In general, it is assumed that a Docker environment is spun up to allow the agent
messaging code to execute in a platform-independent manner.
"""