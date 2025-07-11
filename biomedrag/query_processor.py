class QueryProcessor:
    """Simple processor to clean user queries."""

    def process(self, query: str) -> str:
        if not query:
            return ""
        return query.strip()
