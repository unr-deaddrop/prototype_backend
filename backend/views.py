from pathlib import Path

# from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework import status, permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from backend.models import (
    Agent,
    Protocol,
    Endpoint,
    Credential,
    File,
    Log,
)
from django_celery_results.models import TaskResult
from backend.serializers import (
    UserSerializer,
    AgentSerializer,
    BundleSerializer,
    ProtocolSerializer,
    EndpointSerializer,
    CredentialSerializer,
    FileSerializer,
    LogSerializer,
    TestSerializer,
    TaskResultSerializer,
    CommandSchemaSerializer,
    AgentSchemaSerializer,
)
from backend.packages import install_agent
from backend.preprocessor import preprocess_dict, preprocess_list

# from backend import models
# from backend import serializers
import backend.tasks as tasks

class TaskResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TaskResult.objects.all()
    serializer_class = TaskResultSerializer
    filter_backends = [DjangoFilterBackend]
    # filterset_fields = [
    #     "id",
    #     "name",
    # ]


class TestViewSet(viewsets.ViewSet):
    serializer_class = TestSerializer

    # POST
    def create(self, request, format=None):
        res = tasks.test_connection.delay()
        result = res.get()

        return Response({"task_id": res.id, "data": result})

    
class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny]) # detail is false bc we're posting with no pk
    def sign_up(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            account = serializer.save()
            token = Token.objects.create(user=account).key # might also be create instead of get
            response = {
                "message": "User created",
                "token": token,
                "data": serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        data = request.data
        account = get_object_or_404(User, username=data['username'])
        if not account.check_password(data['password']):
            return Response("missing user", status=status.HTTP_404_NOT_FOUND)
        token, created = Token.objects.get_or_create(user=account)
        serializer = self.serializer_class(account)
        response = {
                "message": "successfully logged in",
                "token": token.key,
                "data": serializer.data
            }
        return Response(data=response, status=status.HTTP_200_OK)


# Agents
class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["id", "name"]
    
    @action(detail=True, methods=['get'])
    def get_metadata(self, request, pk=None):
        agent: Agent = self.get_object()
        
        # Expects exactly one agent.
        serializer = AgentSchemaSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors)
        
        # Pass the agent config schema through the preprocessor
        metadata = agent.get_agent_metadata()
        
        # Attach the protocol metadata as another key
        metadata['protocol_config'] = agent.get_protocol_metadata()
        
        # Return preprocessed dictionary
        return Response(preprocess_dict(metadata))

    @action(detail=True, methods=['get'])
    def get_command_metadata(self, request, pk=None):
        """
        Return all command metadata *without preprocessing*.
        
        This does not support the filtering that the endpoint version of this
        API endpoint does, since this is intended to be used purely for displaying
        the available commands of an agent to a user. It is not intended
        to be used in generating forms.
        """
        agent: Agent = self.get_object()
        return Response(agent.get_command_metadata())

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
            agent_obj = install_agent(Path(data["bundle_path"].temporary_file_path()))
        except Exception as e:
            raise ValidationError({"bundle_path": str(e)})
            # return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AgentSerializer(agent_obj)
        return Response(serializer.data)


@api_view(["GET"])
def agents(request):
    agents = Agent.objects.all()
    serializer = AgentSerializer(
        agents, many=True
    )  # setting to true means to serialize multiple items. False is just one item
    return Response(serializer.data)


@api_view(["POST"])
def addAgent(request):
    serializer = AgentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


# Credentials
class CredentialViewSet(viewsets.ModelViewSet):
    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer


# Protocols
class ProtocolViewSet(viewsets.ModelViewSet):
    queryset = Protocol.objects.all()
    serializer_class = ProtocolSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "id",
        "name",
    ]


