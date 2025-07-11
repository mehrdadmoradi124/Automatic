from typing import List


class FeedbackHandler:
    """Stores user feedback to refine answers."""

    def __init__(self):
        self.messages: List[str] = []

    def add(self, feedback: str):
        self.messages.append(feedback)

    def latest(self):
        return self.messages[-1] if self.messages else None
