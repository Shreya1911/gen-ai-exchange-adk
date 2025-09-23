# Trip Planner Agent API

This directory contains the code for a Trip Planner agent built using Google's Agent Development Kit (ADK), exposed as a FastAPI web service.

## Project Structure

- `agents/`: Contains the main agent definition and supporting modules
  - `agent.py`: Defines the root agent and imports sub-agents
  - `prompt.py`: Contains prompts for the agent
  - `tools.py`: Defines tools used by the agent
  - `sub_agents/`: Contains specialized sub-agents for different parts of the trip planning process
- `main.py`: FastAPI application to expose the agent via a REST API

## Running the API Server

To run the FastAPI server:

1. Ensure you have the required dependencies installed:
   ```bash
   pip install google-adk fastapi uvicorn
   ```

2. Run the server:
   ```bash
   cd /path/to/genai-exchange-trip-planner/backend/trip-planner
   python main.py
   ```

3. The API will be accessible at `http://localhost:8080`
   - API documentation is available at `http://localhost:8080/docs`
   - Alternative API documentation is at `http://localhost:8080/redoc`

## Environment Variables

- `GOOGLE_CLOUD_PROJECT`: The Google Cloud project ID for cloud tracing (defaults to "alvin-exploratory-2")
- `PORT`: The port to run the server on (defaults to 8080)

## API Endpoints

The FastAPI server exposes the following endpoints:

- `/agents`: Lists available agents
- `/agents/{agent_name}/chat`: Endpoint for chatting with the agent
- `/agents/{agent_name}/tools`: Lists available tools for a specific agent

For more details on the API, refer to the automatically generated documentation at the `/docs` endpoint.