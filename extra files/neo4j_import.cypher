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
        