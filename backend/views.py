# from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from backend.models import Agent, Credential
from backend.serializers import AgentSerializer, CredentialSerializer

# Create your views here.
# Agents
@api_view(['GET'])
def agents(request):
    agents = Agent.objects.all()
    serializer = AgentSerializer(agents, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def addAgent(request):
    serializer = AgentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

# Credentials
@api_view(['GET'])
def credentials(request):
    credentials = Credential.objects.all()
    serializer = CredentialSerializer(credentials, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def addCredential(request):
    serializer = CredentialSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)