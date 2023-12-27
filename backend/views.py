# from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status, permissions, viewsets

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User

from backend.models import Agent, Protocol, Endpoint, Task, TaskResult, Credential, File, Log
from backend.serializers import SignUpSerializer, AgentSerializer, ProtocolSerializer, EndpointSerializer, TaskSerializer, TaskResultSerializer, CredentialSerializer, FileSerializer, LogSerializer
# from backend import models
# from backend import serializers

# Create your views here.
# Users
# @api_view(['POST'])
# def signUp(request):
#     serializer = SignUpSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#     return Response(data=serializer.data)

# from rest_framework import generics
# class SignUpView(generics.GenericAPIView):
#     serializer_class = SignUpSerializer
#     def post(self, request):
#         data = request.data
#         serializer = self.serializer_class(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             response = {
#                 "message": "User created",
#                 "data": serializer.data
#             }
#             return Response(data=response, status=status.HTTP_201_CREATED)
#         return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SignUpViewSet(viewsets.ViewSet):
    serializer_class = SignUpSerializer
    # def list(self, request):
    #     queryset = User.objects.all()
    #     serializer = self.serializer_class(queryset, many=True)
    #     return Response(data=serializer.data)
    
    def create(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "message": "User created",
                "data": serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Agents
class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
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
class CredentialViewSet(viewsets.ModelViewSet):
    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer
    
    # def list(self, request):
    #     serializer = self.get_serializer(self.get_queryset(), many=True)
    #     return self.get_paginated_response(self.paginate_queryset(serializer.data))

    # def create(self, *args, **kwargs):
    #     return super().create(*args, **kwargs)

    # def retrieve(self, request, pk=None):
    #     pass

    # def update(self, request, pk=None):
    #     pass

    # def partial_update(self, request, pk=None):
    #     pass

    # def destroy(self, request, pk=None):
    #     pass
    
# @api_view(['GET'])
# def credentials(request):
#     credentials = Credential.objects.all()
#     serializer = CredentialSerializer(credentials, many=True)
#     return Response(serializer.data)

# @api_view(['POST'])
# def addCredential(request):
#     serializer = CredentialSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#     return Response(serializer.data)

# Protocols
class ProtocolViewSet(viewsets.ModelViewSet):
    queryset = Protocol.objects.all()
    serializer_class = ProtocolSerializer

# Endpoints
class EndpointViewSet(viewsets.ModelViewSet):
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'name', 'hostname', 'address', 'is_virtual', 'agent', 'protocols', 'encryption_key', 'hmac_key', 'connections']

# tasks
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    def create(self, request, *args, **kwargs):
        print('all:', request.data)
        print('\nform data:', request.data['data'])
        return super().create(request, *args, **kwargs)

# TaskResults
class TaskResultViewSet(viewsets.ModelViewSet):
    queryset = TaskResult.objects.all()
    serializer_class = TaskResultSerializer

# Files
class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

# Logs
class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer
# @api_view(['GET'])
# def logs(request):
#     logs = Log.objects.all()
#     serializer = LogSerializer(logs, many=True)
#     return Response(serializer.data)