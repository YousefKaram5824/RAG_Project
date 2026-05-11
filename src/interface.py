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
HEALTH_URL = "http://localhost:5000/docs"

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

if "last_search_results" not in st.session_state:
    st.session_state.last_search_results = []

if "last_answer_data" not in st.session_state:
    st.session_state.last_answer_data = {}

def safe_request(method, url, **kwargs):
    try:
        return requests.request(method, url, timeout=120, **kwargs)
    except requests.RequestException as exc:
        return exc

def show_progress(label: str, percent: int):
    percent = max(0, min(100, percent))
    st.progress(percent, text=label)


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

health_response = safe_request("GET", HEALTH_URL)
if isinstance(health_response, Exception):
    st.sidebar.error("❌ API not reachable — start FastAPI first")
else:
    if health_response.status_code == 200:
        st.sidebar.success("✅ API connected")
    else:
        st.sidebar.error(f"❌ API returned {health_response.status_code}")

# ── Step 1: Upload ────────────────────────────────────────────────────────────
st.header("Step 1: Upload a Document")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **What happens here:**
    - File is sent as `multipart/form-data`.
    - A MongoDB project record is created
    - The file is saved under the project folder.
    """)

with col2:
    uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])
    if st.button("📤 Upload") and uploaded_file:
        with st.spinner("Uploading..."):
            show_progress("Uploading file...", 20)
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(f"{API_BASE}/data/upload/{project_name}", files=files)
            show_progress("Uploading file...", 100)
            if isinstance(response, Exception):
                st.error(f"Upload failed: {response}")
            elif response.status_code == 200:
                data = response.json()
                st.session_state.project_id = data.get("project_id","")
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
    do_reset = st.selectbox("Reset existing chunks?", [0, 1], index=1)

    if st.button("⚙️ Process"):
        if not pid:
            st.warning("Please upload a file first.")
        elif not target_file:
            st.warning("Missing filename.")
        else:
             with st.spinner("Processing document into chunks..."):
                show_progress("Processing...", 20)
                body = {
                    "project_name": target_file, 
                    "chunk_size": c_size, 
                    "overlap": over, 
                    "do_reset": do_reset
                }
                response = safe_request(
                    "POST",
                    f"{API_BASE}/data/process/{pid}",
                    json=body,
                )
                show_progress("Processing...", 100)
                if isinstance(response, Exception):
                    st.error(f"Processing failed: {response}")
                elif response.status_code == 200:
                    data = response.json()
                    st.success(
                        f"Created {data.get('inserted_chunks', 0)} chunks in MongoDB."
                    )
                    st.json(data)
                else:
                    st.error(f"Processing failed: {response.text}")

        

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
    push_reset = st.selectbox("Reset Qdrant collection?", [0, 1], index=1, key="push_reset")
    if st.button("🔼 Push to Index"):
        if not pid:
            st.warning("Please upload and process a document first.")
        else:
            with st.spinner("Embedding and Indexing..."):
                response = safe_request(
                    "POST",
                    f"{API_BASE}/nlp/index/push/{pid}",
                    json={"do_reset": push_reset},
                )
                if isinstance(response, Exception):
                    st.error(f"Push failed: {response}")
                elif response.status_code == 200:
                    st.success("Successfully pushed to Qdrant!")
                    st.json(response.json())
                else:
                    st.error(f"Push failed: {response.text}")

st.divider()

# ── Step 4: Semantic Search ───────────────────────────────────────────────────
st.header("Step 4: Semantic Search (no LLM)")
col1, col2 = st.columns(2)

with col1:
    st.markdown("Test the retrieval quality without generating an answer.")

with col2:
    search_query = st.text_input("Search query", value="What is the main topic?")
    top_k = st.slider("Top-K results", 1, 10, 5, key="search_top_k")

    if st.button("🔍 Search"):
        if not pid:
            st.warning("Please upload and process a document first.")
        else:
            with st.spinner("Searching vector database..."):
                body = {"text": search_query, "top_k": top_k, "language": language}
                response = safe_request(
                    "POST",
                    f"{API_BASE}/nlp/index/search/{pid}",
                    json=body,
                )
                if isinstance(response, Exception):
                    st.error(f"Search failed: {response}")
                elif response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    st.session_state.last_search_results = results

                    st.success(f"Retrieved {len(results)} chunks")
                    for i, result in enumerate(results, start=1):
                        st.markdown(f"**Rank {i} — Score: {result.get('score', 0):.3f}**")
                        st.info(result.get("text", ""))
                        if result.get("metadata"):
                            with st.expander(f"Metadata for chunk {i}"):
                                st.json(result["metadata"])
                else:
                    st.error(f"Search failed: {response.text}")


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
        if not pid:
            st.warning("Please upload and process a document first.")
        elif not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Consulting the documents..."):
                body = {"text": question, "top_k": top_k, "language": language}
                response = safe_request(
                    "POST",
                    f"{API_BASE}/nlp/index/answer/{pid}",
                    json=body,
                )
                if isinstance(response, Exception):
                    st.error(f"RAG answer failed: {response}")
                elif response.status_code == 200:
                    data = response.json()
                    st.session_state.last_answer_data = data

                    st.subheader("Answer")
                    st.write(data.get("answer", ""))

                    retrieved = (
                        data.get("retrieved_chunks")
                        or data.get("relevant_chunks")
                        or data.get("chunks")
                        or st.session_state.last_search_results
                    )

                    st.subheader("Retrieved Chunks")
                    if retrieved:
                        for i, chunk in enumerate(retrieved, start=1):
                            with st.expander(f"Chunk {i}"):
                                if isinstance(chunk, dict):
                                    st.write(chunk.get("text", chunk.get("chunk_text", "")))
                                    if "score" in chunk:
                                        st.write(f"Score: {chunk['score']:.4f}")
                                    if chunk.get("metadata"):
                                        st.json(chunk["metadata"])
                                else:
                                    st.write(str(chunk))
                    else:
                        st.info("No retrieved chunks were returned by the backend.")

                    with st.expander("Show Technical Details (Prompt)"):
                        st.text_area(
                            "Full Prompt Sent to LLM",
                            data.get("full_prompt", ""),
                            height=300,
                        )

                    if data.get("chat_history") is not None:
                        with st.expander("Chat History"):
                            st.json(data.get("chat_history"))
                else:
                    st.error(f"Failed to generate answer: {response.text}")