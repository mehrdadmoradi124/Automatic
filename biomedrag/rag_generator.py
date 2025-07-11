from typing import List, Dict
import os

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None


class RAGAnswerGenerator:
    """Retrieve-then-answer generation pipeline."""

    def __init__(self, embedder, vector_store):
        self.embedder = embedder
        self.vector_store = vector_store

    def generate(self, query: str, documents: List[Dict[str, str]], top_k: int = 3) -> str:
        texts = [doc.get("abstract") or doc.get("title", "") for doc in documents]
        if texts:
            embeddings = self.embedder.fit_transform(texts)
            self.vector_store.build(embeddings, documents)
            q_vec = self.embedder.transform([query])
            top_docs, _ = self.vector_store.search(q_vec, k=top_k)
        else:
            top_docs = []
        context = "\n\n".join(
            f"PMID:{d['pmid']} Title:{d['title']} Abstract:{d['abstract']}" for d in top_docs
        )
        prompt = (
            "Answer the biomedical question using the documents provided. "
            "Cite PMIDs in your answer.\n" + context + f"\nQuestion: {query}\nAnswer:"
        )
        if openai and os.getenv("OPENAI_API_KEY"):
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.choices[0].message.content.strip()
        # Fallback: simple concatenation
        if top_docs:
            snippets = "\n\n".join(d["abstract"] for d in top_docs)
            answer = f"Based on the following articles:\n{snippets}\n\nQuestion: {query}\n"
            answer += "Please refer to the cited PMIDs for details."
        else:
            answer = "No relevant documents were retrieved to answer the question."
            answer += f"\nQuestion: {query}"
        return answer
