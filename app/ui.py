# app/ui.py
import streamlit as st
import os
import tempfile
from app.pipeline import ask
from app.embeddings_manager import embed_document
from app.llm import check_ollama_health

st.set_page_config(
    page_title="RAG Document Q&A",
    page_icon="📚",
    layout="wide"
)

with st.sidebar:
    st.title("📚 RAG Document Management System")
    st.markdown("---")

    if check_ollama_health():
        st.success("🟢 LLM Connected")
    else:
        st.error("🔴 LLM Offline — run `ollama serve`")

    st.markdown("---")
    st.subheader("Upload Document")

    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT file",
        type=["pdf", "txt", "docx"]
    )

    if uploaded_file and st.button("Process Document", type="primary"):
        with st.spinner("Processing..."):
            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            try:
                from app.ingestion import ingest_document
                doc_id = ingest_document(tmp_path, uploaded_file.name)
                
                n_chunks = embed_document(doc_id)
                
                st.success(f"✅ Processed {n_chunks} chunks from '{uploaded_file.name}'")
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                os.unlink(tmp_path)

st.title("Ask Your Documents")
st.markdown("Upload documents in the sidebar, then ask questions below.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("📎 Sources"):
                for s in message["sources"]:
                    st.markdown(
                        f"**{s['filename']}** — relevance: `{s['relevance_score']}`"
                    )

if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = ask(prompt)

        st.markdown(result["answer"])

        if result["sources"]:
            with st.expander(f"📎 {len(result['sources'])} source(s) used"):
                for s in result["sources"]:
                    st.markdown(
                        f"**{s['filename']}** — relevance: `{s['relevance_score']}`"
                    )

        st.caption(f"⏱️ {result['response_time_ms']}ms")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"]
    })
