import json
from .query_processor import QueryProcessor
from .retrieval import LiteratureRetriever
from .embedder import Embedder
from .vector_store import VectorStore
from .rag_generator import RAGAnswerGenerator


class Evaluator:
    """Run sample questions through the pipeline."""

    def __init__(self, questions_file: str):
        with open(questions_file) as f:
            self.questions = json.load(f)
        self.qp = QueryProcessor()
        self.retriever = LiteratureRetriever()
        self.embedder = Embedder()
        self.store = VectorStore()
        self.generator = RAGAnswerGenerator(self.embedder, self.store)

    def evaluate(self, limit: int = 1):
        results = []
        for q in self.questions[:limit]:
            processed = self.qp.process(q)
            try:
                docs = self.retriever.search(processed)
            except Exception as exc:
                docs = []
                print(f"Retrieval failed for '{q}': {exc}")
            answer = self.generator.generate(processed, docs)
            results.append({"question": q, "answer": answer})
        return results


if __name__ == "__main__":
    import sys
    eval_file = sys.argv[1] if len(sys.argv) > 1 else "sample_questions.json"
    ev = Evaluator(eval_file)
    for res in ev.evaluate(limit=3):
        print(f"Q: {res['question']}\nA: {res['answer']}\n")
