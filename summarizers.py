import os
import requests
import tiktoken
import logging
from dotenv import load_dotenv

load_dotenv()

# Setup logging
log = logging.getLogger(__name__)

# OpenAI configuration (Azure preferred if available)
USE_AZURE = bool(os.getenv("GITHUB_OPENAI_API_KEY"))
if USE_AZURE:
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.core.credentials import AzureKeyCredential

    AZURE_ENDPOINT = "https://models.github.ai/inference"
    MODEL_NAME = "openai/gpt-4o"
    AZURE_TOKEN = os.getenv("GITHUB_OPENAI_API_KEY")

    client = ChatCompletionsClient(
        endpoint=AZURE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_TOKEN),
    )
else:
    from openai import OpenAI
    MODEL_NAME = "gpt-4o"
    OPENAI_TOKEN = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_TOKEN)

ENCODER = tiktoken.get_encoding("cl100k_base")
MAX_TOKENS = 16000

def num_tokens(text):
    return len(ENCODER.encode(text))

def truncate_text(text, token_limit):
    tokens = ENCODER.encode(text)
    return ENCODER.decode(tokens[:token_limit])

def ask_openai(prompt):
    try:
        if USE_AZURE:
            response = client.complete(
                model=MODEL_NAME,
                temperature=0.2,
                max_tokens=700,
                messages=[
                    SystemMessage(content="Summarize GitHub repo content in under 1000 characters."),
                    UserMessage(content=prompt)
                ]
            )
            return response.choices[0].message.content.strip()
        else:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                temperature=0.2,
                max_tokens=700,
                messages=[
                    {"role": "system", "content": "Summarize GitHub repo content in under 1000 characters."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
    except Exception as e:
        log.error("[ask_openai] Error: %s", e)
        return None

def summarize_any_repo(repo_full_name):
    print(f"[summarize_any_repo] Summarizing {repo_full_name}")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"
    }

    repo_url = f"https://api.github.com/repos/{repo_full_name}"
    readme_url = f"{repo_url}/readme"

    try:
        repo_res = requests.get(repo_url, headers=headers)
        readme_res = requests.get(readme_url, headers=headers)

        if not repo_res.ok:
            return "Could not find repo."

        repo = repo_res.json()
        readme = readme_res.json().get("content", "") if readme_res.ok else ""

        readme = readme.encode("utf-8")
        import base64
        readme_text = base64.b64decode(readme).decode("utf-8", errors="ignore")

        prompt = f"""
Summarize this GitHub repo:

Repo Name: {repo.get("name")}
Owner: {repo.get("owner", {}).get("login")}
Description: {repo.get("description")}
Stars: {repo.get("stargazers_count")}
Forks: {repo.get("forks_count")}
Primary Language: {repo.get("language")}

README:
{readme_text}
        """.strip()

        total_tokens = num_tokens(prompt)
        if total_tokens > MAX_TOKENS:
            print(f"[summarize_any_repo] Trimming README to fit {MAX_TOKENS} token budget.")
            allowable_tokens = MAX_TOKENS - num_tokens(prompt) + num_tokens(readme_text)
            readme_text = truncate_text(readme_text, allowable_tokens)
            prompt = f"""
Summarize this GitHub repo:

Repo Name: {repo.get("name")}
Owner: {repo.get("owner", {}).get("login")}
Description: {repo.get("description")}
Stars: {repo.get("stargazers_count")}
Forks: {repo.get("forks_count")}
Primary Language: {repo.get("language")}

README:
{readme_text}
            """.strip()

        summary = ask_openai(prompt)
        return summary or "AI summarization failed."

    except Exception as e:
        log.error("[summarize_any_repo] Error: %s", e)
        return "Something went wrong."

def summarize_latest_issue(repo_full_name):
    print(f"[summarize_latest_issue] Summarizing latest issue in {repo_full_name}")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"
    }

    issues_url = f"https://api.github.com/repos/{repo_full_name}/issues"
    try:
        res = requests.get(issues_url, headers=headers, params={"state": "open", "per_page": 1})
        if not res.ok or not res.json():
            return "No issues found."
        issue = res.json()[0]

        issue_text = f"Issue #{issue['number']}: {issue['title']}\n{issue.get('body', '')}"
        prompt = f"Summarize this GitHub issue thread:\n{issue_text}\n\nLimit the summary to no more than 1,000 characters. Return plain text only. No formatting."

        summary = ask_openai(prompt)
        return summary or "AI summarization failed."
    except Exception as e:
        log.error("[summarize_latest_issue] Error: %s", e)
        return "Failed to summarize issue."
