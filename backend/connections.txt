Agent

Protocol

Endpoint
    agent = AgentSerializer()
    protocol = ProtocolSerializer(many=True)

Task
    endpoint = EndpointSerializer()

TaskResult
    task = TaskSerializer(read_only=True)

Credential
    task = TaskSerializer()

File
    task = TaskSerializer()

Log
    source = EndpointSerializer()
    task = TaskSerializer()
    task_result = TaskResultSerializer()







#################

Agent

Protocol

Endpoint
    agent = AgentSerializer()
    protocol = ProtocolSerializer(many=True)

Task
    endpoint = EndpointSerializer()
        Endpoint
        agent = AgentSerializer()
        protocol = ProtocolSerializer(many=True)

TaskResult
    task = TaskSerializer(read_only=True)
        Task
        endpoint = EndpointSerializer()
            Endpoint
            agent = AgentSerializer()
            protocol = ProtocolSerializer(many=True)

Credential
    task = TaskSerializer()
        Task
        endpoint = EndpointSerializer()
            Endpoint
            agent = AgentSerializer()
            protocol = ProtocolSerializer(many=True)

File
    task = TaskSerializer()
        Task
        endpoint = EndpointSerializer()
            Endpoint
            agent = AgentSerializer()
            protocol = ProtocolSerializer(many=True)

Log
    source = EndpointSerializer()
        Endpoint
        agent = AgentSerializer()
        protocol = ProtocolSerializer(many=True)

    task = TaskSerializer()
        Task
        endpoint = EndpointSerializer()
            Endpoint
            agent = AgentSerializer()
            protocol = ProtocolSerializer(many=True)

    task_result = TaskResultSerializer()
        TaskResult
        task = TaskSerializer(read_only=True)
            Task
            endpoint = EndpointSerializer()
                Endpoint
                agent = AgentSerializer()
                protocol = ProtocolSerializer(many=True)


NEW
#################

Agent

Protocol

Endpoint
    agent = AgentSerializer()
    protocol = ProtocolSerializer(many=True)

Task
    endpoint = EndpointSerializer()
        Endpoint
        agent = AgentSerializer()
        protocol = ProtocolSerializer(many=True)

TaskResult
    task = TaskSerializer(read_only=True)
        Task
        endpoint = EndpointSerializer()
            Endpoint
            agent = AgentSerializer()
            protocol = ProtocolSerializer(many=True)

Credential
    task = TaskSerializer()
        Task
        endpoint = EndpointSerializer()
            Endpoint
            agent = AgentSerializer()
            protocol = ProtocolSerializer(many=True)

File
    task = TaskSerializer()
        Task
        endpoint = EndpointSerializer()
            Endpoint
            agent = AgentSerializer()
            protocol = ProtocolSerializer(many=True)

Log
    source = EndpointSerializer()
        Endpoint
        agent = AgentSerializer()
        protocol = ProtocolSerializer(many=True)

    task_result = TaskResultSerializer()
        TaskResult
        task = TaskSerializer(read_only=True)
            Task
            endpoint = EndpointSerializer()
                Endpoint
                agent = AgentSerializer()
                protocol = ProtocolSerializer(many=True)

