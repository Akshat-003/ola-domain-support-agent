# Ola Domain Support Agent
### Business Operations / Customer Support Capstone Project

## 1. Project Overview

The Ola Domain Support Agent is an AI-powered customer support system designed to answer support-related questions, retrieve ticket information, and provide knowledge-base-based responses.

The project combines Retrieval-Augmented Generation (RAG), LangGraph, FastAPI, Model Context Protocol (MCP), and SQLite checkpointing.

This is an educational simulation. The policies and support records are synthetic and do not represent actual Ola internal systems or policies.

## 2. Key Features

- Synthetic support-ticket dataset containing 50 records.
- Knowledge base containing 12 support-policy documents.
- Two document chunking strategies:
  - Fixed-size chunking with overlap.
  - Sentence-based chunking.
- SentenceTransformer embeddings.
- ChromaDB vector database.
- Similarity-threshold-based retrieval.
- Groundedness validation and out-of-scope fallback.
- Ticket-status lookup with escalation scoring.
- LangGraph-based conversational workflow.
- JSON conversation memory.
- Pydantic response-schema validation.
- Phone-number masking and prompt-injection detection.
- FastAPI endpoints for support queries and document insertion.
- Structured JSONL API logs.
- RAG Triad evaluation.
- FastMCP server and separate MCP client.
- SQLite-based LangGraph checkpointing.
- Retry with exponential backoff and timeout demonstrations.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| SentenceTransformers | Text embeddings |
| ChromaDB | Vector database |
| LangGraph | Agent workflow |
| LangChain Core | Supporting AI components |
| Pydantic | Data validation |
| FastAPI | REST API |
| Uvicorn | API server |
| FastMCP | MCP server and client |
| SQLite | Workflow checkpointing |

## 4. Project Structure

```text
ola-domain-support-agent/
│
├── agent/
│   ├── guardrails.py
│   ├── memory.py
│   ├── response_schema.py
│   ├── support_agent.py
│   └── ticket_lookup.py
│
├── api/
│   └── main.py
│
├── dataset/
│   ├── dataset.py
│   └── support_tickets.json
│
├── knowledge_base/
│   └── 12 support policy documents
│
├── rag/
│   ├── chunking.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retrieval.py
│   ├── generation.py
│   ├── grounding.py
│   ├── config.py
│   ├── calibrate_threshold.py
│   ├── evaluate_retrieval.py
│   └── validate_kb.py
│
├── evaluations/
│   ├── rag_triad_evaluation.py
│   └── rag_triad_results.json
│
├── mcp_tools/
│   ├── server.py
│   └── client.py
│
├── resilience/
│   ├── checkpoint_demo.py
│   └── retry_timeout_demo.py
│
├── transcripts/
├── logs/
├── chroma_db/
│
├── .gitignore
├── requirements.txt
└── README.md
```

## 5. Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd ola-domain-support-agent
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## 6. Running the Project

### Build the Vector Database

```bash
python -m rag.vector_store
```

Note: This command rebuilds the ChromaDB collections from the original knowledge-base documents.

### Run the Support Agent

```bash
python -m agent.support_agent
```

### Run the FastAPI Server

```bash
python -m uvicorn api.main:app --reload
```

Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Run the MCP Client

```bash
python -m mcp_tools.client
```

### Run SQLite Checkpointing Demo

```bash
python -m resilience.checkpoint_demo
```

### Run Retry and Timeout Demo

```bash
python -m resilience.retry_timeout_demo
```

### Run RAG Evaluation

```bash
python -m evaluations.rag_triad_evaluation
```

## 7. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API health check |
| POST | `/ask` | Ask the support agent a question |
| POST | `/add-document` | Add a document to both vector collections |

## 8. Evaluation and Testing

The project includes:

- Retrieval evaluation comparing fixed-size and sentence-based chunking.
- Similarity-threshold calibration using in-scope and out-of-scope queries.
- Groundedness validation.
- Ticket escalation-score testing.
- Response-schema validation.
- RAG Triad evaluation using a deterministic mock evaluator.
- MCP tool testing with multiple ticket IDs.
- SQLite checkpoint and resume testing.
- Retry, per-node timeout, and global timeout demonstrations.

## 9. Mock Mode and Limitations

The project supports deterministic mock mode and does not require an external LLM API key for its demonstration workflows.

The mock response generator uses retrieved knowledge-base context rather than producing a fully synthesized LLM answer.

Groundedness and evaluation scores use deterministic heuristics. They are useful for demonstrating the evaluation pipeline but are not equivalent to semantic LLM judging or a guarantee of factual correctness.

The dataset, support tickets, and policies are synthetic.

## 10. Future Improvements

- Integrate a production-grade language model.
- Improve semantic groundedness evaluation.
- Add authentication and authorization.
- Add a frontend customer-support interface.
- Improve monitoring and production deployment.
- Expand the synthetic support dataset.

## 11. Author

**Akshat Kumar**

https://github.com/Akshat-003/ola-domain-support-agent