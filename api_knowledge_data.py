# api_knowledge_data.py

API_KNOWLEDGE = {
    "apis": {
        "post__signup": {
            "path": "/signup",
            "method": "POST",
            "description": "Registers a new user in the system with the provided credentials.",
            "parameters": [],
            "returns": {
                "type": "object",
                "description": "Response from the endpoint",
                "structure": {},
            },
            "category": "API Endpoint",
            "intent_keywords": [
                "post",
                "signup",
            ],
        },
        "post__login": {
            "path": "/login",
            "method": "POST",
            "description": "Authenticates a user and issues an access token for authorized API access.",
            "parameters": [],
            "returns": {
                "type": "object",
                "description": "Response from the endpoint",
                "structure": {},
            },
            "category": "API Endpoint",
            "intent_keywords": [
                "post",
                "login",
            ],
        },
        "post__createcourse": {
            "path": "/createcourse",
            "method": "POST",
            "description": "Creates a new course with the provided details and content structure.",
            "parameters": [
                {
                    "name": "coursename",
                    "type": "string",
                    "required": True,
                    "description": "The name of the course (required)",
                },
                {
                    "name": "courseid",
                    "type": "string",
                    "required": True,
                    "description": "The unique identifier for the course (required)",
                },
            ],
            "returns": {
                "type": "object",
                "description": "*   Status Codes: *   200 OK - Course created successfully. *   `msg` (string) - Confirmation message indicating successful course creation, e.g., \"course [coursename] created by [admin email]\". ",
                "structure": {},
            },
            "category": "API Endpoint",
            "intent_keywords": [
                "post",
                "createcourse",
            ],
        },
        "delete__deletecourse": {
            "path": "/deletecourse",
            "method": "DELETE",
            "description": "Removes the specified deletecourse record from the system.",
            "parameters": [
                {
                    "name": "courseid",
                    "type": "string",
                    "required": True,
                    "description": "The unique identifier of the course to be deleted (required)",
                },
            ],
            "returns": {
                "type": "object",
                "description": "*   Status Codes: *   200 OK - Course deleted successfully. *   `msg` (string) - Confirmation message indicating successful course deletion, e.g., \"course [courseid] deleted by [admin email]\". ",
                "structure": {},
            },
            "category": "API Endpoint",
            "intent_keywords": [
                "delete",
                "deletecourse",
            ],
        },
        "put__addcontent": {
            "path": "/addcontent",
            "method": "PUT",
            "description": "Updates an existing addcontent record with new information.",
            "parameters": [
                {
                    "name": "coursename",
                    "type": "string",
                    "required": True,
                    "description": "The new name of the course (required)",
                },
                {
                    "name": "courseid",
                    "type": "string",
                    "required": True,
                    "description": "The unique identifier of the course to be updated (required)",
                },
            ],
            "returns": {
                "type": "object",
                "description": "*   Status Codes: *   200 OK - Course updated successfully. *   `msg` (string) - Confirmation message indicating successful course update, e.g., \"course [courseid] has been updated\". ",
                "structure": {},
            },
            "category": "API Endpoint",
            "intent_keywords": [
                "put",
                "addcontent",
            ],
        },
        "get__allcourses": {
            "path": "/allcourses",
            "method": "GET",
            "description": "Retrieves course information, possibly filtered by specific criteria.",
            "parameters": [],
            "returns": {
                "type": "object",
                "description": "Response from the endpoint",
                "structure": {},
            },
            "category": "API Endpoint",
            "intent_keywords": [
                "get",
                "allcourses",
            ],
        },
        "post__purchase": {
            "path": "/purchase",
            "method": "POST",
            "description": "Processes a purchase or enrollment request for a specified item or course.",
            "parameters": [],
            "returns": {
                "type": "object",
                "description": "Response from the endpoint",
                "structure": {},
            },
            "category": "API Endpoint",
            "intent_keywords": [
                "post",
                "purchase",
            ],
        },
        "get__mycourses": {
            "path": "/mycourses",
            "method": "GET",
            "description": "Retrieves course information, possibly filtered by specific criteria.",
            "parameters": [],
            "returns": {
                "type": "object",
                "description": "Response from the endpoint",
                "structure": {},
            },
            "category": "API Endpoint",
            "intent_keywords": [
                "get",
                "mycourses",
            ],
        },
    },
}