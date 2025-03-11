from neo4j import GraphDatabase

# to establish the connection   
# Update these values with your Neo4j credentials
NEO4J_URI = "bolt://localhost:7687"  # Change if hosted remotely
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "qwerty123456"

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        with self.driver.session() as session:
            return session.run(query, parameters)

# Create a connection instance
neo4j_conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
