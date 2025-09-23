# Trip Planner API Testing

This directory contains testing scripts for the Trip Planner API built with Google Agent Development Kit (ADK).

## Test Run Endpoint

The `test_run_endpoint.py` script tests the `/run` endpoint which is responsible for processing user queries and generating trip planning responses.

### Requirements

- Python 3.6+
- `requests` library

```bash
pip install requests
```

### Usage

1. First, ensure that your Trip Planner API server is running (typically on port 8080).

2. Run the basic test (sends a simple trip planning query):

```bash
python test_run_endpoint.py
```

3. Run the complex test (sends a more detailed trip planning query):

```bash
python test_run_endpoint.py --complex
```

4. List all active sessions for the test user:

```bash
python test_run_endpoint.py --list-sessions
```

5. Create a fresh session and test with it:

```bash
python test_run_endpoint.py --fresh
```

6. Use a specific session ID for testing:

```bash
python test_run_endpoint.py --session <session_id>
```

### Script Details

The script includes these main functions:

1. `get_active_sessions()`: Retrieves all active sessions for a user
2. `check_session_exists()`: Verifies if a specific session exists and is valid
3. `create_session()`: Creates a new session or uses an existing one
4. `list_sessions()`: Lists all available sessions for the test user
5. `test_run_endpoint()`: Sends a simple query about planning a trip to Paris
6. `test_run_endpoint_with_complex_query()`: Sends a more detailed query about planning a family trip to Japan

### Request Schema

First, a session is created, and then a request is sent to the `/run` endpoint. 

The request to the `/run` endpoint follows this structure:

```json
{
  "appName": "trip-planner",
  "userId": "test-user",
  "sessionId": "<generated-uuid>",
  "newMessage": {
    "role": "user",
    "parts": [
      {
        "text": "Your trip planning query here"
      }
    ]
  },
  "streaming": false
}
```

### Response Structure

The response contains a list of events, each potentially having content with text parts. The script extracts and displays the text content from these events.

### Customization

You can modify the BASE_URL variable in the script if your server is running on a different host or port.