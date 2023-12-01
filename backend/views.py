# from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status, permissions, viewsets
from backend.models import Agent, Protocol, Endpoint, Task, TaskResult, Credential, File, Log
from backend.serializers import AgentSerializer, ProtocolSerializer, EndpointSerializer, TaskSerializer, TaskResultSerializer, CredentialSerializer, FileSerializer, LogSerializer

# Create your views here.
# Agents
@api_view(['GET'])
def agents(request):
    agents = Agent.objects.all()
    serializer = AgentSerializer(agents, many=True) # setting to true means to serialize multiple items. False is just one item
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

# Protocols
@api_view(['GET'])
def protocols(request):
    protocols = Protocol.objects.all()
    serializer = ProtocolSerializer(protocols, many=True)
    return Response(serializer.data)

# Endpoints
@api_view(['GET'])
def endpoints(request):
    endpoints = Endpoint.objects.all()
    serializer = EndpointSerializer(endpoints, many=True)
    return Response(serializer.data)

# tasks
@api_view(['GET'])
def tasks(request):
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

# TaskResults
@api_view(['GET'])
def taskResults(request):
    taskResults = TaskResult.objects.all()
    serializer = TaskResultSerializer(taskResults, many=True)
    return Response(serializer.data)

# Files
@api_view(['GET'])
def files(request):
    files = File.objects.all()
    serializer = FileSerializer(files, many=True)
    return Response(serializer.data)

# Logs
@api_view(['GET'])
def logs(request):
    logs = Log.objects.all()
    serializer = LogSerializer(logs, many=True)
    return Response(serializer.data)