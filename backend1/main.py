from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from scripts.lazy_rag import lazy_rag_query
from scripts.naive_rag import naive_rag_query
from typing import List
import psutil
import time

app = FastAPI()

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Precompute embeddings for Lazy RAG
@app.on_event("startup")
async def startup_event():
    print("Loading embeddings for Lazy RAG...")
    from scripts.lazy_rag import load_embeddings
    load_embeddings()
    print("Lazy RAG embeddings loaded.")

# Input model
class QueryRequest(BaseModel):
    question: str
    top_k: int = 3  # Default number of top results

# Response model
class QueryResponse(BaseModel):
    answers: List[str]
    time_taken: float
    cpu_usage: float

def measure_cpu_usage(func, *args, **kwargs):
    """
    Measure CPU usage while running a function.
    """
    process = psutil.Process()
    cpu_before = process.cpu_percent(interval=None)  # CPU usage before
    start_time = time.time()  # Time before
    result = func(*args, **kwargs)  # Execute the function
    end_time = time.time()  # Time after
    cpu_after = process.cpu_percent(interval=None)  # CPU usage after
    cpu_usage = (cpu_before + cpu_after) / 2  # Average CPU usage
    time_taken = end_time - start_time  # Total time taken
    return result, cpu_usage, time_taken

@app.post("/lazy_rag", response_model=QueryResponse)
async def query_lazy_rag(request: QueryRequest):
    try:
        answers, cpu_usage, time_taken = measure_cpu_usage(
            lazy_rag_query, request.question, top_k=request.top_k
        )
        if not answers:
            raise HTTPException(status_code=404, detail="No relevant information found.")
        return QueryResponse(answers=answers, time_taken=time_taken, cpu_usage=cpu_usage)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/naive_rag", response_model=QueryResponse)
async def query_naive_rag(request: QueryRequest):
    try:
        answers, cpu_usage, time_taken = measure_cpu_usage(
            naive_rag_query, request.question, top_k=request.top_k
        )
        if not answers:
            raise HTTPException(status_code=404, detail="No relevant information found.")
        return QueryResponse(answers=answers, time_taken=time_taken, cpu_usage=cpu_usage)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
