from rest_framework import serializers
from rest_framework.validators import ValidationError
from backend.models import Agent, Protocol, Endpoint, Task, TaskResult, Credential, File, Log
from django.contrib.auth.models import User

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        # fields = ['username', 'first_name', 'last_name', 'email', 'password', 'groups', 'user_permissions', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'last_login', 'date_joined']
        fields = ['username', 'password']
    # def validate(self, attrs):
    #     email_exists = User.objects.filter(email=attrs['email']).exists()
    #     if email_exists:
    #         raise ValidationErrror("Email already in use!")
    #     return super().validate(attrs)
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    def __str__(self):
        return self.username
    

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'
        # fields = ['name']

class ProtocolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Protocol
        fields = '__all__'
        # fields = ['name']

class EndpointSerializer(serializers.ModelSerializer):
    # agent = AgentSerializer()
    # protocols = ProtocolSerializer(many=True)
    class Meta:
        model = Endpoint
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    # endpoint = EndpointSerializer()
    data = serializers.JSONField()
    class Meta:
        model = Task
        fields = '__all__'

class TaskResultSerializer(serializers.ModelSerializer):
    # task = TaskSerializer(read_only=True) # taskresult should not be able to make tasks
    class Meta:
        model = TaskResult
        fields = '__all__'

class CredentialSerializer(serializers.ModelSerializer):
    # task = TaskSerializer()
    credential_value = serializers.JSONField()
    class Meta:
        model = Credential
        fields = '__all__'
        # fields = ['id', 'credential_type']

class FileSerializer(serializers.ModelSerializer):
    # task = TaskSerializer()
    class Meta:
        model = File
        fields = '__all__'

class LogSerializer(serializers.ModelSerializer):
    # source = EndpointSerializer()
    # task = TaskSerializer()
    # task_result = TaskResultSerializer()
    class Meta:
        model = Log
        fields = '__all__'

