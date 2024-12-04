from neo4j import GraphDatabase

# Connection details
NEO4J_URI = "bolt://localhost:7689"  # Update if using a different port
NEO4J_USERNAME = "neo4j"  # Replace with your username
NEO4J_PASSWORD = "12345678"  # Replace with your password

class Neo4jHandler:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def close(self):
        self.driver.close()

    def query_all_nodes_and_relationships(self):
        print("driver...", self.driver)
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN n LIMIT 10")  # Fetch 10 nodes for verification
            nodes = [record["n"] for record in result]
            return nodes
    
    def delete_all_nodes_and_relationships(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("All nodes and relationships deleted successfully!")

if __name__ == "__main__":
    # Initialize Neo4j handler
    handler = Neo4jHandler(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    
    # Step 1: Query the existing data
    print("Querying existing nodes...")
    nodes = handler.query_all_nodes_and_relationships()
    if nodes:
        print(f"Found {len(nodes)} nodes:")
        for node in nodes:
            print(node)
    else:
        print("No nodes found in the database.")

    # Step 2: Delete all nodes and relationships
    print("Deleting all nodes and relationships...")
    handler.delete_all_nodes_and_relationships()

    # Step 3: Confirm deletion
    print("Re-querying to confirm deletion...")
    nodes_after_deletion = handler.query_all_nodes_and_relationships()
    if not nodes_after_deletion:
        print("Database is now empty!")
    else:
        print(f"Nodes still present: {len(nodes_after_deletion)}")

    # Close connection
    handler.close()
