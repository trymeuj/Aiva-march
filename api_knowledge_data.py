# api_knowledge_data.py

API_KNOWLEDGE = {
    "apis": {
        "add_professors": {
            "path": "/api/addprof",
            "method": "POST",
            "description": "Adds professors to a department. If the department doesn't exist, it creates a new department and adds the professors.",
            "parameters": [
                {
                    "name": "departmentName",
                    "type": "string",
                    "required": True,
                    "description": "The name of the department to add professors to."
                },
                {
                    "name": "professorName",
                    "type": "array",
                    "required": True,
                    "description": "An array of professor names to add to the department."
                }
            ],
            "returns": {
                "type": "object",
                "description": "Returns a success message and the updated department object if professors were added successfully",
                "structure": {
                    "message": "string",
                    "addedProfessors": "array",
                    "department": "object"
                }
            },
            "category": "Department Management",
            "intent_keywords": ["add", "professor", "department", "create", "new", "faculty"]
        },
        
        "process_user_input": {
            "path": "/api/agent",
            "method": "POST",
            "description": "Processes user input to either create a post or fetch course details using the Gemini AI model.",
            "parameters": [
                {
                    "name": "inputText",
                    "type": "string",
                    "required": True,
                    "description": "User input text for processing."
                }
            ],
            "returns": {
                "type": "object",
                "description": "Returns either a Gemini AI response or course data based on the intent",
                "structure": {
                    "message": "string"
                }
            },
            "category": "AI Interaction",
            "intent_keywords": ["process", "input", "query", "ask", "question", "ai", "help"]
        },
        
        "get_course_ratings": {
            "path": "/api/allcourseRatings",
            "method": "GET",
            "description": "Retrieves and calculates average course ratings by professor for all unique courses.",
            "parameters": [],
            "returns": {
                "type": "array",
                "description": "An array of course ratings with details",
                "structure": {
                    "courseCategory": "string",
                    "courseCode": "string",
                    "profName": "string",
                    "averageRating": "number",
                    "mostFrequentAttendance": "string"
                }
            },
            "category": "Course Information",
            "intent_keywords": ["get", "course", "ratings", "professor", "average", "view", "rating"]
        },
        
        "get_general_posts": {
            "path": "/api/allgeneralposts",
            "method": "GET",
            "description": "Retrieves all posts, optionally filtered by postType.",
            "parameters": [
                {
                    "name": "postType",
                    "type": "string",
                    "required": False,
                    "description": "The type of post to retrieve."
                }
            ],
            "returns": {
                "type": "array",
                "description": "An array of GeneralPost objects",
                "structure": {
                    "username": "string",
                    "postType": "string",
                    "title": "string",
                    "content": "string"
                }
            },
            "category": "Post Management",
            "intent_keywords": ["get", "retrieve", "posts", "view", "all", "general", "list"]
        },
        
        "create_general_post": {
            "path": "/api/allgeneralposts",
            "method": "POST",
            "description": "Creates a new post.",
            "parameters": [
                {
                    "name": "title",
                    "type": "string",
                    "required": True,
                    "description": "The title of the post."
                },
                {
                    "name": "postType",
                    "type": "string",
                    "required": True,
                    "description": "The type of the post."
                },
                {
                    "name": "content",
                    "type": "string",
                    "required": True,
                    "description": "The content of the post."
                },
                {
                    "name": "tags",
                    "type": "array",
                    "required": True,
                    "description": "An array of tags for the post."
                },
                {
                    "name": "image",
                    "type": "File",
                    "required": False,
                    "description": "An image file to upload."
                }
            ],
            "returns": {
                "type": "object",
                "description": "Confirmation message and the created post object",
                "structure": {
                    "message": "string",
                    "post": "object"
                }
            },
            "category": "Post Management",
            "intent_keywords": ["create", "post", "new", "add", "write", "publish"]
        },
        
        "get_all_posts": {
            "path": "/api/allposts",
            "method": "GET",
            "description": "Retrieves all posts from the database.",
            "parameters": [],
            "returns": {
                "type": "array",
                "description": "An array of posts, reversed in order",
                "structure": {
                    "_id": "string",
                    "username": "string",
                    "courseCategory": "string",
                    "courseCode": "string",
                    "prof": "string",
                    "content": "string"
                }
            },
            "category": "Post Management",
            "intent_keywords": ["get", "all", "posts", "view", "list", "show"]
        },
        
        "create_post": {
            "path": "/api/allposts",
            "method": "POST",
            "description": "Creates a new post.",
            "parameters": [
                {
                    "name": "courseCategory",
                    "type": "string",
                    "required": True,
                    "description": "The category of the course."
                },
                {
                    "name": "courseCode",
                    "type": "string",
                    "required": True,
                    "description": "The code of the course."
                },
                {
                    "name": "prof",
                    "type": "string",
                    "required": True,
                    "description": "The professor of the course."
                },
                {
                    "name": "content",
                    "type": "string",
                    "required": True,
                    "description": "The content of the post."
                }
            ],
            "returns": {
                "type": "object",
                "description": "Confirmation of post creation or error message",
                "structure": {
                    "message": "string",
                    "post": "object"
                }
            },
            "category": "Post Management",
            "intent_keywords": ["create", "post", "new", "add", "course", "professor"]
        },
        
        "get_professors": {
            "path": "/api/allprof",
            "method": "POST",
            "description": "Retrieves a list of professors belonging to a specific department.",
            "parameters": [
                {
                    "name": "departmentName",
                    "type": "string",
                    "required": True,
                    "description": "The name of the department to retrieve professors from."
                }
            ],
            "returns": {
                "type": "object",
                "description": "Returns a list of professors for the specified department",
                "structure": {
                    "professors": "array"
                }
            },
            "category": "Department Management",
            "intent_keywords": ["get", "professors", "department", "faculty", "list"]
        },
        
        "login": {
            "path": "/api/auth/login",
            "method": "POST",
            "description": "Logs in a user by verifying their username and password and sets a JWT token as a cookie.",
            "parameters": [
                {
                    "name": "username",
                    "type": "string",
                    "required": True,
                    "description": "The user's username."
                },
                {
                    "name": "password",
                    "type": "string",
                    "required": True,
                    "description": "The user's password."
                }
            ],
            "returns": {
                "type": "object",
                "description": "Returns a cookie containing a JWT token upon successful login, or an error message",
                "structure": {
                    "message": "string"
                }
            },
            "category": "Authentication",
            "intent_keywords": ["login", "sign in", "authenticate", "access", "account"]
        },
        
        "logout": {
            "path": "/api/auth/logout",
            "method": "DELETE",
            "description": "Logs out the user by deleting the authentication token cookie and redirecting to the login/signup page.",
            "parameters": [],
            "returns": {
                "type": "object",
                "description": "Redirects to /loginSignup and deletes the 'token' cookie",
                "structure": {
                    "redirect": "string"
                }
            },
            "category": "Authentication",
            "intent_keywords": ["logout", "sign out", "exit", "end session"]
        },
        
        "signup": {
            "path": "/api/auth/signup",
            "method": "POST",
            "description": "Handles user signup by creating a new user in the database, hashing the password, and setting a JWT cookie.",
            "parameters": [
                {
                    "name": "username",
                    "type": "string",
                    "required": True,
                    "description": "The username for the new user."
                },
                {
                    "name": "password",
                    "type": "string",
                    "required": True,
                    "description": "The password for the new user."
                }
            ],
            "returns": {
                "type": "object",
                "description": "Returns a success message and sets a cookie upon successful signup, or an error message if signup fails",
                "structure": {
                    "message": "string",
                    "token": "string"
                }
            },
            "category": "Authentication",
            "intent_keywords": ["signup", "register", "create account", "new user", "join"]
        },
        
        "flag_post": {
            "path": "/api/flagPost",
            "method": "POST",
            "description": "Flags a post by incrementing its flagCount.",
            "parameters": [
                {
                    "name": "userId",
                    "type": "string",
                    "required": True,
                    "description": "The ID of the post to flag."
                }
            ],
            "returns": {
                "type": "object",
                "description": "Response indicating success or failure, and the updated post if successful",
                "structure": {
                    "message": "string",
                    "post": "object"
                }
            },
            "category": "Post Management",
            "intent_keywords": ["flag", "report", "post", "inappropriate", "mark"]
        },
        
        "get_username": {
            "path": "/api/getUsername",
            "method": "POST",
            "description": "Fetches username from a valid token.",
            "parameters": [],
            "returns": {
                "type": "object",
                "description": "Success response with a message and username or error message",
                "structure": {
                    "message": "string",
                    "username": "string"
                }
            },
            "category": "User Management",
            "intent_keywords": ["get", "username", "user", "profile", "who am i"]
        },
        
        "check_upvote_status": {
            "path": "/api/isupvotedornot",
            "method": "POST",
            "description": "Checks if a user has upvoted a specific post.",
            "parameters": [
                {
                    "name": "postId",
                    "type": "string",
                    "required": True,
                    "description": "The ID of the post to check for upvote status."
                }
            ],
            "returns": {
                "type": "object",
                "description": "Indicates whether the user has upvoted the post",
                "structure": {
                    "message": "string",
                    "hasUpvoted": "boolean"
                }
            },
            "category": "Post Management",
            "intent_keywords": ["check", "upvote", "status", "liked", "voted"]
        },
        
        "get_user_profile": {
            "path": "/api/profile",
            "method": "POST",
            "description": "Fetches user posts based on the token provided in the cookies. Requires a valid token.",
            "parameters": [],
            "returns": {
                "type": "object",
                "description": "Returns user's posts if the token is valid and posts exist for the user",
                "structure": {
                    "message": "string",
                    "username": "string",
                    "posts": "array"
                }
            },
            "category": "User Management",
            "intent_keywords": ["profile", "my posts", "user", "my account", "my profile"]
        },
        
        "rate_course": {
            "path": "/api/rate",
            "method": "POST",
            "description": "Creates a new rate card for a course.",
            "parameters": [
                {
                    "name": "courseCategory",
                    "type": "string",
                    "required": True,
                    "description": "The category of the course."
                },
                {
                    "name": "courseCode",
                    "type": "string",
                    "required": True,
                    "description": "The code of the course."
                },
                {
                    "name": "profName",
                    "type": "string",
                    "required": True,
                    "description": "The name of the professor."
                },
                {
                    "name": "starRating",
                    "type": "number",
                    "required": True,
                    "description": "The star rating of the course."
                },
                {
                    "name": "attendance",
                    "type": "string",
                    "required": True,
                    "description": "The attendance policy of the course."
                },
                {
                    "name": "courseContent",
                    "type": "string",
                    "required": True,
                    "description": "The content of the course."
                },
                {
                    "name": "gradingPolicy",
                    "type": "string",
                    "required": True,
                    "description": "The grading policy of the course."
                },
                {
                    "name": "gradeAvg",
                    "type": "number",
                    "required": True,
                    "description": "The average grade of the course."
                },
                {
                    "name": "auditgrade",
                    "type": "string",
                    "required": False,
                    "description": "The audit grade of the course."
                }
            ],
            "returns": {
                "type": "object",
                "description": "Response object containing a success message and the created rate card, or an error message",
                "structure": {
                    "message": "string",
                    "rateCard": "object"
                }
            },
            "category": "Course Management",
            "intent_keywords": ["rate", "course", "rating", "review", "feedback", "grade", "professor"]
        },
        
        "search_courses": {
            "path": "/api/search",
            "method": "POST",
            "description": "Handles search queries for course information. Processes the search query and retrieves relevant data based on the course category and course code provided.",
            "parameters": [
                {
                    "name": "searchQuery",
                    "type": "string",
                    "required": True,
                    "description": "The search query string, expected to be in the format 'courseCategory courseCode' or just 'courseCategory'."
                }
            ],
            "returns": {
                "type": "object",
                "description": "Returns an array of objects containing course information and average ratings based on the search query",
                "structure": {
                    "rateCard": "object",
                    "posts": "array"
                }
            },
            "category": "Course Information",
            "intent_keywords": ["search", "find", "course", "query", "lookup", "browse"]
        },
        
        "upvote_post": {
            "path": "/api/upvotegeneralposts",
            "method": "POST",
            "description": "Handles upvoting or un-upvoting a post. Requires authentication via a token in a cookie.",
            "parameters": [
                {
                    "name": "postId",
                    "type": "string",
                    "required": True,
                    "description": "The ID of the post to upvote or un-upvote."
                }
            ],
            "returns": {
                "type": "object",
                "description": "Response indicating success or failure, including the updated upvote count and whether the user has upvoted",
                "structure": {
                    "message": "string",
                    "upvotes": "array",
                    "hasUpvoted": "boolean"
                }
            },
            "category": "Post Management",
            "intent_keywords": ["upvote", "like", "support", "vote", "thumbs up"]
        },
        
        "verify_user": {
            "path": "/api/verificationForCreatePost",
            "method": "POST",
            "description": "Handles user sign-in verification using a token.",
            "parameters": [],
            "returns": {
                "type": "object",
                "description": "Success or error message",
                "structure": {
                    "message": "string"
                }
            },
            "category": "Authentication",
            "intent_keywords": ["verify", "check", "authentication", "signed in", "logged in"]
        }
    }
}