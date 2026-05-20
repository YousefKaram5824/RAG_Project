import streamlit as st
import requests
import os
import html as html_lib
API_BASE = os.getenv("API_BASE", "http://localhost:5000/api/v1")
HEALTH_URL = os.getenv("HEALTH_URL", "http://localhost:5000/health")

st.set_page_config(
    page_title="Mini-RAG | Document Assistant",
    page_icon="page_facing_up",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
.stApp, .stApp > header, [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlock"], [data-testid="block-container"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
.stApp p, .stApp span, .stApp label, .stApp div,
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stMarkdown, .stMarkdown p, .stMarkdown li,
.stCaption, [data-testid="stCaptionContainer"] {
    color: #000000 !important;
}
section[data-testid="stSidebar"] {
    background: #000000 !important;
    border-right: none !important;
}
section[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}
section[data-testid="stSidebar"] .stTextInput input {
    background: #1a1a1a !important;
    border: 1px solid #333333 !important;
    border-radius: 8px !important;
    color: #ffffff !important;
}
section[data-testid="stSidebar"] .stRadio label span {
    color: #afafaf !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: #ffffff !important;
    color: #000000 !important;
    border: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #e2e2e2 !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff !important;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: #efefef !important;
    color: #000000 !important;
    border-radius: 999px !important;
    padding: 8px 20px !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: #000000 !important;
    color: #ffffff !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: #ffffff !important;
}
.status-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 16px; border-radius: 999px;
    font-size: 0.82rem; font-weight: 500;
}
.pill-online { background: #000000; color: #ffffff; }
.pill-offline { background: #efefef; color: #4b4b4b; }
.pill-ready { background: #000000; color: #ffffff; }
.uber-hero { text-align: center; padding: 3rem 1rem 2rem; }
.uber-hero h1 {
    font-size: 3.25rem; font-weight: 700; line-height: 1.23;
    color: #000000 !important; margin-bottom: .5rem;
}
.uber-hero p {
    color: #4b4b4b !important; font-size: 1.05rem;
    max-width: 520px; margin: 0 auto; line-height: 1.5;
}
.uber-card {
    background: #ffffff;
    border-radius: 12px;
    box-shadow: rgba(0,0,0,0.12) 0px 4px 16px;
    padding: 1.5rem; margin-bottom: 1rem;
}
.uber-card-header {
    display: flex; align-items: center; gap: 12px; margin-bottom: .5rem;
}
.uber-card-icon {
    width: 44px; height: 44px; border-radius: 50%;
    background: #efefef;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0; color: #000000;
}
.uber-card-title { font-weight: 700; font-size: 1.1rem; color: #000000 !important; }
.uber-card-sub { font-size: .85rem; color: #4b4b4b !important; }
.file-chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 8px 16px; background: #efefef;
    border-radius: 999px; font-size: .85rem; font-weight: 500;
    color: #000000 !important; margin: 4px 4px 4px 0;
}
.file-chip-sidebar {
    display: block; padding: 8px 14px; margin: 4px 0;
    background: #1a1a1a; border-radius: 8px;
    font-size: .82rem; color: #afafaf !important;
}
.chat-user-bubble {
    background: #000000; color: #ffffff !important;
    padding: 14px 20px; border-radius: 20px 20px 4px 20px;
    margin: 10px 0; max-width: 72%; margin-left: auto;
    font-size: .95rem; line-height: 1.55; word-wrap: break-word;
}
.chat-bot-bubble {
    background: #efefef; color: #000000 !important;
    padding: 14px 20px; border-radius: 20px 20px 20px 4px;
    margin: 10px 0; max-width: 82%;
    font-size: .95rem; line-height: 1.65; word-wrap: break-word;
}
.step-row {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 16px; margin: 4px 0;
    background: #efefef; border-radius: 999px;
    font-size: .88rem; font-weight: 500; color: #000000 !important;
}
.step-num {
    width: 26px; height: 26px; border-radius: 50%;
    background: #000000; color: #ffffff;
    display: flex; align-items: center; justify-content: center;
    font-size: .75rem; font-weight: 700; flex-shrink: 0;
}
.progress-step {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 0; font-size: .88rem; color: #4b4b4b !important;
}
.dot-active {
    width: 10px; height: 10px; border-radius: 50%;
    background: #000000; flex-shrink: 0;
    animation: uber-pulse 1.4s infinite;
}
@keyframes uber-pulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(0,0,0,.3); }
    50% { box-shadow: 0 0 0 6px rgba(0,0,0,0); }
}
.empty-state { text-align: center; padding: 4rem 2rem; }
.empty-state h3 { color: #000000 !important; font-weight: 700; margin-bottom: .4rem; }
.empty-state p { color: #4b4b4b !important; max-width: 380px; margin: 0 auto; }
.stButton > button {
    border-radius: 999px !important;
    font-weight: 500 !important;
    padding: 0.6rem 1.5rem !important;
    transition: background .15s, transform .1s !important;
}
.stButton > button:active { transform: scale(0.97); }
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: #000000 !important;
    color: #ffffff !important;
    border: none !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: #333333 !important;
}
/* Secondary buttons in main area */
.stApp .stButton > button[kind="secondary"],
.stApp .stButton > button[data-testid="stBaseButton-secondary"] {
    background: #efefef !important;
    color: #000000 !important;
    border: none !important;
}
.stApp .stButton > button[kind="secondary"]:hover,
.stApp .stButton > button[data-testid="stBaseButton-secondary"]:hover {
    background: #e2e2e2 !important;
}
.uber-divider { height: 1px; background: #222222; margin: 1.2rem 0; }

/* ── Upload Zone ── */
[data-testid="stFileUploader"] {
    border: 2px dashed #e2e2e2 !important;
    border-radius: 12px !important;
    background: #ffffff !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #000000 !important;
}
[data-testid="stFileUploader"] * {
    color: #000000 !important;
}
.dup-warning {
    background: #efefef; border-left: 4px solid #000000;
    padding: 10px 14px; border-radius: 0 8px 8px 0;
    font-size: .85rem; color: #000000 !important; margin: 8px 0;
}
[data-testid="stChatInput"] textarea {
    background: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 999px !important;
}
.stSpinner > div { color: #000000 !important; }
.streamlit-expanderHeader { color: #000000 !important; }
.stProgress > div > div {
    background-color: #000000 !important;
}
[data-testid="stAlert"] {
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

DEFAULTS = {
    "project_id": "workspace",
    "uploaded_files": [],
    "indexed": False,
    "chat_history": [],
    "language": "en",
    "is_processing": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

def api_healthy() -> bool:
    try:
        return requests.get(HEALTH_URL, timeout=2).status_code == 200
    except Exception:
        return False

def api_upload(file_obj, project_id: str):
    files = {"file": (file_obj.name, file_obj.getvalue(), file_obj.type)}
    try:
        r = requests.post(f"{API_BASE}/data/upload/{project_id}", files=files, timeout=60)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def api_process(project_id: str, file_id: str, chunk_size=500, overlap=50):
    body = {"file_id": file_id, "chunk_size": chunk_size, "overlap": overlap, "do_reset": 1}
    try:
        r = requests.post(f"{API_BASE}/data/process/{project_id}", json=body, timeout=120)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def api_push_index(project_id: str):
    try:
        r = requests.post(f"{API_BASE}/nlp/index/push/{project_id}", json={"do_reset": 1}, timeout=300)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def api_answer(project_id: str, question: str, language="en", top_k=5):
    body = {"text": question, "top_k": top_k, "language": language}
    try:
        r = requests.post(f"{API_BASE}/nlp/index/answer/{project_id}", json=body, timeout=120)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def api_search(project_id: str, query: str, top_k=5):
    body = {"text": query, "top_k": top_k}
    try:
        r = requests.post(f"{API_BASE}/nlp/index/search/{project_id}", json=body, timeout=60)
        return r.json().get("results", []) if r.status_code == 200 else []
    except Exception:
        return []

def already_uploaded(filename: str) -> bool:
    return any(f["name"] == filename for f in st.session_state.uploaded_files)


# Sidebar
with st.sidebar:
    st.markdown("### Mini-RAG")
    st.caption("Document Assistant")
    st.markdown('<div class="uber-divider"></div>', unsafe_allow_html=True)

    # Health
    if api_healthy():
        st.markdown('<span class="status-pill pill-online">Online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-pill pill-offline">Offline</span>', unsafe_allow_html=True)
        st.error("Backend not reachable.")

    st.markdown('<div class="uber-divider"></div>', unsafe_allow_html=True)

    # Workspace
    st.markdown("**Workspace**")
    st.session_state.project_id = st.text_input(
        "Workspace", value=st.session_state.project_id,
        label_visibility="collapsed", placeholder="e.g. my-resumes",
    )

    st.markdown('<div class="uber-divider"></div>', unsafe_allow_html=True)

    # Language
    st.markdown("**Language**")
    lang = st.radio("Lang", ["English", "Arabic"], horizontal=True, label_visibility="collapsed")
    st.session_state.language = "en" if lang == "English" else "ar"

    st.markdown('<div class="uber-divider"></div>', unsafe_allow_html=True)

    # Uploaded docs
    if st.session_state.uploaded_files:
        st.markdown("**Documents**")
        for f in st.session_state.uploaded_files:
            chunks_txt = f" — {f.get('chunks', '?')} segments" if "chunks" in f else ""
            st.markdown(
                f'<div class="file-chip-sidebar">{f["name"]}{chunks_txt}</div>',
                unsafe_allow_html=True,
            )
        if st.session_state.indexed:
            st.markdown(
                '<span class="status-pill pill-ready">Ready</span>',
                unsafe_allow_html=True,
            )
    else:
        st.caption("No documents yet.")

    st.markdown('<div class="uber-divider"></div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Clear chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    with col_b:
        if st.button("Reset all", use_container_width=True):
            for k, v in DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()

# Hero
st.markdown("""
<div class="uber-hero">
    <h1>Document Assistant</h1>
    <p>Upload documents. Ask questions. Get AI-powered answers grounded in your own files.</p>
</div>
""", unsafe_allow_html=True)

tab_upload, tab_chat = st.tabs(["Upload", "Chat"])


# TAB 1 — Upload
with tab_upload:
    col_main, col_info = st.columns([3, 2], gap="large")

    with col_main:
        st.markdown("""
        <div class="uber-card">
            <div class="uber-card-header">
                <div class="uber-card-icon">+</div>
                <div>
                    <div class="uber-card-title">Upload Documents</div>
                    <div class="uber-card-sub">PDF and TXT — Max 10 MB each</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Drop files here", type=["pdf", "txt"],
            accept_multiple_files=True, label_visibility="collapsed",
            key="file_uploader",
        )

        if uploaded_files:
            new_files_to_upload = []
            duplicates = []
            for uf in uploaded_files:
                if already_uploaded(uf.name):
                    duplicates.append(uf.name)
                else:
                    new_files_to_upload.append(uf)

            if duplicates:
                dup_list = ", ".join(f"**{d}**" for d in duplicates)
                st.markdown(
                    f'<div class="dup-warning">Already uploaded (skipped): {dup_list}</div>',
                    unsafe_allow_html=True,
                )

            if new_files_to_upload:
                st.markdown(f"**{len(new_files_to_upload)}** new file(s) ready")

                btn_disabled = st.session_state.is_processing
                btn_label = "Processing..." if btn_disabled else "Upload and Prepare"

                if st.button(btn_label, type="primary", use_container_width=True, disabled=btn_disabled):
                    st.session_state.is_processing = True
                    pid = st.session_state.project_id
                    progress = st.progress(0)
                    status_el = st.empty()
                    total = len(new_files_to_upload) * 2 + 1
                    step = 0
                    ok = True
                    processed = []

                    # 1. Upload
                    for i, uf in enumerate(new_files_to_upload):
                        status_el.markdown(
                            f'<div class="progress-step"><span class="dot-active"></span>'
                            f'Uploading {uf.name} ({i+1}/{len(new_files_to_upload)})</div>',
                            unsafe_allow_html=True,
                        )
                        res = api_upload(uf, pid)
                        if res:
                            processed.append({"name": uf.name, "file_id": res.get("file_id", uf.name)})
                            step += 1
                            progress.progress(step / total)
                        else:
                            st.error(f"Upload failed: **{uf.name}**")
                            ok = False
                            break

                    # 2. Process
                    if ok:
                        for i, fi in enumerate(processed):
                            status_el.markdown(
                                f'<div class="progress-step"><span class="dot-active"></span>'
                                f'Processing {fi["name"]} ({i+1}/{len(processed)})</div>',
                                unsafe_allow_html=True,
                            )
                            res = api_process(pid, fi["file_id"])
                            if res:
                                fi["chunks"] = res.get("inserted_chunks", 0)
                                step += 1
                                progress.progress(step / total)
                            else:
                                st.error(f"Processing failed: **{fi['name']}**")
                                ok = False
                                break

                    # 3. Index
                    if ok:
                        status_el.markdown(
                            '<div class="progress-step"><span class="dot-active"></span>'
                            'Building search index...</div>',
                            unsafe_allow_html=True,
                        )
                        res = api_push_index(pid)
                        if res:
                            progress.progress(1.0)
                            st.session_state.uploaded_files.extend(processed)
                            st.session_state.indexed = True
                        else:
                            st.error("Indexing failed. Please try again.")
                            ok = False

                    st.session_state.is_processing = False
                    if ok:
                        status_el.empty()
                        progress.empty()
                        n_chunks = sum(f.get("chunks", 0) for f in processed)
                        st.success(
                            f"{len(processed)} document(s) ready — {n_chunks} segments indexed. "
                            f"Go to the Chat tab to ask questions."
                        )

            elif not new_files_to_upload and duplicates:
                st.info("All selected files have already been uploaded.")

    with col_info:
        st.markdown("""
        <div class="uber-card">
            <div class="uber-card-header">
                <div class="uber-card-icon">?</div>
                <div>
                    <div class="uber-card-title">How It Works</div>
                    <div class="uber-card-sub">Three simple steps</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="step-row"><span class="step-num">1</span> Upload your PDF or TXT documents</div>
        <div class="step-row"><span class="step-num">2</span> System reads, splits, and indexes them</div>
        <div class="step-row"><span class="step-num">3</span> Ask any question in the Chat tab</div>
        """, unsafe_allow_html=True)

        st.markdown("")
        st.markdown("""
        **Tips for best results**
        - Upload files about the same topic for focused answers
        - Ask clear, specific questions
        - Try switching between English and Arabic
        """)

        if st.session_state.uploaded_files:
            st.markdown("---")
            st.markdown("**Workspace files**")
            for f in st.session_state.uploaded_files:
                ch = f.get("chunks", "—")
                st.markdown(
                    f'<span class="file-chip">{f["name"]} — {ch} segments</span>',
                    unsafe_allow_html=True,
                )


# TAB 2 — Chat
with tab_chat:
    if not st.session_state.indexed:
        st.markdown("""
        <div class="empty-state">
            <h3>No documents yet</h3>
            <p>Upload documents in the Upload tab first, then come back here to ask questions.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            safe = html_lib.escape(msg["content"])
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user-bubble">{safe}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bot-bubble">{safe}</div>', unsafe_allow_html=True)
                if msg.get("sources"):
                    with st.expander("View sources", expanded=False):
                        for i, src in enumerate(msg["sources"], 1):
                            score = f" — {src['score']:.0%}" if "score" in src else ""
                            st.markdown(f"**Source {i}**{score}")
                            txt = src.get("text", "")
                            st.caption(txt[:300] + ("..." if len(txt) > 300 else ""))
                            if i < len(msg["sources"]):
                                st.markdown("---")

        question = st.chat_input("Ask anything about your documents...")

        if question:
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.markdown(
                f'<div class="chat-user-bubble">{html_lib.escape(question)}</div>',
                unsafe_allow_html=True,
            )

            with st.spinner("Thinking..."):
                pid = st.session_state.project_id
                answer_data = api_answer(pid, question, st.session_state.language)
                sources = api_search(pid, question, top_k=3)

                if answer_data:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer_data.get("answer", "No relevant answer found."),
                        "sources": sources,
                    })
                else:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": "Something went wrong. Please try again.",
                    })

            st.rerun()