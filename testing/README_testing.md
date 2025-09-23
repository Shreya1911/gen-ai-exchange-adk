````markdown
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

## Testing with Postman

This section provides instructions for testing the Trip Planner API using Postman, a popular API testing tool.

### Setting Up Postman for Testing

1. **Install Postman**: Download and install Postman from [postman.com](https://www.postman.com/downloads/).

2. **Configure Environment**:
   - Create a new environment in Postman
   - Add a variable `base_url` with the value `http://localhost:8080` (adjust if your server runs on a different port)
   - Add a variable `userId` with value `test-user`
   - Add a variable `appName` with value `agents`

### Testing Workflow

#### Step 1: Create a Session

1. Create a new POST request in Postman
2. URL: `{{base_url}}/apps/{{appName}}/users/{{userId}}/sessions`
3. Headers: Add `Content-Type: application/json`
4. Body (raw JSON):
   ```json
   {
     "appName": "{{appName}}",
     "userId": "{{userId}}",
     "sessionId": "{{$guid}}",
     "description": "Test session created via Postman"
   }
   ```
5. Send the request
6. After receiving a successful response, extract the `sessionId` from the response and save it as a Postman environment variable:
   - In the Tests tab, add this code:
   ```javascript
   var jsonData = pm.response.json();
   pm.environment.set("sessionId", jsonData.sessionId);
   ```

#### Step 2: Verify Session Exists

1. Create a new GET request
2. URL: `{{base_url}}/apps/{{appName}}/users/{{userId}}/sessions/{{sessionId}}`
3. Send the request
4. Verify you receive a 200 OK response

#### Step 3: Send Your First Message

1. Create a new POST request
2. URL: `{{base_url}}/run`
3. Headers: Add `Content-Type: application/json`
4. Body (raw JSON):
   ```json
   {
     "appName": "{{appName}}",
     "userId": "{{userId}}",
     "sessionId": "{{sessionId}}",
     "newMessage": {
       "role": "user",
       "parts": [
         {
           "text": "I want to plan a trip to Paris for 5 days in December."
         }
       ]
     },
     "streaming": false
   }
   ```
5. Send the request
6. Examine the response - you should receive an itinerary suggestion for Paris

#### Step 4: Continue the Conversation

1. Create a new POST request (or duplicate the previous one)
2. URL: `{{base_url}}/run`
3. Use the same headers
4. Body (raw JSON) - use the same structure but change the message:
   ```json
   {
     "appName": "{{appName}}",
     "userId": "{{userId}}",
     "sessionId": "{{sessionId}}",
     "newMessage": {
       "role": "user",
       "parts": [
         {
           "text": "Can you suggest some good restaurants near the Eiffel Tower?"
         }
       ]
     },
     "streaming": false
   }
   ```
5. Send the request
6. Examine the response - you should receive restaurant recommendations

#### Step 5: Ask About Activities

1. Create another POST request to `/run`
2. Body:
   ```json
   {
     "appName": "{{appName}}",
     "userId": "{{userId}}",
     "sessionId": "{{sessionId}}",
     "newMessage": {
       "role": "user",
       "parts": [
         {
           "text": "What are some family-friendly activities we can do in Paris?"
         }
       ]
     },
     "streaming": false
   }
   ```
3. Send the request
4. Examine the response - you should receive suggestions for family activities

#### Step 6: Request a Revised Itinerary

1. Create another POST request to `/run`
2. Body:
   ```json
   {
     "appName": "{{appName}}",
     "userId": "{{userId}}",
     "sessionId": "{{sessionId}}",
     "newMessage": {
       "role": "user",
       "parts": [
         {
           "text": "Can you revise the itinerary to include more museum visits and less shopping?"
         }
       ]
     },
     "streaming": false
   }
   ```
3. Send the request
4. Examine the response - you should receive an updated itinerary based on your preferences

### List All Sessions

1. Create a new GET request
2. URL: `{{base_url}}/apps/{{appName}}/users/{{userId}}/sessions`
3. Send the request
4. You'll receive a list of all active sessions for the test user

### Advanced: Create a Postman Collection

For easier testing, create a Postman Collection with the following requests:
1. Create Session
2. Verify Session
3. Initial Trip Query
4. Follow-up Questions (restaurants, activities, etc.)
5. List All Sessions

This will allow you to run through the entire conversation flow with a single click using Postman's Collection Runner.

### Troubleshooting Common Issues

1. **Connection Refused**: Ensure your Trip Planner API server is running on the specified port
2. **404 Not Found**: Verify the endpoint paths are correct
3. **500 Internal Server Error**: Check your server logs for details
4. **Invalid Session ID**: Ensure you're using the correct session ID in your requests

### Testing Different Scenarios

Try these different conversation flows to test the Trip Planner's capabilities:

1. **Budget Travel**: Ask for budget-friendly options for different destinations
2. **Family Travel**: Ask about family-friendly accommodations and activities
3. **Adventure Travel**: Request information about outdoor activities and adventure sports
4. **Food Tourism**: Focus your queries on culinary experiences in different destinations
5. **Multi-City Trips**: Ask for itineraries that include multiple cities or countries
````