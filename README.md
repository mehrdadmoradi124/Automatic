# Recipe Agent

This repository contains `recipe_agent.py`, a simple utility for extracting
ingredients from cooking-related text, audio, or video files and storing them in
an Excel sheet. The stored recipes can be searched later by keyword.

## Usage

1. Install dependencies:

```bash
pip install pandas speechrecognition moviepy openpyxl
```

2. Add a recipe from plain text:

```python
from recipe_agent import RecipeAgent
agent = RecipeAgent()
agent.add_from_text("""Pancakes\n1 cup flour\n2 eggs\n1 cup milk""", taste="sweet")
```

3. Add from audio or video files (requires additional dependencies):

```python
agent.add_from_audio("path/to/audio.wav", taste="savory")
agent.add_from_video("path/to/video.mp4", taste="spicy")
```

4. Search recipes:

```python
results = agent.search("sweet")
print(results)
```
