from openai import OpenAI
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Load OpenAI API key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def split_text_into_chunks(text, max_length=2000):
    chunks = []
    current_chunk = []
    current_length = 0

    for line in text.splitlines():
        line_length = len(line)
        if current_length + line_length > max_length:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(line)
        current_length += line_length

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks


# Function to clean and parse GPT response
def clean_and_parse_response(response_content):
    try:
        if response_content.startswith("```"):
            response_content = response_content.split("\n", 1)[1]
            response_content = response_content.rsplit("```", 1)[0] 
        
        return json.loads(response_content)
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)
        print("Response content:", response_content)
        return None


# Normalize and validate the structured data
def normalize_data(structured_data):
    normalized_entities = []
    normalized_relationships = []

    required_entity_keys = {"id", "name", "type", "description"}
    required_relationship_keys = {"from", "to", "type", "context"}

    for entity in structured_data.get("entities", []):
        normalized_entity = {key: entity.get(key, "") for key in required_entity_keys}
        normalized_entities.append(normalized_entity)

    for relationship in structured_data.get("relationships", []):
        normalized_relationship = {key: relationship.get(key, "") for key in required_relationship_keys}
        normalized_relationships.append(normalized_relationship)

    return {"entities": normalized_entities, "relationships": normalized_relationships}


# GPT-4 entity and relationship extraction
def extract_entities_relationships_from_chunks(chunks):
    all_entities = []
    all_relationships = []

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1}/{len(chunks)}...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Extract entities and relationships in JSON format to store them in a Neo4j database. "
                        "Return the response in the following structure. The keys should be present in the entities and relationships:\n\n"
                        "{\n"
                        '  "entities": [\n'
                        '    { "id": "1", "name": "India", "type": "Country", "description": "A country in South Asia." },\n'
                        '    { "id": "2", "name": "Pandemic", "type": "Event", "description": "Global outbreak of a disease." }\n'
                        "  ],\n"
                        '  "relationships": [\n'
                        '    { "from": "1", "to": "2", "type": "affected_by", "context": "Economic impact due to the pandemic" }\n'
                        "  ]\n"
                        "}\n\n"
                        "Make sure to store longer sentences in the description and context fields so that meaningful answers can be retrieved."
                    ),
                },
                {"role": "user", "content": chunk},
            ]
        )

        response_content = response.choices[0].message.content
        structured_data = clean_and_parse_response(response_content)

        if structured_data is not None:
            normalized_data = normalize_data(structured_data)
            all_entities.extend(normalized_data["entities"])
            all_relationships.extend(normalized_data["relationships"])

    return {"entities": all_entities, "relationships": all_relationships}

if __name__ == "__main__":
    input_txt_file = "/Users/mukeshsihag/Desktop/nlp/backend1/data/raw_text.txt"
    output_json_file = "/Users/mukeshsihag/Desktop/nlp/backend1/data/structured_data.json"

    with open(input_txt_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    chunks = split_text_into_chunks(raw_text)

    print("Extracting entities and relationships from chunks...")
    structured_data = extract_entities_relationships_from_chunks(chunks)

    with open(output_json_file, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, indent=4)

    print(f"Entities and relationships extracted and saved to {output_json_file}")
