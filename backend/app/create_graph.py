from neo4j import GraphDatabase
import json
from dotenv import load_dotenv
import os
load_dotenv()

def get_neo4j_driver(uri, username, password):
    return GraphDatabase.driver(uri, auth=(username, password))

def store_entities(driver, entities):
    with driver.session() as session:
        for entity in entities:
            session.run(
                """
                MERGE (e:Entity {id: $id})
                SET e.name = $name,
                    e.description = $description,
                    e.type = $type
                """,
                id=entity["id"],
                name=entity["name"],
                description=entity["description"],
                type=entity["type"]
            )

def store_relationships(driver, relationships):
    with driver.session() as session:
        for relationship in relationships:
            session.run(
                """
                MATCH (a:Entity {id: $from_id})
                MATCH (b:Entity {id: $to_id})
                MERGE (a)-[r:RELATIONSHIP {type: $type}]->(b)
                SET r.context = $context
                """,
                from_id=relationship["from"],
                to_id=relationship["to"],
                type=relationship["type"],
                context=relationship.get("context", "")
            )

def main():
    structured_data_file = "/Users/mukeshsihag/Desktop/nlp/backend/data/structured_data.json"

    neo4j_uri = os.getenv("NEO4J_URI") or "bolt://localhost:7689"
    neo4j_username = os.getenv("NEO4J_USERNAME") or "neo4j"
    neo4j_password = os.getenv("NEO4J_PASSWORD") or "12345678"

    driver = get_neo4j_driver(neo4j_uri, neo4j_username, neo4j_password)

    try:
        with open(structured_data_file, "r", encoding="utf-8") as f:
            structured_data = json.load(f)

        entities = structured_data.get("entities", [])
        relationships = structured_data.get("relationships", [])

        print("Storing entities...")
        store_entities(driver, entities)

        print("Storing relationships...")
        store_relationships(driver, relationships)

        print("Data successfully stored in Neo4j!")
    finally:
        driver.close()

if __name__ == "__main__":
    main()
