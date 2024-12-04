import spacy
import json

nlp = spacy.load("en_core_web_sm")
nlp.max_length = 1000000 

def split_text_into_chunks(text, max_chunk_size=100000):
    """
    Split text into manageable chunks.
    """
    chunks = []
    for i in range(0, len(text), max_chunk_size):
        chunks.append(text[i:i + max_chunk_size])
    return chunks

def extract_entities_and_relationships(chunk):
    doc = nlp(chunk)
    entities = []
    relationships = []

    for ent in doc.ents:
        entities.append({
            "id": str(hash(ent.text)), 
            "name": ent.text,
            "description": f"A {ent.label_} entity, specifically {ent.text}, found in the provided text.",
            "type": ent.label_
        })

    for token in doc:
        if token.dep_ in ("nsubj", "dobj", "pobj", "prep"):
            relationships.append({
                "type": token.dep_,
                "context": f"Relation identified as {token.dep_} between {token.head.text} and {token.text}.",
                "from": str(hash(token.head.text)),
                "to": str(hash(token.text))
            })

    return entities, relationships

def process_large_text(file_path, output_file):
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    print("Splitting text into chunks...")
    chunks = split_text_into_chunks(raw_text)

    all_entities = []
    all_relationships = []

    for idx, chunk in enumerate(chunks):
        print(f"Processing chunk {idx + 1}/{len(chunks)}...")
        entities, relationships = extract_entities_and_relationships(chunk)
        all_entities.extend(entities)
        all_relationships.extend(relationships)

    structured_data = {
        "entities": all_entities,
        "relationships": all_relationships
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, indent=4)

    print(f"Structured data saved to {output_file}")

if __name__ == "__main__":
    raw_text_file = "/Users/mukeshsihag/Desktop/nlp/backend/data/raw_text.txt"
    output_file = "/Users/mukeshsihag/Desktop/nlp/backend/data/structured_data.json"

    process_large_text(raw_text_file, output_file)

