import streamlit as st
from .query_processor import QueryProcessor
from .retrieval import LiteratureRetriever
from .embedder import Embedder
from .vector_store import VectorStore
from .rag_generator import RAGAnswerGenerator
from .feedback_handler import FeedbackHandler


def main():
    st.title("Biomedical RAG QA")
    qp = QueryProcessor()
    retriever = LiteratureRetriever()
    embedder = Embedder()
    store = VectorStore()
    generator = RAGAnswerGenerator(embedder, store)
    feedback = FeedbackHandler()

    if "history" not in st.session_state:
        st.session_state.history = []

    query = st.text_input("Ask a biomedical question:")
    if st.button("Submit") and query:
        processed = qp.process(query)
        try:
            docs = retriever.search(processed, retmax=5)
        except Exception as exc:
            st.error(f"Retrieval failed: {exc}")
            docs = []
        answer = generator.generate(processed, docs)
        st.session_state.history.append({"query": query, "answer": answer})

    for entry in st.session_state.history:
        st.markdown(f"**Q:** {entry['query']}")
        st.markdown(f"**A:** {entry['answer']}")
        st.markdown("---")

    fb = st.text_input("Feedback", key="feedback")
    if st.button("Send Feedback") and fb:
        feedback.add(fb)
        st.success("Feedback stored")


if __name__ == "__main__":
    main()
