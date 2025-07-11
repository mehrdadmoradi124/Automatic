import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional


class LiteratureRetriever:
    """Fetches articles from PubMed using E-utilities."""

    def __init__(self, email: Optional[str] = None):
        self.esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        self.email = email

    def search(self, query: str, retmax: int = 5) -> List[Dict[str, str]]:
        """Return a list of articles with pmid, title, and abstract."""
        params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": retmax}
        if self.email:
            params["email"] = self.email
        resp = requests.get(self.esearch_url, params=params, timeout=10)
        resp.raise_for_status()
        ids = resp.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "xml",
        }
        if self.email:
            fetch_params["email"] = self.email
        resp = requests.get(self.efetch_url, params=fetch_params, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
        records = []
        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//PMID")
            title = article.findtext(".//ArticleTitle") or ""
            abstract = " ".join(
                t.text or "" for t in article.findall(".//AbstractText")
            )
            records.append({"pmid": pmid, "title": title, "abstract": abstract})
        return records
