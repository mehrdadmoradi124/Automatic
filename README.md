## Biomedical RAG Agent

This repository also includes a simple biomedical literature search and RAG-based question answering demo located in the `biomedrag` package.

### Installation

Install required packages (FAISS, scikit-learn and Streamlit):

```bash
pip install faiss-cpu scikit-learn streamlit requests
```

### CLI Usage

Run an example query from the command line:

```bash
python -m biomedrag.cli "What is the role of p53 in cancer?"
```

### Streamlit Demo

To launch the web demo:

```bash
streamlit run biomedrag/gui.py
```

### Evaluation

An example evaluation script is provided:

```bash
python -m biomedrag.evaluator sample_questions.json
```

Note that network access may be required to fetch PubMed articles.
