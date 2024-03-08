from pathlib import Path

# from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework import status, permissions, viewsets
from rest_framework.exceptions import ValidationError

from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User

from backend.models import Agent, Protocol, Endpoint, Task, TaskResult, Credential, File, Log
from backend.serializers import SignUpSerializer, AgentSerializer, BundleSerializer, ProtocolSerializer, EndpointSerializer, TaskSerializer, TaskResultSerializer, CredentialSerializer, FileSerializer, LogSerializer
from backend.packages import install_agent
# from backend import models
# from backend import serializers
import backend.tasks as tasks

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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'name']
    

class InstallAgentViewSet(viewsets.ViewSet):
    serializer_class = BundleSerializer
    
    # See https://www.reddit.com/r/django/comments/soebxo/rest_frameworks_filefield_how_can_i_force_using/
    # This forces all uploaded files to always manifest as an actual file on 
    # the filesystem, rather than loading the file as something in memory.
    # The package manager only accepts real files, so this guarantees everything
    # ends up on the filesystem.
    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        request.upload_handlers = [TemporaryFileUploadHandler(request=request)]
        return request
    
    # POST
    def create(self, request, format=None):
        data = request.data
        serializer = BundleSerializer(data=data)
        
        if not serializer.is_valid():
            return Response(serializer.errors)
        
        try:
            agent_obj = install_agent(Path(data['bundle_path'].temporary_file_path()))
        except Exception as e:
            raise ValidationError({'bundle_path': [str(e)]})
            # return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AgentSerializer(agent_obj)
        return Response(serializer.data)
        

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
    
    # @action(detail=False, methods=['post'])
    # def celery(self, request):
    #     tasks.task23.delay(data=request.data)
    #     return Response(data={'key2':'val2'})

    
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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'name',]

# Endpoints
class EndpointViewSet(viewsets.ModelViewSet):
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer
    filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['id', 'name', 'hostname', 'address', 'is_virtual', 'agent', 'protocols', 'encryption_key', 'hmac_key', 'connections']
    
    # The user can decide on the following fields. The ID is up to the agent to 
    # generate.
    filterset_fields = ['name', 'hostname', 'address', 'is_virtual', 'agent', 'connections']
    
    def create(self, request, *args, **kwargs):
        # This is overriden to change how the serializer returns. By spinning
        # up an asynchronous task, we can no longer bind the response to the
        # Endpoint result, since that would cause the request to return after a
        # *really* long time. Also, it might not even work, so it's better to just
        # return the task ID and return immediately.
        
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors)
        
        if serializer.data['is_virtual']:
            raise ValidationError({'is_virtual': ["Virtual endpoints are not yet supported!"]})
            
        if not serializer.data['agent']:
            raise ValidationError({'agent': ["An agent is required for non-virtual endpoints!"]})
        
        # result = tasks.generate_payload.delay(serializer.data, request.user.id)
        
        # When implemented on the frontend, this should be used to redirect the
        # user to the task page.
        # return Response({'task_id': result.id})
        
        # TODO: Celery isn't working, but that's not the scope of this ticket
        tmp = tasks.generate_payload(serializer.data, request.user.id)
        serializer_tmp = self.serializer_class(tmp)
        return Response(serializer_tmp.data)

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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'task', 'timestamp',]

# Files
class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'task',]

# Logs
class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer
# @api_view(['GET'])
# def logs(request):
#     logs = Log.objects.all()
#     serializer = LogSerializer(logs, many=True)
#     return Response(serializer.data)