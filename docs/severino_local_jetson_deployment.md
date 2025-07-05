graph TD
    User[User on Jetson] --> CLI[Severino CLI on Jetson];
    CLI -- Local IPC --> ReactUI[Electron LLM UI Device Config Hub on Jetson];

    subgraph LocalJetsonDeployment[Severino Local Deployment on Jetson]
        ReactUI -- Local HTTP/IPC --> PythonBackendMain[Python Backend Core Logic and Device Manager on Jetson];
        CLI -- Local HTTP/IPC --> PythonBackendMain;

        MLMonitoring[ML Monitoring CAMA];
        SQLite[SQLite Database];

        PythonBackendMain -- SQLite Local Storage --> SQLite;
        MLMonitoring -- Internal API --> PythonBackendMain;

        PythonBackendMain -- Direct Access --> JetsonHardware[Jetson Hardware Sensors and Accelerators];
        JetsonHardware -- Data Streams --> PythonBackendMain;

        PythonBackendMain -- Local LLM Inference --> LocalLLM[Local LLM Gemma on Jetson];
        LocalLLM -- LLM Responses --> PythonBackendMain;
    end

    style LocalJetsonDeployment fill:#f9f,stroke:#333,stroke-width:2px
