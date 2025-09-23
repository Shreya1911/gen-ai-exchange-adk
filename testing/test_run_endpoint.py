#!/usr/bin/env python3
"""
Test script for the /run endpoint of the Trip Planner Agent.
This script creates a session first and then sends a test request to the /run endpoint and displays the response.
"""

import requests
import json
import uuid
import sys
import os
from pprint import pprint

# Base URL of your ADK application - adjust as needed
BASE_URL = "http://localhost:8080"  # Default ADK server port

def check_session_exists(app_name, user_id, session_id):
    """Check if a session exists by getting session info from the server"""
    try:
        print(f"Checking if session {session_id} exists...")
        # Try to get the session info
        response = requests.get(
            f"{BASE_URL}/apps/{app_name}/users/{user_id}/sessions/{session_id}",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"Session {session_id} exists and is valid.")
            return True
        else:
            print(f"Session {session_id} does not exist or is not valid. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error checking session: {e}")
        return False

def get_active_sessions(app_name, user_id):
    """Get a list of active sessions for the user"""
    try:
        print(f"Getting active sessions for user {user_id}...")
        # Try to list all sessions for this user
        response = requests.get(
            f"{BASE_URL}/apps/{app_name}/users/{user_id}/sessions",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            sessions = response.json()
            print(f"Response content: {json.dumps(sessions, indent=2)}")
            
            # Check if response is a list or object and handle accordingly
            if isinstance(sessions, list):
                if sessions and len(sessions) > 0:
                    print(f"Found {len(sessions)} active sessions")
                    # Debug - show session IDs
                    for i, session in enumerate(sessions):
                        session_id = session.get("sessionId")
                        print(f"Session {i+1} ID: {session_id}")
                    return sessions
                else:
                    print("No active sessions found")
                    return []
            elif isinstance(sessions, dict):
                # Some APIs return a dict with a sessions array
                sessions_list = sessions.get("sessions", [])
                if sessions_list and len(sessions_list) > 0:
                    print(f"Found {len(sessions_list)} active sessions")
                    # Debug - show session IDs
                    for i, session in enumerate(sessions_list):
                        session_id = session.get("sessionId")
                        print(f"Session {i+1} ID: {session_id}")
                    return sessions_list
                else:
                    print("No active sessions found")
                    return []
            else:
                print(f"Unexpected response format: {type(sessions)}")
                return []
        else:
            print(f"Failed to get active sessions. Status code: {response.status_code}")
            try:
                error_content = response.json()
                print(f"Error content: {json.dumps(error_content, indent=2)}")
            except:
                print(f"Error content: {response.text}")
            return []
    except Exception as e:
        print(f"Error getting active sessions: {e}")
        return []

def create_session(app_name, user_id):
    """Create a new session and return the session ID"""
    
    # First, try to find existing sessions
    active_sessions = get_active_sessions(app_name, user_id)
    if active_sessions and len(active_sessions) > 0:
        # Use the most recent session
        first_session = active_sessions[0]
        
        # Debug the session object structure
        print(f"First session object: {json.dumps(first_session, indent=2)}")
        
        # Try different common field names for session ID
        possible_id_fields = ["sessionId", "id", "session_id", "session"]
        
        session_id = None
        for field in possible_id_fields:
            if field in first_session:
                session_id = first_session[field]
                print(f"Found session ID in field '{field}': {session_id}")
                break
        
        if not session_id:
            print("WARNING: Couldn't extract session ID from existing session. Creating new one.")
        else:
            print(f"Using existing session: {session_id}")
            return session_id
    
    # Generate a new session ID
    session_id = str(uuid.uuid4())
    
    # Construct the create session payload
    payload = {
        "appName": app_name,
        "userId": user_id,
        "sessionId": session_id,
        # Some ADK implementations might require additional fields
        "description": "Test session created by test_run_endpoint.py"
    }
    
    print(f"Creating new session with ID: {session_id}")
    
    try:
        # Send request to create a session
        response = requests.post(
            f"{BASE_URL}/apps/{app_name}/users/{user_id}/sessions",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful
        response.raise_for_status()
        print(f"Session created successfully: {session_id}")
        
        # Verify session was created
        if check_session_exists(app_name, user_id, session_id):
            return session_id
        else:
            raise Exception("Session was created but verification failed")
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error when creating session: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            try:
                print(f"Response body: {e.response.json()}")
            except json.JSONDecodeError:
                print(f"Response body: {e.response.text}")
        
        # If the error is 409 Conflict, the session might already exist
        if hasattr(e, "response") and e.response is not None and e.response.status_code == 409:
            print(f"Session appears to already exist, verifying: {session_id}")
            if check_session_exists(app_name, user_id, session_id):
                return session_id
        
        raise Exception(f"Failed to create session: {str(e)}")
    except Exception as e:
        print(f"Unexpected error creating session: {e}")
        raise Exception(f"Failed to create session: {str(e)}")

def test_run_endpoint(custom_query=None):
    """Test the /run endpoint with a sample request or custom query."""
    
    # App and user identifiers
    app_name = "agents"  # Using consistent app name throughout the script
    user_id = "test-user"
    
    try:
        # Create a session first
        session_id = create_session(app_name, user_id)
        
        # Verify session exists before proceeding
        if not check_session_exists(app_name, user_id, session_id):
            print(f"ERROR: Session {session_id} could not be verified. Cannot proceed with test.")
            return None
        
        print(f"Session {session_id} verified. Proceeding with API request.")
        
        # Use default query if no custom query is provided
        query_text = custom_query if custom_query else "I want to plan a trip to Paris for 5 days in December."
        
        print(f"Query: {query_text}")
        
        # Construct the request payload according to the API spec
        payload = {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [
                    {
                        "text": query_text
                    }
                ]
            },
            "streaming": False
        }
        
        print(f"Sending request to {BASE_URL}/run:")
        print(json.dumps(payload, indent=2))
        print("\n" + "-"*50 + "\n")
    
    except Exception as e:
        print(f"Failed to setup session: {e}")
        return None
    
    # Send the request to the /run endpoint
    try:
        response = requests.post(
            f"{BASE_URL}/run",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse and print the response
        response_data = response.json()
        print("Response status code:", response.status_code)
        
        # Format and print the response
        format_response_output(response_data, is_complex_query=False)
        return response_data
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            try:
                print(f"Response body: {e.response.json()}")
            except json.JSONDecodeError:
                print(f"Response body: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def test_run_endpoint_with_complex_query(custom_query=None):
    """Test the /run endpoint with a more complex trip planning query or custom query."""
    
    # App and user identifiers
    app_name = "agents"  # Using consistent app name with the other function
    user_id = "test-user"
    
    try:
        # Create a session first
        session_id = create_session(app_name, user_id)
        
        # Verify session exists before proceeding
        if not check_session_exists(app_name, user_id, session_id):
            print(f"ERROR: Session {session_id} could not be verified. Cannot proceed with test.")
            return None
        
        print(f"Session {session_id} verified. Proceeding with API request.")
        
        # Use default complex query if no custom query is provided
        query_text = custom_query if custom_query else ("I want to plan a family trip to Japan for 10 days in April. "
                    "We're interested in experiencing cherry blossom season, visiting historical sites, "
                    "and trying authentic Japanese cuisine. We'd like to visit Tokyo, Kyoto, and possibly one other city. "
                    "Our budget is medium, and we prefer a mix of hotel and traditional ryokan accommodations. "
                    "Please suggest an itinerary.")
        
        print(f"Query: {query_text}")
        
        # Construct a more detailed request
        payload = {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [
                    {
                        "text": query_text
                    }
                ]
            },
            "streaming": False
        }
        
        print(f"Sending complex request to {BASE_URL}/run:")
        print(json.dumps(payload, indent=2))
        print("\n" + "-"*50 + "\n")
    
    except Exception as e:
        print(f"Failed to setup session: {e}")
        return None
    
    # Send the request
    try:
        response = requests.post(
            f"{BASE_URL}/run",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse and print the response
        response_data = response.json()
        print("Response status code:", response.status_code)
        
        # Format and print the response
        format_response_output(response_data, is_complex_query=True)
        return response_data
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            try:
                print(f"Response body: {e.response.json()}")
            except json.JSONDecodeError:
                print(f"Response body: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def format_response_output(response_data, is_complex_query=False):
    """Format and print the response output in a readable way
    
    Args:
        response_data (list): The response data from the API
        is_complex_query (bool): Whether this is a complex query response
    """
    query_type = "COMPLEX QUERY" if is_complex_query else "STANDARD QUERY"
    print("\n" + "="*80)
    print(f"TRIP PLANNER AGENT RESPONSE ({query_type})")
    print("="*80)
    
    for event_idx, event in enumerate(response_data):
        if "content" in event and event["content"] is not None:
            role = event["content"].get("role", "")
            if role == "model":
                if "parts" in event["content"] and event["content"]["parts"]:
                    for part_idx, part in enumerate(event["content"]["parts"]):
                        # Process text content
                        if "text" in part and part["text"]:
                            print(f"\n{part['text']}")
                        
                        # Process tool calls if they exist
                        if "function_call" in part:
                            tool = part["function_call"]
                            print(f"\n🛠️ TOOL USED: {tool.get('name', 'Unknown Tool')}")
                            print("-" * 40)
                            try:
                                args = json.loads(tool.get("args", "{}"))
                                print(json.dumps(args, indent=2))
                            except:
                                print(tool.get("args", "{}"))
                            print("-" * 40)
                        
                        # For any other types of parts
                        for key, value in part.items():
                            if key not in ["text", "function_call"] and value is not None:
                                print(f"\n▶️ {key.upper()}:")
                                print("-" * 40)
                                try:
                                    if isinstance(value, dict) or isinstance(value, list):
                                        print(json.dumps(value, indent=2))
                                    else:
                                        print(value)
                                except:
                                    print(value)
                                print("-" * 40)
    
    print("\n" + "="*80 + "\n")


def list_sessions():
    """List all available sessions for the test user"""
    app_name = "agents"  # Using consistent app name throughout the script
    user_id = "test-user"
    
    try:
        sessions = get_active_sessions(app_name, user_id)
        if sessions and len(sessions) > 0:
            print(f"\nFound {len(sessions)} active sessions:")
            for i, session in enumerate(sessions):
                # Try different possible field names for session ID and creation time
                session_id = None
                for field in ["sessionId", "id", "session_id", "session"]:
                    if field in session:
                        session_id = session[field]
                        break
                
                created_at = None
                for field in ["createdAt", "created_at", "timestamp", "creationTime"]:
                    if field in session:
                        created_at = session[field]
                        break
                
                session_id = session_id or "Unknown"
                created_at = created_at or "Unknown"
                
                print(f"{i+1}. Session ID: {session_id}")
                print(f"   Created: {created_at}")
                print(f"   Full session data: {json.dumps(session, indent=2)}")
                print()
            return True
        else:
            print("\nNo active sessions found.")
            return False
    except Exception as e:
        print(f"Error listing sessions: {e}")
        return False


def use_manual_session(app_name, user_id, session_id):
    """Test using a manually specified session ID"""
    if not session_id:
        print("ERROR: No session ID provided")
        return None
    
    print(f"Using manually specified session ID: {session_id}")
    
    # Verify session exists before proceeding
    if check_session_exists(app_name, user_id, session_id):
        return session_id
    else:
        print(f"ERROR: Manually specified session {session_id} could not be verified.")
        return None

def create_fresh_session(custom_query=None):
    """Create a fresh session and test with it, optionally with a custom query"""
    # App and user identifiers
    app_name = "agents"  # Use consistent app name
    user_id = "test-user"
    
    try:
        # Generate a completely new UUID for the session
        session_id = str(uuid.uuid4())
        print(f"Creating fresh session with ID: {session_id}")
        
        # Construct the create session payload
        payload = {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "description": "Fresh test session created by test_run_endpoint.py"
        }
        
        # Send request to create a session
        response = requests.post(
            f"{BASE_URL}/apps/{app_name}/users/{user_id}/sessions",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful
        response.raise_for_status()
        print(f"Fresh session created successfully: {session_id}")
        
        # Verify session exists
        if check_session_exists(app_name, user_id, session_id):
            print(f"Session {session_id} verified. Proceeding with test.")
            # Run the test with the fresh session
            test_with_specific_session(app_name, user_id, session_id, custom_query)
        else:
            print(f"ERROR: Fresh session {session_id} could not be verified.")
    except Exception as e:
        print(f"Failed to create fresh session: {e}")


def test_with_specific_session(app_name, user_id, session_id, custom_query=None):
    """Run a test with a specific session ID and optional custom query"""
    if not session_id:
        print("ERROR: No session ID provided")
        return
    
    print(f"Testing with session ID: {session_id}")
    
    # Use default query if no custom query is provided
    query_text = custom_query if custom_query else "I want to plan a trip to Paris for 5 days in December."
    
    print(f"Query: {query_text}")
    
    # Construct the request payload
    payload = {
        "appName": app_name,
        "userId": user_id,
        "sessionId": session_id,
        "newMessage": {
            "role": "user",
            "parts": [
                {
                    "text": query_text
                }
            ]
        },
        "streaming": False
    }
    
    print(f"Sending request to {BASE_URL}/run:")
    print(json.dumps(payload, indent=2))
    print("\n" + "-"*50 + "\n")
    
    # Send the request
    try:
        response = requests.post(
            f"{BASE_URL}/run",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse and print the response
        response_data = response.json()
        print("Response status code:", response.status_code)
        
        # Format and print the response
        format_response_output(response_data, is_complex_query=False)
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            try:
                print(f"Response body: {e.response.json()}")
            except json.JSONDecodeError:
                print(f"Response body: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def create_fresh_session_and_return_id():
    """Create a fresh session and return the session ID"""
    app_name = "agents"  # Use consistent app name
    user_id = "test-user"
    
    try:
        # Generate a completely new UUID for the session
        session_id = str(uuid.uuid4())
        print(f"Creating fresh session with ID: {session_id}")
        
        # Construct the create session payload
        payload = {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "description": "Fresh test session created by test_run_endpoint.py"
        }
        
        # Send request to create a session
        response = requests.post(
            f"{BASE_URL}/apps/{app_name}/users/{user_id}/sessions",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful
        response.raise_for_status()
        print(f"Fresh session created successfully: {session_id}")
        
        # Verify session exists
        if check_session_exists(app_name, user_id, session_id):
            print(f"Session {session_id} verified.")
            return session_id
        else:
            print(f"ERROR: Fresh session {session_id} could not be verified.")
            return None
    except Exception as e:
        print(f"Failed to create fresh session: {e}")
        return None


def test_with_complex_query_and_session(app_name, user_id, session_id, custom_query=None):
    """Run a complex query with a specific session ID and optional custom query"""
    if not session_id:
        print("ERROR: No session ID provided for complex query")
        return
    
    print(f"Running complex query with session ID: {session_id}")
    
    # Use default complex query if no custom query is provided
    query_text = custom_query if custom_query else ("I want to plan a family trip to Japan for 10 days in April. "
                    "We're interested in experiencing cherry blossom season, visiting historical sites, "
                    "and trying authentic Japanese cuisine. We'd like to visit Tokyo, Kyoto, and possibly one other city. "
                    "Our budget is medium, and we prefer a mix of hotel and traditional ryokan accommodations. "
                    "Please suggest an itinerary.")
    
    print(f"Query: {query_text}")
    
    # Construct a complex request payload
    payload = {
        "appName": app_name,
        "userId": user_id,
        "sessionId": session_id,
        "newMessage": {
            "role": "user",
            "parts": [
                {
                    "text": query_text
                }
            ]
        },
        "streaming": False
    }
    
    print(f"Sending complex request to {BASE_URL}/run:")
    print(json.dumps(payload, indent=2))
    print("\n" + "-"*50 + "\n")
    
    # Send the request
    try:
        response = requests.post(
            f"{BASE_URL}/run",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful
        response.raise_for_status()
        print("Response received successfully!")
        
        # Format and print the response
        response_data = response.json()
        format_response_output(response_data, is_complex_query=True)
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            try:
                print(f"Response body: {e.response.json()}")
            except json.JSONDecodeError:
                print(f"Response body: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    print("Trip Planner Agent API Test")
    print("==========================")
    
    # Parse command line arguments and options
    args = sys.argv[1:]
    use_complex = False
    use_fresh = True  # Default is now using fresh session
    session_id = None
    custom_query = None  # To store user-provided question
    
    # Check if help is requested
    if "--help" in args or "-h" in args:
        print("Trip Planner Agent API Test Tool")
        print("==============================")
        print("\nUsage: python test_run_endpoint.py [OPTIONS] [--question \"Your query text here\"]")
        print("\nOptions:")
        print("  --complex           Run the complex trip planning query test")
        print("                      (10-day Japan trip with cherry blossoms)")
        print("  --list-sessions     List all active sessions for the test user")
        print("  --session <id>      Use a specific session ID for testing")
        print("  --fresh             Create a fresh session and test with it")
        print("  --no-fresh          Use existing session (don't create a fresh one)")
        print("  --question \"text\"   Specify a custom question to ask the agent")
        print("  --help, -h          Display this help message")
        print("\nDefault behavior:")
        print("  Uses a fresh session and runs a simple trip planning query test (5-day Paris trip)")
        print("  Multiple options can be combined (e.g., --complex --fresh)")
        print("\nExamples:")
        print("  python test_run_endpoint.py --question \"What are good places to visit in Rome?\"")
        print("  python test_run_endpoint.py --fresh --question \"What should I pack for a beach vacation?\"")
        print("  python test_run_endpoint.py --session abc123 --question \"Is Tokyo expensive to visit?\"")
        print("\nOutput formatting:")
        print("  The test tool will format the agent's response to show:")
        print("  - Main text content from the agent")
        print("  - Any tools that were called by the agent")
        print("  - Other relevant response data in a readable format")
        sys.exit(0)
    
    # Process arguments
    if args:
        if "--list-sessions" in args:
            list_sessions()
            sys.exit(0)
        
        # Parse other flags
        if "--complex" in args:
            use_complex = True
        
        if "--no-fresh" in args:
            use_fresh = False
        
        # Extract arguments that require values
        i = 0
        while i < len(args):
            if args[i] == "--session" and i + 1 < len(args):
                session_id = args[i + 1]
                i += 2  # Skip the next argument as it's the session ID
            elif args[i] == "--question" and i + 1 < len(args):
                custom_query = args[i + 1]
                i += 2  # Skip the next argument as it's the question text
            else:
                i += 1  # Move to the next argument
    
    # Execute based on parsed options
    if session_id:
        app_name = "agents"  # Use consistent app name
        user_id = "test-user"
        test_with_specific_session(app_name, user_id, session_id, custom_query)
    elif use_fresh:
        if use_complex:
            # Create fresh session and run complex query
            app_name = "agents"
            user_id = "test-user"
            session_id = create_fresh_session_and_return_id()
            if session_id:
                # Use this session with complex query
                test_with_complex_query_and_session(app_name, user_id, session_id, custom_query)
            else:
                print("Failed to create fresh session for complex query")
        else:
            create_fresh_session(custom_query)
    else:
        if use_complex:
            if custom_query:
                # Run the complex query workflow with a custom query
                app_name = "agents"
                user_id = "test-user"
                # Create a session or use existing one
                session_id = create_session(app_name, user_id)
                test_with_complex_query_and_session(app_name, user_id, session_id, custom_query)
            else:
                test_run_endpoint_with_complex_query()
        else:
            if custom_query:
                # Run the simple query workflow with a custom query
                app_name = "agents"
                user_id = "test-user"
                # Create a session or use existing one
                session_id = create_session(app_name, user_id)
                test_with_specific_session(app_name, user_id, session_id, custom_query)
            else:
                test_run_endpoint()