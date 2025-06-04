import os
import re
from dataclasses import dataclass, field
from typing import List, Optional

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

@dataclass
class Recipe:
    name: str
    ingredients: List[str]
    amounts: List[str] = field(default_factory=list)
    taste: Optional[str] = None

class RecipeAgent:
    def __init__(self, excel_path: str = "recipes.xlsx"):
        if pd is None:
            raise ImportError("pandas is required to use RecipeAgent")
        self.excel_path = excel_path
        if os.path.exists(excel_path):
            self.df = pd.read_excel(excel_path)
        else:
            self.df = pd.DataFrame(columns=["name", "ingredients", "amounts", "taste"])

    def _save(self):
        self.df.to_excel(self.excel_path, index=False)

    def _parse_text(self, text: str) -> Recipe:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        name = lines[0] if lines else "unknown"
        ingredient_lines = [l for l in lines[1:] if re.search(r"\d", l)]
        ingredients = []
        amounts = []
        for line in ingredient_lines:
            match = re.match(r"(\d+\s*[^\s]+)\s+(.*)", line)
            if match:
                amounts.append(match.group(1))
                ingredients.append(match.group(2))
            else:
                ingredients.append(line)
                amounts.append("")
        return Recipe(name=name, ingredients=ingredients, amounts=amounts)

    def add_from_text(self, text: str, taste: Optional[str] = None):
        recipe = self._parse_text(text)
        recipe.taste = taste
        self.df.loc[len(self.df)] = {
            "name": recipe.name,
            "ingredients": ", ".join(recipe.ingredients),
            "amounts": ", ".join(recipe.amounts),
            "taste": taste or ""
        }
        self._save()
        return recipe

    def add_from_audio(self, audio_path: str, taste: Optional[str] = None):
        if sr is None:
            raise ImportError("speech_recognition is required for audio processing")
        r = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)
        text = r.recognize_google(audio)
        return self.add_from_text(text, taste)

    def add_from_video(self, video_path: str, taste: Optional[str] = None):
        try:
            from moviepy.editor import VideoFileClip
        except ImportError:
            raise ImportError("moviepy is required for video processing")
        clip = VideoFileClip(video_path)
        audio_path = "temp_audio.wav"
        clip.audio.write_audiofile(audio_path)
        recipe = self.add_from_audio(audio_path, taste)
        os.remove(audio_path)
        return recipe

    def search(self, keyword: str):
        if self.df.empty:
            return None
        mask = self.df.apply(lambda row: keyword.lower() in str(row).lower(), axis=1)
        results = self.df[mask]
        return results

if __name__ == "__main__":
    agent = RecipeAgent()
    # Example usage
    # agent.add_from_text("""Pancakes\n1 cup flour\n2 eggs\n1 cup milk""", taste="sweet")
    # print(agent.search("sweet"))
