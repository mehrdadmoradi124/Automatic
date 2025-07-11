import argparse
from .query_processor import QueryProcessor
from .retrieval import LiteratureRetriever
from .embedder import Embedder
from .vector_store import VectorStore
from .rag_generator import RAGAnswerGenerator


def main():
    parser = argparse.ArgumentParser(description="Biomedical RAG CLI")
    parser.add_argument("question", help="Question to answer")
    args = parser.parse_args()

    qp = QueryProcessor()
    retriever = LiteratureRetriever()
    embedder = Embedder()
    store = VectorStore()
    generator = RAGAnswerGenerator(embedder, store)

    q = qp.process(args.question)
    try:
        docs = retriever.search(q)
    except Exception as exc:
        print(f"Retrieval failed: {exc}")
        docs = []
    ans = generator.generate(q, docs)
    print(ans)


if __name__ == "__main__":
    main()
