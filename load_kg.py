import json
from neo4j_connection import neo4j_conn

# Load KG data from the JSON file
with open("kg_output/kg_elements.json", "r") as file:
    kg_data = json.load(file)

def insert_nodes():
    for node in kg_data["nodes"]:
        query = """
        MERGE (n {id: $id})
        SET n.label = $label, n.name = $name
        """
        if "path" in node:
            query += ", n.path = $path"
        if "type" in node:
            query += ", n.type = $type"

        neo4j_conn.run_query(query, node)

def insert_relationships():
    for rel in kg_data["relationships"]:
        query = """
        MATCH (a {id: $source}), (b {id: $target})
        MERGE (a)-[r:RELATION {type: $type}]->(b)
        """
        neo4j_conn.run_query(query, rel)

if __name__ == "__main__":
    insert_nodes()
    insert_relationships()
    print("✅ KG inserted into Neo4j successfully!")
    neo4j_conn.close()
