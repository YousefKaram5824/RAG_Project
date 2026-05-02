# 🧠 RAG Project — Team Setup Guide (Windows + VS Code)

## ⚡ Quick Start (3 commands to get running)

```powershell
# Terminal 1 — Start databases
cd docker
copy .env.example .env      # then open .env and verify credentials
docker-compose up -d

# Terminal 2 — Start FastAPI backend
cd src
copy .env.example .env      # then open .env and add your OPENAI_API_KEY
pip install -r requirements.txt
uvicorn main:app --reload --port 5000

# Terminal 3 — Start Streamlit UI (optional)
cd src
streamlit run interface.py
```

---

## 📋 Step-by-Step Windows Setup

### Prerequisites — Install Once

| Tool | Download | Verify |
|------|----------|--------|
| Docker Desktop | https://www.docker.com/products/docker-desktop | `docker --version` |
| Python 3.11+ | https://www.python.org/downloads/ | `python --version` |
| VS Code | https://code.visualstudio.com | — |
| Git | https://git-scm.com/download/win | `git --version` |

**VS Code extensions to install:**
- Python (Microsoft)
- Docker (Microsoft)
- REST Client (Huachao Mao) — for testing API endpoints

---

### Step 1: Clone and open the project

```powershell
git clone <your-repo-url> rag-project
cd rag-project
code .          # opens VS Code in the project folder
```

---

### Step 2: Start the databases with Docker

```powershell
cd docker
copy .env.example .env
```

Open `docker/.env` in VS Code and verify:
```
MONGO_USER=admin
MONGO_PASSWORD=admin123
```

Then start the containers:
```powershell
docker-compose up -d
```

**Verify both containers are running:**
```powershell
docker ps
```
You should see `rag_mongodb` and `rag_qdrant`.

**Verify Qdrant dashboard:**
Open http://localhost:6333/dashboard in your browser.

**Verify MongoDB:**
```powershell
docker exec -it rag_mongodb mongosh -u admin -p admin123
```

---

### Step 3: Set up the Python environment

```powershell
cd src
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
pip install -r requirements.txt
```

Configure the app:
```powershell
copy .env.example .env
```

Open `src/.env` and fill in:
- `OPENAI_API_KEY` — your OpenAI key (or Ollama if running locally)
- Leave everything else as default for now

---

### Step 4: Start the FastAPI backend

```powershell
cd src
uvicorn main:app --reload --port 5000
```

Open http://localhost:5000/docs — you should see the Swagger UI with all endpoints.

---

### Step 5: Start the Streamlit UI (optional)

Open a second PowerShell terminal:
```powershell
cd src
streamlit run interface.py
```

Opens at http://localhost:8501

---

## 🗂️ Project Structure

```
rag-project/
├── docker/                     ← Docker config for MongoDB + Qdrant
│   ├── docker-compose.yaml     ← Defines both DB services
│   ├── .env                    ← DB credentials (git-ignored)
│   └── .env.example            ← Template — copy and fill in
│
└── src/                        ← All Python source code
    ├── main.py                 ★ START HERE — FastAPI app entry point
    ├── interface.py            ★ Streamlit UI
    ├── requirements.txt        ← Python packages
    ├── .env                    ← App secrets (git-ignored)
    ├── Dockerfile              ← Container for the FastAPI app
    │
    ├── helpers/
    │   └── config.py           ← Reads .env into typed Settings class
    │
    ├── controllers/            ← Business logic (no DB queries here)
    │   ├── BaseController.py   ← Parent: provides settings + file paths
    │   ├── DataController.py   ← File validation (MIME, size)
    │   ├── FileController.py   ← Directory management
    │   ├── ProcessController.py← Document loading + chunking (20% grade)
    │   └── NlpController.py    ← Core RAG logic (embed, search, answer)
    │
    ├── models/                 ← MongoDB CRUD (no business logic here)
    │   ├── DataBaseModel.py    ← Parent: provides Motor async DB client
    │   ├── ProjectModel.py     ← projects collection CRUD
    │   ├── ChunkModel.py       ← chunks collection CRUD
    │   └── db_schemes/         ← Pydantic schemas (data contracts)
    │       ├── project.py      ← Project schema
    │       └── data_chunk.py   ← DataChunk + RetrievalDocument schemas
    │
    ├── routes/                 ← FastAPI endpoint definitions
    │   ├── base.py             ← GET /api/ (health check)
    │   ├── data.py             ← POST /api/data/upload + /process
    │   ├── nlp.py              ← POST /api/nlp/index/push, search, answer
    │   └── schema/             ← Pydantic request body schemas
    │       ├── data.py         ← RequestProcess
    │       └── nlp.py          ← PushDataRequest, SearchRequest
    │
    └── stores/                 ← External service integrations
        ├── llm/
        │   ├── LLMInterface.py      ← Abstract contract (Strategy Pattern)
        │   ├── LLMFactory.py        ← Creates providers (Factory Pattern ★ Bonus)
        │   ├── provider/
        │   │   ├── OpenAIProvider.py    ← Text generation via OpenAI API
        │   │   └── EmbeddingProvider.py ← Local embeddings via sentence-transformers
        │   └── template/
        │       ├── template_parser.py   ← Loads + renders prompt templates
        │       └── locales/
        │           ├── en/rag.py    ← English prompts
        │           └── ar/rag.py    ← Arabic prompts (★ Bonus)
        └── vectordb/
            ├── VectorDBInterface.py ← Abstract contract (Strategy Pattern)
            ├── VectorDBFactory.py   ← Creates providers (Factory Pattern)
            └── provider/
                └── QDrantDB.py      ← All Qdrant operations
```

---

## 🔗 API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/` | Health check |
| POST | `/api/data/upload/{project_name}` | Upload a document |
| POST | `/api/data/process/{project_id}` | Chunk the document |
| POST | `/api/nlp/index/push/{project_id}` | Embed + index chunks |
| GET | `/api/nlp/index/info/{project_id}` | Check index status |
| POST | `/api/nlp/index/search/{project_id}` | Semantic search |
| POST | `/api/nlp/index/answer/{project_id}` | Full RAG answer |

Full interactive docs: http://localhost:5000/docs

---

## 🐛 Troubleshooting

**Docker containers not starting:**
```powershell
docker-compose down
docker-compose up -d --force-recreate
```

**Port 27007 already in use:**
Change the port in `docker-compose.yaml` from `"27007:27017"` to `"27017:27017"` and update `MONGODB_URI` in `src/.env`.

**`ModuleNotFoundError` when running uvicorn:**
Make sure your virtual environment is activated:
```powershell
.venv\Scripts\activate
```

**Embedding model download is slow:**
First run downloads BAAI/bge-small-en (~130MB). Subsequent runs use the cache at `~/.cache/huggingface/`.

**Qdrant connection error:**
Verify the container is running: `docker ps | findstr qdrant`
