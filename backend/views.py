# from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from backend.models import Agent
from .serializers import AgentSerializer

# Create your views here.
@api_view(['GET'])
def agents(request):
    agents = Agent.objects.all()
    serializer = AgentSerializer(agents, many=True) # setting to true means to serialize multiple items. False is just one item
    return Response(serializer.data)