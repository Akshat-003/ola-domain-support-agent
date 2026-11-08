import json
import time
import uuid

from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from agent.support_agent import chat
from rag.vector_store import add_document_to_vector_store


# ==========================================
# 1. LOGGING CONFIGURATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOG_DIRECTORY = PROJECT_ROOT / "logs"
LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIRECTORY / "api_requests.jsonl"


def write_log(log_data):

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(log_data) + "\n")


# ==========================================
# 2. FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Ola Domain Support Agent",
    description="API for Ola Business Operations and Customer Support",
    version="1.0.0"
)


# ==========================================
# 3. REQUEST LOGGING MIDDLEWARE
# ==========================================

@app.middleware("http")
async def logging_middleware(request: Request, call_next):

    trace_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    status_code = 500

    try:

        response = await call_next(request)

        status_code = response.status_code
        response.headers["X-Trace-ID"] = trace_id

        return response

    finally:

        processing_time = (
            time.perf_counter() - start_time
        ) * 1000

        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": trace_id,
            "method": request.method,
            "endpoint": request.url.path,
            "status_code": status_code,
            "processing_time_ms": round(processing_time, 2)
        }

        # Logging failure should not break the API response
        try:
            write_log(log_data)
        except OSError:
            pass


# ==========================================
# 4. ASK REQUEST MODEL
# ==========================================

class AskRequest(BaseModel):

    question: str = Field(min_length=1, max_length=2000)

    thread_id: str = Field(
        default="customer_001",
        min_length=1,
        max_length=64,
        pattern=r"^[a-zA-Z0-9_-]+$"
    )

    record_id: str = Field(
        default="",
        pattern=r"^(|OLA-\d{4})$"
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value):

        if not value.strip():
            raise ValueError("Question cannot contain only spaces.")

        return value.strip()


# ==========================================
# 5. ADD DOCUMENT REQUEST MODEL
# ==========================================

class AddDocumentRequest(BaseModel):

    document_id: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$"
    )

    text: str = Field(min_length=1, max_length=10000)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value):

        if not value.strip():
            raise ValueError("Document text cannot contain only spaces.")

        return value.strip()


# ==========================================
# 6. HOME ENDPOINT
# ==========================================

@app.get("/")
def home():

    return {
        "message": "Ola Domain Support Agent API is running!",
        "status": "success"
    }


# ==========================================
# 7. ASK ENDPOINT
# ==========================================

@app.post("/ask")
def ask_question(request: AskRequest):

    try:

        response = chat(
            thread_id=request.thread_id,
            question=request.question,
            record_id=request.record_id
        )

        return {
            "status": "success",
            "thread_id": request.thread_id,
            "response": response
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing the question."
        )


# ==========================================
# 8. ADD DOCUMENT ENDPOINT
# ==========================================

@app.post("/add-document")
def add_document(request: AddDocumentRequest):

    try:

        result = add_document_to_vector_store(
            document_id=request.document_id,
            text=request.text
        )

        return {
            "status": "success",
            "data": result
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to add document to the vector database."
        )