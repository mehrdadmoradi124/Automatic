# Job Application Automation

This repository contains `job_agent.py`, a small utility that watches the public
GitHub repository [speedyapply/2025-AI-College-Jobs](https://github.com/speedyapply/2025-AI-College-Jobs)
for new job postings. Whenever new postings are detected, the agent can update
your CV summary using OpenAI and push the changes to your Overleaf project.

## Installation

1. Ensure you have **Python 3.8+** installed.
2. Install required Python packages:
   ```bash
   pip install requests beautifulsoup4 openai
   ```
3. Make sure `git` is available on your `PATH`.

## Environment variables

The script relies on the following environment variables:

- `OPENAI_API_KEY` – API key used to personalize your CV summary. If this is not
  set, the script will skip the summary update step.
- `OVERLEAF_GIT_URL` – the git URL for your Overleaf project. The project should
  contain a `cv.tex` file with markers `SUMMARY_START` and `SUMMARY_END` where
the summary text will be inserted.

## Usage

Run the agent from the repository root:

```bash
python job_agent.py
```

On the first run it stores the last processed commit in `last_commit.txt` so
subsequent runs only look at new additions. The agent checks for new jobs,
scrapes the posting page to gather a description, then updates the CV summary in
the Overleaf project (if configured). Job application automation is left as a
placeholder for further customization.

`cv_summary.txt` contains the current summary. Edit it manually before running
the agent if you want to start from a different summary.
