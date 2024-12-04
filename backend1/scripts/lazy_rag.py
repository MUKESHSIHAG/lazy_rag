import os
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain.embeddings import OpenAIEmbeddings
import numpy as np
import faiss
from dotenv import load_dotenv
import warnings
import logging as py_logging

warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()

py_logging.getLogger("neo4j").setLevel(py_logging.ERROR)

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")

neo4j_url = "bolt://localhost:7689"
neo4j_username = "neo4j"
neo4j_password = "12345678"

graph = Neo4jGraph(
    url=neo4j_url,
    username=neo4j_username,
    password=neo4j_password
)

embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
embedding_dim = 1536
faiss_index = faiss.IndexFlatL2(embedding_dim)
index_map = {} 


def load_embeddings():
    """Precompute embeddings and store in FAISS index."""
    global faiss_index, index_map
    cypher_query = """
    MATCH (n)
    RETURN id(n) AS id, COALESCE(n.description, n.name) AS text
    """
    results = graph.query(cypher_query)

    for record in results:
        node_id = record["id"]
        text = record["text"]
        if not text:
            continue
        embedding = embedding_model.embed_query(text)  
        faiss_index.add(np.array([embedding]).astype("float32")) 
        index_map[len(index_map)] = node_id

def search_embeddings(query, top_k=3):
    query_embedding = np.array(embedding_model.embed_query(query)).astype("float32")
    distances, indices = faiss_index.search(np.array([query_embedding]), top_k)
    relevant_nodes = [
        (index_map[i], distances[0][idx])
        for idx, i in enumerate(indices[0]) if i != -1
    ]
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
    prompt = f"Given the context:\n{context}\nAnswer the question: {question}\n The answer should include the data from context only not other info"
    return llm.predict(prompt)

def lazy_rag_query(question, top_k=3):
    relevant_nodes = search_embeddings(question, top_k)
    if not relevant_nodes:
        return ["No relevant information found."]

    responses = []
    for node_id, _ in relevant_nodes:
        details = retrieve_details(node_id)
        if not details:
            continue

        context = f"Description: {details.get('description', '')}\n" \
                  f"Name: {details.get('name', '')}\n" \
                  f"Relationships: {details.get('relationships', [])}"
        response = generate_response(question, context)
        responses.append(response)

    return responses


if __name__ == "__main__":
    print("Loading embeddings...")
    load_embeddings()  # Precompute embeddings once
    print("Embeddings loaded.")

    # Example query
    question = "What was the impact of the pandemic on India's economy?"
    answers = lazy_rag_query(question, top_k=3)

    print("Top Answers:")
    for idx, answer in enumerate(answers, start=1):
        print(f"Answer {idx}:", answer)
