```mermaid
graph TD
    UserRequest[User Request] --> IntelligentInputProcessing[Intelligent Input Processing];
    IntelligentInputProcessing --> ToolManager[ToolManager];

    subgraph ToolManager Responsibilities
        ToolManager --> ToolRegistration[Tool Registration];
        ToolManager --> DynamicDiscovery[Dynamic Discovery];
        ToolManager --> IntelligentToolSelection[Intelligent Tool Selection & Chaining];
        ToolManager --> ToolAdapters[Tool Adapters];
        ToolManager --> SecureOperations[Secure Operations (User Confirmation)];
    end

    IntelligentToolSelection --> ToolExecution[Tool Execution];
    ToolExecution --> ExternalTools[External Tools / Services];
    ExternalTools --> ToolExecutionResult[Tool Execution Result];
    ToolExecutionResult --> IntelligentInputProcessing;

    ToolAdapters --> LocalShell[Local Shell Commands];
    ToolAdapters --> RemoteAPIs[Remote APIs];

    SecureOperations -- "Requires" --> UserConfirmation[User Confirmation];
    UserConfirmation -- "If Approved" --> ToolExecution;
```

**Explanation:** This diagram outlines the Severino CLI's Tool Management System. It shows how user requests are processed, leading to the `ToolManager` which handles registration, discovery, selection, and execution of tools. The diagram also highlights the role of tool adapters for interacting with different environments and the crucial step of user confirmation for secure operations.