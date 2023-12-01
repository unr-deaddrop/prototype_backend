from backend.models import Agent

Agent.object.create(name='Test', definition_path=None)
print(Agent.objects.all())
print(Agent.objects.all().delete())


Credential.objects.create(credential_type='test', credential_value='test2', expiry=None, task=None)
print(Credential.objects.all())
print(Credential.objects.all().delete())

exit()