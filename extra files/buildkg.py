import json
from neo4j import GraphDatabase
import os
import argparse

# build KG from elements
class Neo4jKnowledgeGraphCreator:
    """
    Create a Knowledge Graph in Neo4j from extracted code elements.
    """
    
    def __init__(self, uri, username, password):
        """
        Initialize the Neo4j connection.
        
        Args:
            uri: Neo4j server URI (e.g., "bolt://localhost:7687")
            username: Neo4j username
            password: Neo4j password
        """
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def close(self):
        """Close the Neo4j connection."""
        self.driver.close()
    
    def clear_database(self):
        """Clear all nodes and relationships from the database."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Database cleared.")
    
    def create_constraints_and_indexes(self):
        """Create constraints and indexes for better performance."""
        with self.driver.session() as session:
            # Create constraints for uniqueness
            try:
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:File) REQUIRE n.id IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Function) REQUIRE n.id IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Library) REQUIRE n.id IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:DataStructure) REQUIRE n.id IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Parameter) REQUIRE n.id IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Component) REQUIRE n.id IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:API) REQUIRE n.id IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Service) REQUIRE n.id IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Module) REQUIRE n.id IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Interface) REQUIRE n.id IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:DataFlow) REQUIRE n.id IS UNIQUE")
                
                # Create indexes for commonly queried fields
                session.run("CREATE INDEX IF NOT EXISTS FOR (n:File) ON (n.name)")
                session.run("CREATE INDEX IF NOT EXISTS FOR (n:Function) ON (n.name)")
                session.run("CREATE INDEX IF NOT EXISTS FOR (n:DataStructure) ON (n.name)")
                
                print("Constraints and indexes created.")
            except Exception as e:
                print(f"Error creating constraints or indexes: {e}")
                # For Neo4j 4.x compatibility
                try:
                    session.run("CREATE CONSTRAINT ON (n:File) ASSERT n.id IS UNIQUE")
                    session.run("CREATE CONSTRAINT ON (n:Function) ASSERT n.id IS UNIQUE")
                    session.run("CREATE INDEX ON :File(name)")
                    session.run("CREATE INDEX ON :Function(name)")
                    print("Constraints and indexes created using legacy syntax.")
                except Exception as e2:
                    print(f"Error creating constraints using legacy syntax: {e2}")
    
    def create_knowledge_graph(self, kg_elements):
        """
        Create the knowledge graph in Neo4j.
        
        Args:
            kg_elements: Dictionary containing nodes, relationships, and properties
        """
        self.create_nodes(kg_elements.get("nodes", []))
        self.create_relationships(kg_elements.get("relationships", []))
        self.add_properties(kg_elements.get("properties", {}))
    
    def create_nodes(self, nodes):
        """Create nodes in the Neo4j database."""
        with self.driver.session() as session:
            total_nodes = len(nodes)
            for i, node in enumerate(nodes):
                # Print progress every 10% of nodes
                if i % max(1, total_nodes // 10) == 0:
                    print(f"Creating nodes: {i}/{total_nodes}")
                
                # Extract node properties
                label = node["label"]
                node_id = node["id"]
                
                # Create a dictionary of all other properties
                props = {k: v for k, v in node.items() if k not in ["id", "label"]}
                
                # Generate Cypher parameter dictionary
                params = {
                    "id": node_id,
                    "props": props
                }
                
                # Create the node
                session.run(
                    f"CREATE (n:{label} {{id: $id}}) SET n += $props",
                    params
                )
            
            print(f"Created {total_nodes} nodes.")
    
    def create_relationships(self, relationships):
        """Create relationships in the Neo4j database."""
        with self.driver.session() as session:
            total_rels = len(relationships)
            for i, rel in enumerate(relationships):
                # Print progress every 10% of relationships
                if i % max(1, total_rels // 10) == 0:
                    print(f"Creating relationships: {i}/{total_rels}")
                
                # Extract relationship properties
                source_id = rel["source"]
                target_id = rel["target"]
                rel_type = rel["type"]
                
                # Create the relationship
                try:
                    session.run(
                        f"""
                        MATCH (a), (b)
                        WHERE a.id = $source_id AND b.id = $target_id
                        CREATE (a)-[:{rel_type}]->(b)
                        """,
                        {"source_id": source_id, "target_id": target_id}
                    )
                except Exception as e:
                    print(f"Error creating relationship {source_id} -> {target_id}: {e}")
            
            print(f"Created {total_rels} relationships.")
    
    def add_properties(self, properties):
        """Add additional properties to nodes."""
        with self.driver.session() as session:
            total_props = len(properties)
            for i, (node_id, props) in enumerate(properties.items()):
                # Print progress every 10% of properties
                if i % max(1, total_props // 10) == 0:
                    print(f"Adding properties: {i}/{total_props}")
                
                # Add properties as a list or individual properties depending on the data structure
                if isinstance(props, list):
                    # Properties as a list
                    session.run(
                        """
                        MATCH (n)
                        WHERE n.id = $node_id
                        SET n.properties = $props
                        """,
                        {"node_id": node_id, "props": props}
                    )
                elif isinstance(props, dict):
                    # Properties as a dictionary
                    session.run(
                        """
                        MATCH (n)
                        WHERE n.id = $node_id
                        SET n += $props
                        """,
                        {"node_id": node_id, "props": props}
                    )
            
            print(f"Added properties to {total_props} nodes.")
    
    def run_query(self, query, params=None):
        """Run a custom Cypher query and return the results."""
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record for record in result]
    
    def execute_cypher_file(self, cypher_file):
        """Execute Cypher statements from a file."""
        with open(cypher_file, 'r') as f:
            statements = f.read().split(';')
            
            with self.driver.session() as session:
                for statement in statements:
                    if statement.strip():
                        try:
                            session.run(statement)
                        except Exception as e:
                            print(f"Error executing statement: {statement}")
                            print(f"Error: {e}")
            
            print(f"Executed Cypher statements from {cypher_file}.")
    
    def get_node_count(self):
        """Get the total number of nodes in the database."""
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) AS count")
            return result.single()["count"]
    
    def get_relationship_count(self):
        """Get the total number of relationships in the database."""
        with self.driver.session() as session:
            result = session.run("MATCH ()-[r]->() RETURN count(r) AS count")
            return result.single()["count"]
    
    def get_node_label_counts(self):
        """Get the count of nodes by label."""
        with self.driver.session() as session:
            result = session.run("""
                CALL db.labels() YIELD label
                MATCH (n:`{label}`)
                RETURN label, count(n) AS count
                ORDER BY count DESC
            """)
            return [(record["label"], record["count"]) for record in result]
    
    def get_relationship_type_counts(self):
        """Get the count of relationships by type."""
        with self.driver.session() as session:
            result = session.run("""
                CALL db.relationshipTypes() YIELD relationshipType
                MATCH ()-[r:`{relationshipType}`]->()
                RETURN relationshipType, count(r) AS count
                ORDER BY count DESC
            """)
            return [(record["relationshipType"], record["count"]) for record in result]
    
    def add_derived_relationships(self):
        """
        Add derived relationships that can be inferred from existing relationships.
        For example, if A IMPORTS B and B CONTAINS C, then A USES C.
        """
        with self.driver.session() as session:
            # File that imports a module uses the functions in that module
            session.run("""
                MATCH (f:File)-[:IMPORTS]->(m)
                MATCH (m)-[:CONTAINS]->(func:Function)
                MERGE (f)-[:USES]->(func)
            """)
            
            # Function that calls another function depends on that function
            session.run("""
                MATCH (f1:Function)-[:CALLS]->(f2:Function)
                MERGE (f1)-[:DEPENDS_ON]->(f2)
            """)
            
            # Function that accepts a data structure depends on that data structure
            session.run("""
                MATCH (f:Function)-[:ACCEPTS]->(ds:DataStructure)
                MERGE (f)-[:DEPENDS_ON]->(ds)
            """)
            
            # Function that returns a data structure produces that data structure
            session.run("""
                MATCH (f:Function)-[:RETURNS]->(ds:DataStructure)
                MERGE (f)-[:PRODUCES]->(ds)
            """)
            
            print("Added derived relationships.")
    
    def generate_kg_summary(self, output_file='kg_summary.txt'):
        """Generate a summary of the knowledge graph and save it to a file."""
        # Get counts
        node_count = self.get_node_count()
        rel_count = self.get_relationship_count()
        node_label_counts = self.get_node_label_counts()
        rel_type_counts = self.get_relationship_type_counts()
        
        # Generate summary text
        summary = [
            "Knowledge Graph Summary",
            "======================\n",
            f"Total nodes: {node_count}",
            "\nNode types:"
        ]
        
        for label, count in node_label_counts:
            summary.append(f"  - {label}: {count}")
        
        summary.append(f"\nTotal relationships: {rel_count}")
        summary.append("\nRelationship types:")
        
        for rel_type, count in rel_type_counts:
            summary.append(f"  - {rel_type}: {count}")
        
        # Save to file
        with open(output_file, 'w') as f:
            f.write('\n'.join(summary))
        
        print(f"Knowledge graph summary saved to {output_file}")
        return '\n'.join(summary)

def main():
    """Main function to create a knowledge graph from JSON files."""
    parser = argparse.ArgumentParser(description="Create a Neo4j knowledge graph from code summary JSON files")
    parser.add_argument("--uri", default="bolt://localhost:7687", help="Neo4j connection URI")
    parser.add_argument("--username", default="neo4j", help="Neo4j username")
    parser.add_argument("--password", required=True, help="Neo4j password")
    parser.add_argument("--input", default="kg_output/kg_elements.json", help="Input JSON file with KG elements")
    parser.add_argument("--clear", action="store_true", help="Clear the database before creating the graph")
    parser.add_argument("--cypher", help="Cypher file to execute after creating the graph")
    parser.add_argument("--summary", default="neo4j_kg_summary.txt", help="Output file for the graph summary")
    
    args = parser.parse_args()
    
    # Load KG elements from JSON
    with open(args.input, 'r') as f:
        kg_elements = json.load(f)
    
    # Create the knowledge graph
    creator = Neo4jKnowledgeGraphCreator(args.uri, args.username, args.password)
    
    try:
        if args.clear:
            creator.clear_database()
        
        creator.create_constraints_and_indexes()
        creator.create_knowledge_graph(kg_elements)
        creator.add_derived_relationships()
        
        if args.cypher:
            creator.execute_cypher_file(args.cypher)
        
        # Generate summary
        creator.generate_kg_summary(args.summary)
        
        # Print final counts
        node_count = creator.get_node_count()
        rel_count = creator.get_relationship_count()
        print(f"\nFinal graph statistics:")
        print(f"  - Total nodes: {node_count}")
        print(f"  - Total relationships: {rel_count}")
        
    finally:
        creator.close()

if __name__ == "__main__":
    main()