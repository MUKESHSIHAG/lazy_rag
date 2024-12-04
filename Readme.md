## Project Overview
### Note:
The original PDF file was too large to process due to system resource limitations and high costs associated with using the OpenAI API. To address this, I split the document into smaller sections (e.g., processing the first chapter separately) and used that subset for generating entities and relationships. For large PDFs, you can follow the same approach—split the file, process each chunk iteratively, and aggregate the results. If your system has sufficient resources, you can process the entire file, but this might incur significant API costs when using GPT-4.

This project consists of two backends and one frontend:

1. **`backend`**: 
   - Uses **SpaCy** and **transformers** (free tools) for entity and relationship extraction.
   - Implements **Lazy RAG** and **Naive RAG** methods to generate responses in natural language based on Neo4j data.
   
2. **`backend1`**: 
   - Uses **GPT-4** for entity and relationship extraction and for generating responses in natural language.
   - Provides more advanced response generation compared to the `backend`.

3. **`frontend`**:
   - A simple **HTML, CSS, JavaScript** application that allows users to query the backends and view responses in a chat-like interface.

---

## Folder Structure

```
.
├── backend
│   ├── app
│   │   ├── data_extract.py
│   │   ├── structure_data.py
│   │   ├── create_graph.py
│   │   ├── lazy_rag.py
│   ├── main.py
│   └── requirements.txt
├── backend1
│   ├── scripts
│   │   ├── extract_data.py
│   │   ├── generate_entities.py
│   │   ├── create_graph_db.py
│   │   ├── lazy_rag.py
|   |   |── naive_rag.py
│   ├── main.py
│   └── requirements.txt
├── frontend
│   ├── index.html
│   ├── style.css
│   ├── app.js
└── README.md
```

---

## Requirements

### Backend Requirements

1. **Python 3.9 or above**
2. **Neo4j**
   - Download and install [Neo4j Desktop](https://neo4j.com/download/) or run a Neo4j database instance.
   - Ensure Neo4j is running on `bolt://localhost:7689` (default port for this project). 
3. **Dependencies** (Install using `requirements.txt`):
   - Install the required Python packages for both `backend` and `backend1` by running:
     ```bash
     pip install -r requirements.txt
     ```
4. **OpenAI API Key** (for `backend1`):
   - Get an API key from [OpenAI](https://platform.openai.com/).
   - Create a `.env` file in the `backend1` folder and add the following:
     ```
     OPENAI_API_KEY=your_openai_api_key
     ```

### Frontend Requirements

1. **HTML, CSS, JavaScript**:
   - No additional libraries are required.
   - A modern web browser (Chrome, Firefox, etc.) is sufficient.

---

## Step-by-Step Instructions

### 1. Extract Raw Data from PDF
- Use `extract_data.py` in both `backend` and `backend1` to extract raw text from a PDF file present in `data` folder:
  ```bash
  python scripts/extract_data.py
  ```

### 2. Generate Entities and Relationships
- **`backend1`**:
  - Uses GPT-4 to generate entities and relationships.
  - Run the script:
    ```bash
    python scripts/generate_entities.py
    ```
- **`backend`**:
  - Uses SpaCy and transformers to generate entities and relationships.
  - Run the script:
    ```bash
    python scripts/generate_entities.py
    ```

### 3. Insert Data into Neo4j
- Insert the structured data (`structured_data.json`) into Neo4j using the `create_graph_db.py` script:
  ```bash
  python scripts/create_graph_db.py
  ```
  
### 4. Start the Backend Servers
- **`backend1`**:
  ```bash
  python main.py
  ```

### 6. Run the Frontend
- Open the `frontend/index.html` file in a browser.

---

## How to Query

1. Open the frontend UI in your browser.
2. Enter your query in the input field.
3. Select the backend (`Naive RAG` or `Lazy RAG`) from the dropdown.
4. Click "Send."
5. View the assistant's response in the chat interface.

---

## Key Features

1. **Lazy RAG**:
   - Precomputes embeddings for faster query response.
   - Provides semantically accurate answers based on stored context.

2. **Naive RAG**:
   - Computes embeddings at runtime, avoiding precomputation overhead.
   - Useful for small-scale data.

---

## Notes

1. **Benchmarking**:
   - Use the dropdown in the frontend to select `Naive RAG` or `Lazy RAG` for comparison.
   - The backend calculates CPU usage for each query and time taken.