from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
import faiss
import numpy as np
from transformers import pipeline
import logging as py_logging

py_logging.getLogger("neo4j").setLevel(py_logging.ERROR)
import os

# Disable parallelism warning from HuggingFace
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from transformers import pipeline

# Set device to "cpu" (or "cuda" for GPU if available and desired)
response_pipeline = pipeline("text2text-generation", model="t5-small", tokenizer="t5-small", device=0)  # For GPU, set device=0; for CPU, set device=-1

# Step 1: Precompute and Store Embeddings
# def precompute_embeddings(driver, model, faiss_index, index_map):
#     with driver.session() as session:
#         query = "MATCH (n) RETURN id(n) AS id, n.text AS text"
#         results = session.run(query)

#         for record in results:
#             node_id = record["id"]
#             text = record["text"]
#             embedding = model.encode(text)
#             faiss_index.add(np.array([embedding]).astype('float32'))
#             index_map[len(index_map)] = node_id  # Map FAISS index to node ID

def precompute_embeddings(driver, model, faiss_index, index_map):
    with driver.session() as session:
        query = """
        MATCH (n)
        RETURN elementId(n) AS id, COALESCE(n.description, n.name) AS text
        """
        results = session.run(query)

        for record in results:
            node_id = record["id"]
            text = record["text"]
            if not text:  # Skip nodes without text
                continue
            embedding = model.encode(text)
            faiss_index.add(np.array([embedding]).astype('float32'))
            index_map[len(index_map)] = node_id  # Map FAISS index to node ID

# Step 2: Fine-tune User Query
def refine_query(user_query):
    query_refinement_pipeline = pipeline("text2text-generation", model="t5-small", tokenizer="t5-small")
    refined_query = query_refinement_pipeline(f"Refine: {user_query}", max_length=50, num_return_sequences=1)[0]["generated_text"]
    return refined_query

# Step 3: Search Precomputed Embeddings
def search_embeddings(query, model, faiss_index, index_map, top_k=3):
    query_embedding = model.encode(query).astype('float32')
    distances, indices = faiss_index.search(np.array([query_embedding]), top_k)
    return [(index_map[i], distances[0][idx]) for idx, i in enumerate(indices[0])]

# Step 4: Retrieve Details from Neo4j
# def retrieve_details(driver, node_ids):
#     details_list = []
#     with driver.session() as session:
#         for node_id in node_ids:
#             query = """
#             MATCH (n) WHERE id(n) = $node_id
#             RETURN n.text AS text, [(n)-[r]->(m) | {relation: type(r), target: m.text}] AS relationships
#             """
#             result = session.run(query, node_id=node_id)
#             record = result.single()
#             if record:
#                 details_list.append({
#                     "text": record["text"],
#                     "relationships": record["relationships"]
#                 })
#     return details_list

def retrieve_details(driver, node_ids):
    details_list = []
    with driver.session() as session:
        for node_id in node_ids:
            query = """
            MATCH (n)-[r]->(m)
            WHERE elementId(n) = $node_id
            RETURN n.description AS description, n.name AS name, n.type AS type,
                   [(n)-[r]->(m) | {relation: type(r), target: m.name, context: r.context}] AS relationships
            """
            result = session.run(query, node_id=node_id)
            record = result.single()
            if record:
                details_list.append({
                    "description": record["description"],
                    "name": record["name"],
                    "type": record["type"],
                    "relationships": record["relationships"]
                })
    return details_list

# Step 5: Generate Natural Language Answers

def generate_answers(details_list):
    response_pipeline = pipeline("text2text-generation", model="t5-small", tokenizer="t5-small",)
    answers = []
    for details in details_list:
        text = details.get("text", "")
        relationships = details.get("relationships", [])
        context = f"context: {text}. Relationships: {relationships}"
        response = response_pipeline(f"Generate a simple text response from this context: {context}", max_length=100, num_return_sequences=1, temperature=0.7)[0]["generated_text"]
        answers.append(response)
    return answers

# Main Script
if __name__ == "__main__":
    # Neo4j credentials
    neo4j_uri = "bolt://localhost:7689"
    neo4j_username = "neo4j"
    neo4j_password = "12345678"

    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))

    # Load embedding model
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    # Initialize FAISS index
    embedding_dim = 384  # Dimension of MiniLM embeddings
    faiss_index = faiss.IndexFlatL2(embedding_dim)
    index_map = {}

    # Precompute embeddings and store them
    print("Precomputing embeddings...")
    precompute_embeddings(driver, embedding_model, faiss_index, index_map)
    print("Embeddings precomputed and stored in FAISS!")

    # User query
    # user_query = "What was the fiscal deficit of states in FY24?"
    # user_query = "The prices of what increased in FY23 due to the Russia-Ukraine conflict?"
    user_query = "What was the impact of the pandemic on India's economy?"

    # Refine user query
    # refined_query = refine_query(user_query)
    # print(f"Refined Query: {refined_query}")

    # Search precomputed embeddings
    relevant_nodes = search_embeddings(user_query, embedding_model, faiss_index, index_map, top_k=3)

    if relevant_nodes:
        print("Relevant Nodes:", relevant_nodes)
        top_node_ids = [node_id for node_id, _ in relevant_nodes]
        details_list = retrieve_details(driver, top_node_ids)
        if details_list:
            answers = generate_answers(details_list)
            print("Generated Answers:")
            for answer in answers:
                print(answer)
        else:
            print("No details found for the relevant nodes.")
    else:
        print("No relevant nodes found.")


    # user_query = "The prices of what increased in FY23 due to the Russia-Ukraine conflict?"
    # # user_query = "the gross fiscal deficit of how many states was 8.6 per cent lower than the budgeted figure of ₹9.1 lakh crore"
