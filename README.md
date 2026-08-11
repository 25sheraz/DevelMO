# DevelMo AI — Dual-Vector Hybrid RAG Assistant

<p align="center">
  <strong>Production-grade Enterprise Retrieval-Augmented Generation (RAG) System with Dual-Vector Search, Cross-Encoder Reranking, Redis Session Memory, and Embedded React Chat Widget.</strong>
</p>

---

## 🚀 Overview

**DevelMo** is an end-to-end, enterprise-ready AI Chat & Knowledge Retrieval System. It combines dense semantic embeddings with sparse BM25 keyword matching via **Reciprocal Rank Fusion (RRF)**, re-ranks candidate matches with high-precision Cross-Encoders, and leverages **Redis Cloud** for multi-turn conversation memory with dynamic query reformulation.

Whether deployed as a FastAPI backend, embedded into web applications via the included React widget, or executed interactively in the terminal, DevelMo delivers fast, contextually aware, and non-hallucinating responses grounded strictly in your corporate knowledge base.

---

## ⚡ Key Features

- **🔎 Dual-Vector Hybrid Search**: Combines Dense Vector Search (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) and Sparse BM25 Search inside **Qdrant**.
- **🔀 Reciprocal Rank Fusion (RRF)**: Merges dense vector proximity scores and sparse lexical ranking to capture both semantic intent and exact keyphrase matches.
- **🎯 Cross-Encoder Reranking**: Re-scores top RRF candidate document chunks using `cross-encoder/ms-marco-MiniLM-L-6-v2` / `BAAI/bge-reranker-v2-m3` to eliminate irrelevant context before LLM generation.
- **🧠 Multi-Turn Redis Session Memory**: Tracks conversation turns across user sessions (`RedisMemoryManager`) with sliding window limits and TTL expiration, alongside automatic local in-memory fallback.
- **🔄 Intelligent Query Rewriting**: Reformulates follow-up user queries (`QueryRewriter`) into standalone search statements using past turn context.
- **🌐 FastAPI REST Server**: Production API serving `/api/chat`, static web hosting, CORS middleware, and interactive OpenAPI docs (`/docs`).
- **⚛️ React Chat Widget**: Modular, customizable TypeScript React component (`DevelMoChatWidget.tsx`) with instant messaging, quick reply suggestions, source citations, and dark-mode styled UI.
- **💻 Interactive CLI Assistant**: Terminal interface (`cli.py`) supporting live memory clearing, interactive source inspection, and status reporting.
- **📄 Document Ingestion Pipeline**: Auto-parsing and sliding-window chunking (`ingest.py` & `document_processor.py`) for PDF, Markdown, and TXT files.

---

## 🏗 System Architecture

```mermaid
flowchart TD
    User([User / Web Widget / CLI]) -->|1. Submit Query| API[FastAPI Server / CLI]
    API --> Memory[Redis Session Memory]
    Memory -->|Fetch History| Rewriter[Query Rewriter]
    Rewriter -->|2. Standalone Query| Dense[Dense Embedding Model]
    
    Dense -->|3. Dense Vector| Qdrant[(Qdrant Cloud Collection)]
    Rewriter -->|3. BM25 Keywords| Qdrant
    
    Qdrant -->|4. Dense & BM25 Candidates| RRF[Reciprocal Rank Fusion]
    RRF -->|5. Top Candidates| Reranker[Cross-Encoder Reranker]
    Reranker -->|6. Top-K Final Chunks| Prompt[Context Builder]
    
    Prompt -->|7. Grounded Context Payload| LLM[LLM Generator / OpenAI API]
    LLM -->|8. Generated Answer| API
    API -->|9. Store Turn| Memory
    API -->|10. Return Response + Sources| User
```

---

## 📋 Prerequisites

- **Python**: `3.10+`
- **Node.js**: `18.0+` & `npm`
- **Qdrant Cloud** vector database instance
- **Redis Cloud** (or local Redis instance)
- **LLM API Key** (OpenAI compatible endpoint, e.g., GPT-4o-mini / GPT-5)

---

## 📥 Installation & Setup

### 1. Clone Repository & Setup Virtual Environment

```bash
# Clone the repository
git clone https://github.com/25sheraz/DevelMo.git
cd DevelMo

# Create and activate Python virtual environment
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```
*(If `requirements.txt` is missing, install the core dependencies directly:)*
```bash
pip install fastapi uvicorn pydantic sentence-transformers cross-encoder qdrant-client redis httpx python-dotenv PyPDF2
```

### 3. Install Frontend Dependencies

```bash
npm install
```

---

## ⚙️ Environment Configuration (`.env`)

