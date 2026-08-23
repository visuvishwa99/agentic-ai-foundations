# Week 14: local agent API

This folder wraps the Week 8 SQL agent in a small FastAPI service and includes a request script.

## Files

- `[1.0]_agent_api.py` exposes `/health` and `/chat`.
- `[2.0]_api_client.py` sends sample requests to the local server.
- `[3.0]_docker_example.md` contains container notes. There is no checked-in Dockerfile.

This is a development example. The API does not implement authentication, streaming, durable background logging, or a production readiness check. The current client sends requests sequentially.

## Run

Start the API:

```bash
python "14_Agent_API_and_Docker/[1.0]_agent_api.py"
```

In another terminal:

```bash
python "14_Agent_API_and_Docker/[2.0]_api_client.py"
```

Swagger UI is available at `http://127.0.0.1:8000/docs`.

## Notes for revision

Before exposing an agent API beyond localhost, add authentication, request limits, sanitized errors, readiness checks, and tests for concurrent requests.
