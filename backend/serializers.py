from rest_framework import serializers
from backend.models import Agent

class AgentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'