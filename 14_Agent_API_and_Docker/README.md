# Week 14: Serving & API Deployment

## Weekly Goals
1.  **API Layer**: Wrap your "Observable Agent" (Week 13) in a robust HTTP API using **FastAPI**.
2.  **Standards**: Use modern API practices (Pydantic models, Async endpoints, Swagger UI).
3.  **Scalability**: Handle multiple concurrent requests without blocking.
4.  **Security**: Basic API Key authentication.

## Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - *Best modern Python API framework*
- [Uvicorn](https://www.uvicorn.org/) - *ASGI Server*
- [LangChain Runnables](https://python.langchain.com/docs/expression_language/interface) - *Streaming responses*

## Architecture: The Agent Microservice

### 1. The API Server (FastAPI)
**Implemented in:** `[1.0]_agent_api.py`
-   **Endpoint**: `POST /chat`
-   **Input**: `{"query": "Show me sales", "user_id": "123"}`
-   **Output**: `{"response": "Here is the chart...", "trace_id": "abc-123"}`
-   **Features**:
    -   Auto-Generated Swagger Docs (`/docs`).
    -   Background Tasks for logging (to avoid latency).
    -   Streaming support (optional, for real-time feel).

### 2. The Client Simulator
**Implemented in:** `[2.0]_api_client.py`
-   **Role**: A script that hammers the API with requests to test concurrency.
-   **Tech**: Uses `httpx` or `requests`.

### 3. Dockerization (Optional Logic)
**Context**: In a real deployment, this API would run inside a Docker container orchestrated by Kubernetes/ECS.
-   **Dockerfile**: Instructions to build the image.

## Jargon Buster

| Term | Simple Definition | Technical Context | DE Equivalent |
| :--- | :--- | :--- | :--- |
| **ASGI** | Asynchronous Server Gateway Interface. | The standard for Python async web servers. | **Worker Node (Celery)** |
| **Endpoint** | A specific URL where your API lives. | `http://api.com/v1/chat`. | **REST API Resource** |
| **Payload** | The data sent to the API. | JSON body of a POST request. | **Message in Kafka** |
| **Concurrency** | Handling multiple requests at overlapping times. | `async def` functions awaiting I/O. | **Parallel Processing** |

-   [ ] **Client Test**: Run the python client to send 5 rapid requests.

## How to Run

### Start the API Server
This launches the FastAPI application on localhost.
```bash
python 14_Agent_API_and_Docker/[1.0]_agent_api.py
```

### Run the Client Simulator
Test the API with concurrent requests.
```bash
python 14_Agent_API_and_Docker/[2.0]_api_client.py
```

### View API Documentation
Once the server is running, visit:
`http://127.0.0.1:8000/docs`
