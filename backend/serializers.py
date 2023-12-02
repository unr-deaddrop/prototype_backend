from rest_framework import serializers
from backend.models import Agent, Protocol, Endpoint, Task, TaskResult, Credential, File, Log

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        # fields = '__all__'
        fields = ['name']

class ProtocolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Protocol
        # fields = '__all__'
        fields = ['name']

class EndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endpoint
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class TaskResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskResult
        fields = '__all__'

class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = '__all__'
        # fields = ['id', 'credential_type']

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'

