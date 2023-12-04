# from backend.models import Agent
# from backend import serializers

# # Agent.object.create(name='Test', definition_path=None)
# # print(Agent.objects.all())
# # print(Agent.objects.all().delete())


# # Credential.objects.create(credential_type='test', credential_value='test2', expiry=None, task=None)
# # print(Credential.objects.all())
# # print(Credential.objects.all().delete())

# print(repr(serializers.CredentialSerializer()))
# print(repr(serializers.AgentSerializer()))
# print(repr(serializers.ProtocolSerializer()))

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
for user in User.objects.all():
    print(Token.objects.get_or_create(user=user))
    
exit()

{"credential_type":"test1", "credential_value":"test12", "expiry":null, "task":null}
