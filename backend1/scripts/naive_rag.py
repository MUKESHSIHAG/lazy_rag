import os
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain.embeddings import OpenAIEmbeddings
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Neo4j connection details
neo4j_url = "bolt://localhost:7689"
neo4j_username = "neo4j"
neo4j_password = "12345678"

graph = Neo4jGraph(
    url=neo4j_url,
    username=neo4j_username,
    password=neo4j_password
)

embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)

def search_and_retrieve(question, top_k=3):
    query_embedding = np.array(embedding_model.embed_query(question)).astype("float32")

    cypher_query = """
    MATCH (n)
    RETURN id(n) AS id, COALESCE(n.description, n.name) AS text
    """
    results = graph.query(cypher_query)

    nodes = []
    embeddings = []
    for record in results:
        node_id = record["id"]
        text = record["text"]
        if text:
            nodes.append({"id": node_id, "text": text})
            embeddings.append(np.array(embedding_model.embed_query(text)).astype("float32"))

    distances = [np.linalg.norm(query_embedding - node_emb) for node_emb in embeddings]
    ranked_indices = np.argsort(distances)[:top_k]

    relevant_nodes = [{"id": nodes[i]["id"], "text": nodes[i]["text"], "distance": distances[i]} for i in ranked_indices]
    return relevant_nodes

def retrieve_details(node_id):
    cypher_query = """
    MATCH (n)-[r]->(m)
    WHERE id(n) = $node_id
    RETURN n.description AS description, n.name AS name,
           [(n)-[r]->(m) | {relation: type(r), target: m.name}] AS relationships
    """
    result = graph.query(cypher_query, {"node_id": node_id})

    if result:
        record = result[0]
        return {
            "description": record.get("description"),
            "name": record.get("name"),
            "relationships": record.get("relationships", [])
        }
    return None

def generate_response(question, context):
    llm = ChatOpenAI(model_name="gpt-4o-mini", api_key=openai_api_key)
    prompt = f"Given the context:\n{context}\nAnswer the question: {question}\n  The answer should include the data from context only not other info"
    return llm.predict(prompt)

def naive_rag_query(question, top_k=3):
    relevant_nodes = search_and_retrieve(question, top_k)

    if not relevant_nodes:
        return ["No relevant information found."]

    responses = []
    for node in relevant_nodes:
        details = retrieve_details(node["id"])
        if not details:
            continue

        context = f"Description: {details.get('description', '')}\n" \
                  f"Name: {details.get('name', '')}\n" \
                  f"Relationships: {details.get('relationships', [])}"
        response = generate_response(question, context)
        responses.append(response)

    return responses

# if __name__ == "__main__":
#     question = "What was the impact of the pandemic on India's economy?"
#     answers = naive_rag_query(question, top_k=3)

#     print("Top Answers:")
#     for idx, answer in enumerate(answers, start=1):
#         print(f"Answer {idx}:", answer)
