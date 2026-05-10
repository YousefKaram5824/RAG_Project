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

# =============================================================================
# interface.py — Streamlit Interactive UI
# =============================================================================
import streamlit as st
import requests
import time

# ── Configuration ─────────────────────────────────────────────────────────────
API_BASE = "http://localhost:5000/api/v1"

st.set_page_config(
    page_title="Mini-RAG Pipeline",
    page_icon="🧠",
    layout="wide"
)

# Persistent state to store IDs across the pipeline steps
if "project_id" not in st.session_state:
    st.session_state.project_id = ""
if "last_filename" not in st.session_state:
    st.session_state.last_filename = ""

st.title("🧠 Mini-RAG — Interactive Pipeline")
st.markdown("Use this interface to move documents through the ingestion, indexing, and retrieval stages.")

# ── Sidebar: Project Selection ────────────────────────────────────────────────
st.sidebar.header("Project Settings")
project_name = st.sidebar.text_input(
    "Project Directory Name",
    value="demoproject",
    help="Alphanumeric folder name where files are stored."
)
language = st.sidebar.selectbox("Response language", ["en", "ar"])

st.sidebar.markdown("---")
st.sidebar.markdown("**API Status**")
try:
    r = requests.get(f"http://localhost:5000/health", timeout=2) # Health check
    st.sidebar.success("✅ API connected")
except:
    st.sidebar.error("❌ API not reachable — start FastAPI first")

# ── Step 1: Upload ────────────────────────────────────────────────────────────
st.header("Step 1: Upload a Document")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **What happens here:**
    - File is sent as `multipart/form-data`.
    - Backend validates size (max 10MB) and type (PDF/TXT).
    - Returns a **Project ID** (MongoDB Object ID).
    """)

with col2:
    uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])
    if st.button("📤 Upload") and uploaded_file:
        with st.spinner("Uploading..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(f"{API_BASE}/data/upload/{project_name}", files=files)
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.project_id = data.get("project_id")
                st.session_state.last_filename = uploaded_file.name
                st.success(f"Success! Project ID: {st.session_state.project_id}")
                st.json(data)
            else:
                st.error(f"Upload failed: {response.text}")

st.divider()

# ── Step 2: Process (Chunk) ───────────────────────────────────────────────────
st.header("Step 2: Process Document into Chunks")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **What happens here:**
    - Text is extracted and cleaned.
    - `RecursiveCharacterTextSplitter` creates chunks.
    - Chunks are saved to MongoDB for persistence.
    """)

with col2:
    # Use session state or manual override
    pid = st.text_input("Project ID (from Step 1)", value=st.session_state.project_id)
    target_file = st.text_input("Target Filename", value=st.session_state.last_filename)
    c_size = st.slider("Chunk size (chars)", 100, 2000, 500)
    over = st.slider("Overlap (chars)", 0, 200, 50)

    if st.button("⚙️ Process"):
        body = {
            "project_id": target_file, 
            "chunk_size": c_size, 
            "overlap": over, 
            "do_reset": 1
        }
        response = requests.post(f"{API_BASE}/data/process/{pid}", json=body)
        if response.status_code == 200:
            st.success(f"Created {response.json().get('inserted_chunks')} chunks in MongoDB.")
        else:
            st.error("Processing failed.")

st.divider()

# ── Step 3: Push to Vector Index ──────────────────────────────────────────────
st.header("Step 3: Push Chunks to Vector Index")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **What happens here:**
    - Chunks are embedded using `BAAI/bge-small-en`.
    - Vectors are synced to **Qdrant**.
    """)

with col2:
    if st.button("🔼 Push to Index"):
        with st.spinner("Embedding and Indexing..."):
            response = requests.post(f"{API_BASE}/nlp/index/push/{pid}", json={"do_reset": 1})
            if response.status_code == 200:
                st.success("Successfully pushed to Qdrant!")
                st.json(response.json())

st.divider()

# ── Step 4: Semantic Search ───────────────────────────────────────────────────
st.header("Step 4: Semantic Search (no LLM)")
col1, col2 = st.columns(2)

with col1:
    st.markdown("Test the retrieval quality without generating an answer.")

with col2:
    search_query = st.text_input("Search query", value="What is the main topic?")
    top_k = st.slider("Top-K results", 1, 10, 5)

    if st.button("🔍 Search"):
        body = {"text": search_query, "top_k": top_k}
        response = requests.post(f"{API_BASE}/nlp/index/search/{pid}", json=body)
        if response.status_code == 200:
            results = response.json().get("results", [])
            for i, result in enumerate(results):
                st.markdown(f"**Rank {i+1} — Score: {result['score']:.3f}**")
                st.info(result['text'])
        else:
            st.error("Search failed.")

st.divider()

# ── Step 5: RAG Answer ────────────────────────────────────────────────────────
st.header("Step 5: Ask a Question (Full RAG)")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **The Final Output:**
    - Retrieval → Prompt Augmentation → LLM Generation.
    """)

with col2:
    question = st.text_input("Your question", placeholder="e.g., Summarize the document.")

    if st.button("🤖 Get RAG Answer"):
        if not question:
            st.warning("Please enter a question.")
        else:
            with st.spinner("Consulting the documents..."):
                body = {"text": question, "top_k": top_k, "language": language}
                response = requests.post(f"{API_BASE}/nlp/index/answer/{pid}", json=body)
                
                if response.status_code == 200:
                    data = response.json()
                    st.subheader("Answer:")
                    st.write(data.get("answer"))
                    
                    with st.expander("Show Technical Details (Prompt)"):
                        st.text_area("Full Prompt Sent to LLM", data.get("full_prompt"), height=300)
                else:
                    st.error("Failed to generate answer.")