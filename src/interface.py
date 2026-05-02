# =============================================================================
# interface.py — Streamlit Interactive UI
# =============================================================================
# PURPOSE:
#   A web UI that walks through all 5 RAG pipeline steps visually.
#   Communicates with the FastAPI backend via HTTP — no direct Python imports.
#
# HOW TO RUN (from src/ directory, in a separate terminal):
#   streamlit run interface.py
#   → Opens at http://localhost:8501
#
# PREREQUISITES:
#   The FastAPI backend must already be running on port 5000:
#   uvicorn main:app --reload --port 5000
#
# LAYOUT:
#   Left column:  Shows what's happening at each step (code/theory)
#   Right column: Live execution buttons and outputs
#
# TEAM NOTE (Member 6 — Phase 4, after endpoints are working):
#   Implement each section below in order (Steps 1 → 5).
#   Use requests.post() and requests.get() to call the FastAPI endpoints.
#   API_BASE is defined below — don't hardcode localhost elsewhere.
# =============================================================================

import streamlit as st
import requests

# ── Configuration ─────────────────────────────────────────────────────────────
API_BASE = "http://localhost:5000/api"      # FastAPI backend base URL

st.set_page_config(
    page_title="Mini-RAG Pipeline",
    page_icon="🧠",
    layout="wide"
)
st.title("🧠 Mini-RAG — Interactive Pipeline")
st.markdown("Walk through the complete RAG pipeline step by step.")


# ── Sidebar: Project Selection ────────────────────────────────────────────────
st.sidebar.header("Project Settings")
project_name = st.sidebar.text_input(
    "Project name (alphanumeric only)",
    value="demoproject"
)
language = st.sidebar.selectbox("Response language", ["en", "ar"])

st.sidebar.markdown("---")
st.sidebar.markdown("**API Status**")
try:
    r = requests.get(f"{API_BASE}/", timeout=2)
    if r.status_code == 200:
        st.sidebar.success("✅ API connected")
    else:
        st.sidebar.error("❌ API returned error")
except:
    st.sidebar.error("❌ API not reachable — start FastAPI first")


# ── Step 1: Upload ────────────────────────────────────────────────────────────
st.header("Step 1: Upload a Document")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **What happens here:**
    - File MIME type is validated (PDF or TXT only)
    - File is saved to `assets/files/<project_name>/`
    - A project record is created in MongoDB
    """)

with col2:
    uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])
    if st.button("📤 Upload") and uploaded_file:
        # TODO (Member 6):
        # files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        # response = requests.post(f"{API_BASE}/data/upload/{project_name}", files=files)
        # st.json(response.json())
        st.info("Upload button clicked — implement API call here")


st.divider()


# ── Step 2: Process (Chunk) ───────────────────────────────────────────────────
st.header("Step 2: Process Document into Chunks")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **What happens here:**
    - File is loaded from disk using PyMuPDF (PDF) or TextLoader (TXT)
    - Arabic text is pre-processed if needed (reshaper + bidi)
    - Text is split into overlapping chunks by RecursiveCharacterTextSplitter
    - Chunks are stored in MongoDB "chunks" collection
    """)

with col2:
    filename = st.text_input("Filename to process", value="document.pdf")
    chunk_size = st.slider("Chunk size (chars)", 100, 2000, 500)
    overlap = st.slider("Overlap (chars)", 0, 200, 50)
    project_id = st.text_input("Project ID (from upload response)", value="")

    if st.button("⚙️ Process"):
        # TODO (Member 6):
        # body = {"project_id": filename, "chunk_size": chunk_size, "overlap": overlap, "do_reset": 0}
        # response = requests.post(f"{API_BASE}/data/process/{project_id}", json=body)
        # st.success(f"Created {response.json()} chunks")
        st.info("Process button clicked — implement API call here")


st.divider()


# ── Step 3: Push to Vector Index ──────────────────────────────────────────────
st.header("Step 3: Push Chunks to Vector Index")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **What happens here:**
    - All chunks are fetched from MongoDB (paginated)
    - Each chunk is embedded by EmbeddingProvider (BAAI/bge-small-en)
    - Vectors are batch-uploaded to Qdrant with text payload
    - A Qdrant collection is created for this project
    """)

with col2:
    if st.button("🔼 Push to Index"):
        # TODO (Member 6):
        # response = requests.post(f"{API_BASE}/nlp/index/push/{project_id}", json={"do_reset": 0})
        # st.json(response.json())
        st.info("Push button clicked — implement API call here")


st.divider()


# ── Step 4: Semantic Search ───────────────────────────────────────────────────
st.header("Step 4: Semantic Search (no LLM)")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **What happens here:**
    - Your query is embedded using the same model as the documents
    - Qdrant finds the top-k most similar chunks by cosine similarity
    - Raw chunks and scores are returned — no LLM involved
    
    *(Use this to debug retrieval quality before running full RAG)*
    """)

with col2:
    search_query = st.text_input("Search query", value="What is the main topic?")
    top_k = st.slider("Top-K results", 1, 10, 5)

    if st.button("🔍 Search"):
        # TODO (Member 6):
        # body = {"text": search_query, "top_k": top_k}
        # response = requests.post(f"{API_BASE}/nlp/index/search/{project_id}", json=body)
        # for result in response.json().get("results", []):
        #     st.markdown(f"**Score:** {result['score']:.3f}")
        #     st.text(result['text'])
        #     st.divider()
        st.info("Search button clicked — implement API call here")


st.divider()


# ── Step 5: RAG Answer ────────────────────────────────────────────────────────
st.header("Step 5: Ask a Question (Full RAG)")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **What happens here:**
    1. Query is embedded and top-k chunks retrieved from Qdrant
    2. Chunks are injected into a prompt template (EN or AR)
    3. Full prompt is sent to the LLM (OpenAI / Ollama)
    4. LLM generates an answer grounded in the retrieved documents
    5. Answer + full prompt + chat history are returned
    """)

with col2:
    question = st.text_input("Your question", value="Summarise the key points.")

    if st.button("🤖 Get RAG Answer"):
        # TODO (Member 6):
        # body = {"text": question, "top_k": top_k, "language": language}
        # response = requests.post(f"{API_BASE}/nlp/index/answer/{project_id}", json=body)
        # data = response.json()
        # st.success("Answer:")
        # st.write(data.get("answer"))
        # with st.expander("Full prompt sent to LLM"):
        #     st.text(data.get("full_prompt"))
        st.info("RAG answer button clicked — implement API call here")
