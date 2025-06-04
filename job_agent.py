import os
import re
import json
import shutil
import subprocess
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# Configuration constants
GITHUB_REPO = "speedyapply/2025-AI-College-Jobs"
JOB_FILES = {
    "README.md",
    "NEW_GRAD_USA.md",
    "NEW_GRAD_INTL.md",
    "INTERN_INTL.md",
}
LAST_SEEN_FILE = "last_commit.txt"
CV_SUMMARY_FILE = "cv_summary.txt"

# Load OpenAI library if available
try:
    import openai
except ImportError:
    openai = None


def get_latest_commit_sha():
    """Fetch the latest commit SHA on the main branch."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/commits/main"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()["sha"]


def get_changed_files_since(last_sha):
    """Return diff files since the given SHA."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/compare/{last_sha}...main"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json().get("files", [])


def parse_new_jobs_from_patch(patch):
    """Parse newly added table rows from a GitHub patch."""
    jobs = []
    for line in patch.splitlines():
        if line.startswith("+|") and not line.startswith("++"):
            row = line[1:]
            cols = [c.strip() for c in row.split("|")[1:-1]]
            if len(cols) < 6:
                continue
            company = re.sub(r"<.*?>", "", cols[0])
            position = re.sub(r"<.*?>", "", cols[1])
            apply_match = re.search(r"href=\"([^\"]+)\"", cols[4])
            link = apply_match.group(1) if apply_match else ""
            jobs.append({
                "company": company,
                "position": position,
                "link": link,
            })
    return jobs


def fetch_job_description(url):
    """Scrape text from a job posting page."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception:
        return ""
    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text("\n")
    return text


def load_cv_summary():
    if os.path.exists(CV_SUMMARY_FILE):
        with open(CV_SUMMARY_FILE) as f:
            return f.read().strip()
    return ""


def generate_updated_summary(job_desc, current_summary):
    """Use OpenAI to craft a CV summary tailored to the job."""
    if openai is None:
        print("openai package not installed")
        return current_summary
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Missing OPENAI_API_KEY env var")
        return current_summary
    openai.api_key = api_key
    messages = [
        {"role": "system", "content": "You help update CV summaries."},
        {"role": "user", "content": f"Current summary: {current_summary}"},
        {"role": "user", "content": f"Job description: {job_desc}"},
    ]
    resp = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return resp.choices[0].message.content.strip()


def update_overleaf(summary):
    """Update CV in Overleaf Git project with the new summary."""
    repo_url = os.environ.get("OVERLEAF_GIT_URL")
    if not repo_url:
        print("Missing OVERLEAF_GIT_URL env var")
        return None
    tmp = "overleaf_proj"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    subprocess.check_call(["git", "clone", repo_url, tmp])
    tex_file = os.path.join(tmp, "cv.tex")
    if not os.path.exists(tex_file):
        print("cv.tex not found in project")
        return None
    with open(tex_file) as f:
        content = f.read()
    new_content = re.sub(r"(SUMMARY_START).*?(SUMMARY_END)",
                         rf"\1\n{summary}\n\2", content, flags=re.DOTALL)
    with open(tex_file, "w") as f:
        f.write(new_content)
    subprocess.check_call(["git", "add", "cv.tex"], cwd=tmp)
    subprocess.check_call(["git", "commit", "-m", "Update CV summary"], cwd=tmp)
    subprocess.check_call(["git", "push"], cwd=tmp)
    return tmp


def run():
    last_sha = None
    if os.path.exists(LAST_SEEN_FILE):
        with open(LAST_SEEN_FILE) as f:
            last_sha = f.read().strip()
    latest_sha = get_latest_commit_sha()
    if last_sha == latest_sha:
        print("No new commits")
        return
    changed = get_changed_files_since(last_sha) if last_sha else []
    jobs = []
    for file in changed:
        if file.get("filename") in JOB_FILES and "patch" in file:
            jobs.extend(parse_new_jobs_from_patch(file["patch"]))
    with open(LAST_SEEN_FILE, "w") as f:
        f.write(latest_sha)
    if not jobs:
        print("No new jobs found")
        return
    current_summary = load_cv_summary()
    for job in jobs:
        print(f"Processing job: {job['position']} at {job['company']}")
        desc = fetch_job_description(job["link"])
        summary = generate_updated_summary(desc, current_summary)
        proj_dir = update_overleaf(summary)
        if proj_dir:
            pdf_path = os.path.join(proj_dir, "cv.pdf")
            if os.path.exists(pdf_path):
                print(f"Updated CV available at {pdf_path}")
        # Placeholder for job application logic
        # apply_to_job(job["link"], pdf_path)


if __name__ == "__main__":
    run()