Create a `.env` file in the root directory containing your service credentials and model configurations:

```ini
# Qdrant Vector DB Configuration
QDRANT_URL=https://your-qdrant-cluster-url.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=rag_documents

# Redis Session Memory Configuration
REDIS_URL=redis://default:password@your-redis-host:port
MEMORY_TURNS=5
MEMORY_TTL_SECONDS=1800

# Embedding & Reranker Models
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2

# LLM Endpoint Configuration
LLM_API_KEY=your_openai_or_compatible_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# Search & Retrieval Parameters
TOP_K_DENSE=20
TOP_K_BM25=20
RRF_K=60
TOP_K_RRF=20
TOP_K_FINAL=5

# Document Chunking Settings
CHUNK_SIZE=600
CHUNK_OVERLAP=100
```

---

## 🚀 Usage Guide

### 1. Ingest Documents into Vector Store

Ingest single files or entire folders of PDF, Markdown (`.md`), or Text (`.txt`) documents into Qdrant:

```bash
# Ingest default knowledge base (DevelMo_Knowledge_Base.md)
python ingest.py

# Ingest a specific document
python ingest.py --file path/to/document.pdf

# Ingest an entire directory (and optionally recreate collection)
python ingest.py --dir path/to/docs --recreate
```

### 2. Launch FastAPI Server & Web App

Run the server to expose the REST API and serve the frontend interface:

```bash
# Start FastAPI backend server on port 8000
python server.py
```
Access the application:
- **Web Chat Interface**: `http://localhost:8000`
- **Interactive Swagger API Docs**: `http://localhost:8000/docs`

For frontend hot-reloading during UI development:
```bash
npm run dev
```

### 3. Interactive CLI Assistant

Interact with the RAG pipeline directly inside your terminal:

```bash
python cli.py --session my_terminal_user --sources
```
*CLI Commands:*
- `/clear` — Reset session conversation memory.
- `/sources` — Toggle output of retrieved document chunks.
- `exit` — Exit the assistant.

### 4. Run Pipeline Verification Tests

```bash
# Verify environment setup and connections
python test_env.py

# Test hybrid search & reranking isolation
python test_hybrid_search.py

# Run end-to-end multi-turn scenario tests
python test_full_pipeline.py
```

---

## 🔌 API Reference

### `POST /api/chat`

Processes user queries through the multi-stage hybrid RAG pipeline.

#### Request Body
```json
{
  "query": "What custom AI solutions does DevelMo offer?",
  "session_id": "web_user_123"
}
```

#### Response Body
```json
{
  "query": "What custom AI solutions does DevelMo offer?",
  "rewritten_query": "What custom artificial intelligence and machine learning solutions are offered by DevelMo?",
  "response": "DevelMo provides custom AI solutions including enterprise RAG systems, predictive analytics, computer vision applications, and tailored LLM integrations...",
  "sources": [
    {
      "source": "DevelMo_Knowledge_Base.md",
      "page": 1
    }
  ]
}
```

---

## ⚛️ React Widget Integration

Embed the `DevelMoChatWidget` component directly into any React / Next.js application:

```tsx
import React from 'react';
import { DevelMoChatWidget } from './DevelMoChatWidget';

export default function App() {
  return (
    <div className="app-container">
      <h1>Welcome to Our Corporate Portal</h1>
      
      {/* Floating DevelMo AI Chat Widget */}
      <DevelMoChatWidget 
        apiEndpoint="http://localhost:8000/api/chat"
        sessionId="user_session_456"
        initialMessage="Hello! How can DevelMo assist you today?"
      />
    </div>
  );
}
```

---

## 📁 Repository Structure

```
DevelMo/
├── server.py                  # FastAPI REST API & static file server
├── cli.py                     # Terminal interactive assistant
├── ingest.py                  # Document ingestion tool
├── document_processor.py      # PDF/MD/TXT reader & chunker
├── qdrant_manager.py          # Qdrant client, sparse/dense indexing & RRF search
├── rag_pipeline.py            # Redis memory, query rewriter, context builder & LLM generator
├── DevelMoChatWidget.tsx      # React UI Chat Widget component
├── index.html                 # Web interface entry point
├── package.json               # Node.js dependencies & scripts
├── tsconfig.json              # TypeScript configuration
├── DevelMo_Knowledge_Base.md  # Default corporate knowledge base source
├── test_env.py                # Environment & connectivity test
├── test_hybrid_search.py      # Search & RRF test script
└── test_full_pipeline.py      # Multi-turn end-to-end pipeline test
```

---

## 📄 License

This project is proprietary and maintained by **DevelMo**. All rights reserved.
