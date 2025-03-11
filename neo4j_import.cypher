CREATE (:File {id: "agent_py", name: "agent.py", path: "C:\\Users\\ujjwa\\Desktop\\learning\\Agents\\flightagent\\backend\\agent.py", type: "utility"})
CREATE (:Function {id: "parse_user_query", name: "parse_user_query"})
CREATE (:Parameter {id: "parse_user_query_the", name: "the"})
CREATE (:DataStructure {id: "parse_user_query_return_intent", name: "intent"})
CREATE (:DataStructure {id: "parse_user_query_return_extracted", name: "extracted"})
CREATE (:DataStructure {id: "input_data", name: "input_data"})
CREATE (:DataStructure {id: "graph", name: "graph"})
CREATE (:Library {id: "google_generativeai", name: "google.generativeai"})
CREATE (:Library {id: "langgraph", name: "langgraph"})
CREATE (:Library {id: "json", name: "json"})
CREATE (:Library {id: "os", name: "os"})
CREATE (:Library {id: "api_calls", name: "api_calls"})
CREATE (:DataFlow {id: "input", name: "Input"})
CREATE (:File {id: "route_ts", name: "route.ts", path: "C:\\Users\\ujjwa\\Desktop\\learning\\dev\\IITD_Forum\\IITD-Forum\\src\\app\\api\\addprof\\route.ts", type: "utility"})
CREATE (:Function {id: "post", name: "POST"})
CREATE (:DataStructure {id: "post_return_response", name: "response"})
CREATE (:DataStructure {id: "post_return_nextresponse", name: "NextResponse"})
CREATE (:DataStructure {id: "addprofessorrequest", name: "AddProfessorRequest"})
CREATE (:Service {id: "error_handling", name: "Error Handling"})
CREATE (:Function {id: "get", name: "GET"})
CREATE (:DataStructure {id: "get_return_formatted", name: "formatted"})
CREATE (:DataStructure {id: "get_return_500", name: "500"})
CREATE (:DataStructure {id: "get_return_professor", name: "professor"})
CREATE (:DataStructure {id: "uniquecourses", name: "uniqueCourses"})
CREATE (:DataStructure {id: "ratings", name: "ratings"})
CREATE (:DataStructure {id: "profratings", name: "profRatings"})
CREATE (:API {id: "api_endpoint", name: "API Endpoint"})
CREATE (:DataStructure {id: "get_return_retrieved", name: "retrieved"})
CREATE (:DataStructure {id: "get_return_401", name: "401"})
CREATE (:DataStructure {id: "get_return_400", name: "400"})
CREATE (:DataStructure {id: "get_return_201", name: "201"})
CREATE (:DataStructure {id: "get_return_502", name: "502"})
CREATE (:DataStructure {id: "get_return_buffer", name: "Buffer"})
CREATE (:Service {id: "mongodb_database", name: "MongoDB Database"})
CREATE (:DataStructure {id: "get_return_reversed", name: "reversed"})
CREATE (:Service {id: "database", name: "Database"})
CREATE (:DataStructure {id: "post_return_http", name: "HTTP"})
CREATE (:DataStructure {id: "body", name: "body"})
CREATE (:DataStructure {id: "post_return_400", name: "400"})
CREATE (:DataStructure {id: "user", name: "User"})
CREATE (:Library {id: "bcrypt", name: "bcrypt"})
CREATE (:Library {id: "generatetokenandsetcookie", name: "generateTokenAndSetCookie"})
CREATE (:Function {id: "delete", name: "DELETE"})
CREATE (:DataStructure {id: "delete_return_redirect", name: "redirect"})
CREATE (:DataStructure {id: "delete_return_json", name: "JSON"})
CREATE (:DataStructure {id: "request", name: "Request"})
CREATE (:DataStructure {id: "nextresponse", name: "NextResponse"})
CREATE (:DataStructure {id: "cookiestore", name: "cookieStore"})
CREATE (:Library {id: "process_env_node_env", name: "process.env.NODE_ENV"})
CREATE (:Service {id: "authentication_system", name: "Authentication System"})
CREATE INDEX ON :File(id)
CREATE INDEX ON :Function(id)
CREATE INDEX ON :Library(id)
CREATE INDEX ON :DataStructure(id)

        MATCH (a), (b)
        WHERE a.id = "agent_py" AND b.id = "parse_user_query"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "parse_user_query" AND b.id = "parse_user_query_the"
        CREATE (a)-[:ACCEPTS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "parse_user_query" AND b.id = "parse_user_query_return_intent"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "parse_user_query" AND b.id = "parse_user_query_return_extracted"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "agent_py" AND b.id = "input_data"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "agent_py" AND b.id = "graph"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "agent_py" AND b.id = "google_generativeai"
        CREATE (a)-[:IMPORTS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "agent_py" AND b.id = "langgraph"
        CREATE (a)-[:IMPORTS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "agent_py" AND b.id = "json"
        CREATE (a)-[:IMPORTS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "agent_py" AND b.id = "os"
        CREATE (a)-[:IMPORTS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "agent_py" AND b.id = "api_calls"
        CREATE (a)-[:IMPORTS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "agent_py" AND b.id = "input"
        CREATE (a)-[:CALLS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "parse_user_query" AND b.id = "input"
        CREATE (a)-[:CALLS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "post"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "post" AND b.id = "post_return_response"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "post" AND b.id = "post_return_nextresponse"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "addprofessorrequest"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "error_handling"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "post"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "get"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "get_return_formatted"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "get_return_500"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "get_return_professor"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "uniquecourses"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "ratings"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "profratings"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "api_endpoint"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "api_endpoint"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "get"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "get_return_retrieved"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "get_return_401"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "get_return_400"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "get_return_201"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "get_return_502"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "get_return_buffer"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "mongodb_database"
        CREATE (a)-[:INTERACTS_WITH]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "get"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "get_return_reversed"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "get_return_401"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "get_return_401"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "get_return_400"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "get_return_201"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "get_return_502"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "post"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "database"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "get" AND b.id = "database"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "post"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "post" AND b.id = "post_return_http"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "body"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "error_handling"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "post"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "post" AND b.id = "post_return_400"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "user"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "bcrypt"
        CREATE (a)-[:IMPORTS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "generatetokenandsetcookie"
        CREATE (a)-[:IMPORTS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "error_handling"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "delete"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "delete" AND b.id = "delete_return_redirect"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "delete" AND b.id = "delete_return_json"
        CREATE (a)-[:RETURNS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "request"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "nextresponse"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "cookiestore"
        CREATE (a)-[:CONTAINS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "process_env_node_env"
        CREATE (a)-[:IMPORTS]->(b)
        

        MATCH (a), (b)
        WHERE a.id = "route_ts" AND b.id = "authentication_system"
        CREATE (a)-[:USES]->(b)
        

        MATCH (n)
        WHERE n.id = "addprofessorrequest"
        SET n.properties = ["properties", "like"]
        

        MATCH (n)
        WHERE n.id = "uniquecourses"
        SET n.properties = ["properties", "like"]
        

        MATCH (n)
        WHERE n.id = "ratings"
        SET n.properties = ["properties", "like"]
        

        MATCH (n)
        WHERE n.id = "profratings"
        SET n.properties = ["average", "ratings", "related", "information", "specific", "course", "grouped", "professor"]
        

        MATCH (n)
        WHERE n.id = "post"
        SET n.properties = ["user", "information", "extracted", "token", "such"]
        

        MATCH (n)
        WHERE n.id = "user"
        SET n.properties = ["function", "responsible", "generating", "token"]
        

        MATCH (n)
        WHERE n.id = "request"
        SET n.properties = ["information", "about", "request", "such", "URL", "headers", "body"]
        