# Endpoints
class EndpointViewSet(viewsets.ModelViewSet):
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer
    filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['id', 'name', 'hostname', 'address', 'is_virtual', 'agent', 'protocols', 'encryption_key', 'hmac_key', 'connections']

    # The user can decide on the following fields. The ID is up to the agent to
    # generate.
    filterset_fields = [
        "name",
        "hostname",
        "address",
        "is_virtual",
        "agent",
        "connections",
    ]

    def create(self, request, *args, **kwargs):
        # This is overriden to change how the serializer returns. By spinning
        # up an asynchronous task, we can no longer bind the response to the
        # Endpoint result, since that would cause the request to return after a
        # *really* long time. Also, it might not even work, so it's better to just
        # return the task ID and return immediately.

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors)

        if serializer.data["is_virtual"]:
            raise ValidationError(
                {"is_virtual": "Virtual endpoints are not yet supported!"}
            )

        if not serializer.data["agent"]:
            raise ValidationError(
                {"agent": "An agent is required for non-virtual endpoints!"}
            )

        result = tasks.generate_payload.delay(serializer.data, request.user.id)

        # When implemented on the frontend, this should be used to redirect the
        # user to the task page.
        return Response({"task_id": result.id})

        # Synchronous version, used originally for debugging
        # tmp = tasks.generate_payload(serializer.data, request.user.id)
        # serializer_tmp = self.serializer_class(tmp)
        # return Response(serializer_tmp.data)

    # really, this should be a GET request, but i think the interface is "cleaner"
    @action(detail=True, methods=['post'])
    def get_command_metadata(self, request, pk=None):
        # Note that we expect an endpoint, not an agent, even though the response
        # would be the same across two endpoints of the same agent. This is to
        # emphasize that it should not be possible to get fine-grained, 
        # preprocessed metadata without a specific endpoint in mind.
        endpoint: Endpoint = self.get_object()
        
        # Verify the endpoint and command are valid...
        print(request.data)
        serializer = CommandSchemaSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors)
        
        metadata = preprocess_list(endpoint.agent.get_command_metadata())
        commands = {cmd['name']: cmd for cmd in metadata}
        
        # If no command was specialized, return the full list of commands,
        # preprocessed
        if 'command' not in serializer.data:
            return Response(metadata)
        
        # If a command was specified, but it doesn't exist for this endpoint
        # (i.e. it doesn't exist for this agent), then raise an error
        command = serializer.data['command']
        if command not in commands:
            raise ValidationError({"command": "Command is not valid for this endpoint!"})
    
        # Return the selected command, preprocessed
        return Response(commands[command])

    @action(detail=True, methods=['post'])
    def execute_command(self, request, pk=None):
        # TODO: Define the serializer. It'll probably just be equal to 
        # CommandRequestPayload.
        
        # Retrieve the JSON schema for this command, do not preprocess; obviously,
        # fail if the command doesn't exist for this endpoint
        
        # Validate the incoming cmd_args against this schema
        #
        # Note that we can't use a serializer with a pre-defined schema, as with
        # https://pypi.org/project/drf-jsonschema/, since the schema is defined
        # at runtime. There are a few ways to get around this, but the stock
        # jsonschema is fine. 
        #
        # Additionally, note that jsonschema supports the anyOf syntax that is
        # normally removed by the preprocessor. We pass the raw Pydantic output
        # to jsonschema, since this does exactly what we want - validation
        # against the original. The absence of a non-required key is fine, since
        # when it reaches the agent, it should be assumed None. In our case, this
        # is guaranteed by Pydantic's model validation.
        
        # On failure, immediately return the error. This isn't DRF-compliant as-is,
        # but the other library above just returns ValidationError.message anyways.
        # https://python-jsonschema.readthedocs.io/en/latest/errors/
        
        # If the command arguments pass, invoke the command execution task.
        # This also invokes a separate "receive message" subtask, which is started
        # at the end of the task and runs asynchronously. The user attribution
        # for the task is the same as the original command execution task.
        
        # Return the task ID, which is intended to be used by the frontend
        # to bring the user to the relevant TaskResult detail page.
        
        raise NotImplementedError

# Files
class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "id",
        "task",
    ]


# Logs
class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer
