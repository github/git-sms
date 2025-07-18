from fastapi import FastAPI, Form
from fastapi.responses import Response
import requests, os, html
from dotenv import load_dotenv
from natural_language_router import route_natural_command
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

load_dotenv()
app = FastAPI()

# Azure OpenAI configuration
endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4o"
token = os.getenv("GITHUB_OPENAI_API_KEY")

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def ask_openai(prompt: str):
    prompt += "\n\nLimit the summary to no more than 1,000 characters. Return plain text only. No formatting."
    print("\n[ask_openai] Prompt being sent:\n", prompt)

    try:
        response = client.complete(
            messages=[
                SystemMessage("You are a helpful assistant."),
                UserMessage(prompt),
            ],
            temperature=0.7,
            top_p=1.0,
            max_tokens=700,
            model=model_name
        )
        if not response or not response.choices:
            print("[ask_openai] No choices returned.")
            return "Sorry, no summary was generated."

        result = response.choices[0].message.content.strip()
        print(f"[ask_openai] Response length: {len(result)}")

        if len(result) > 1000:
            print("[ask_openai] Response too long.")
            return "The summary was too long to send. Try summarizing a smaller repo or issue."

        return result

    except Exception as e:
        print("[ask_openai] Exception:", e)
        return "AI summarization failed. Please try again later."

@app.post("/webhook")
async def sms_webhook(From: str = Form(...), Body: str = Form(...)):
    text = Body.strip()
    print(f"\n[webhook] Incoming from {From}: {text}")
    parts = text.split()

    if text.lower().startswith("create repo") and len(parts) >= 3:
        repo_name = parts[2]
        success = create_repo(repo_name)
        return twilio_reply(f"Created repo '{repo_name}'" if success else f"Failed to create repo '{repo_name}'.")

    if text.lower().startswith("create issue") and len(parts) >= 4:
        try:
            pre, body = text.split(" -- ", 1)
            _, _, repo, *title_parts = pre.split()
            title = " ".join(title_parts)
            success = create_issue(repo, title, body)
            return twilio_reply(f"Issue created in '{repo}'" if success else f"Failed to create issue in '{repo}'.")
        except ValueError:
            return twilio_reply("Usage: create issue <repo> <title> -- <body>")

    if text.lower() == "help":
        return twilio_reply(
            "Available commands:\n"
            "- summarize owner/repo\n"
            "- summarize owner/repo issue [#]"
        )

    if text.lower().startswith("summarize") and len(parts) >= 2 and "/" in parts[1]:
        owner_repo = parts[1]
        if len(parts) >= 4 and parts[2].lower() == "issue" and parts[3].isdigit():
            issue_number = int(parts[3])
            summary = summarize_specific_issue(owner_repo, issue_number)
            return twilio_reply(summary or "Could not summarize issue.")
        elif len(parts) >= 3 and parts[2].lower() == "issue":
            summary = summarize_latest_issue(owner_repo)
            return twilio_reply(summary or "Could not summarize the latest issue.")
        else:
            summary = summarize_any_repo(owner_repo)
            return twilio_reply(summary or "Could not summarize that repo.")

    # 🔁 Fall back to natural language routing
    print("[fallback] Attempting natural language parse")
    fallback = route_natural_command(text)
    if fallback:
        return twilio_reply(fallback)

    return twilio_reply("Unrecognized command. Text 'help' for available options.")

def get_headers():
    # Only read-only access with no authentication token
    return {
        "Accept": "application/vnd.github+json"
    }

def create_repo(name):
    # Write operations are disabled in this prototype.
    print("[create_repo] Disabled: write operations are disabled in this prototype.")
    return False

def create_issue(repo, title, body):
    # Write operations are disabled in this prototype.
    print("[create_issue] Disabled: write operations are disabled in this prototype.")
    return False

def summarize_any_repo(owner_repo):
    try:
        owner, repo = owner_repo.split("/")
    except ValueError:
        return "Invalid format. Use <owner>/<repo>"

    readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Accept": "application/vnd.github+json"}

    readme_res = requests.get(readme_url, headers=headers)
    repo_res = requests.get(repo_url, headers=headers)

    if not readme_res.ok or not repo_res.ok:
        return None

    try:
        download_url = readme_res.json().get("download_url")
        readme_content = requests.get(download_url).text if download_url else "No README found."
        if len(readme_content) > 4000:
            readme_content = readme_content[:4000]
    except Exception as e:
        print("[summarize_any_repo] Error downloading README:", e)
        readme_content = "No README content available."

    repo_data = repo_res.json()
    prompt = f"""
Summarize this GitHub repo:

Repo Name: {repo_data.get('name') or 'Unknown'}
Owner: {owner}
Description: {repo_data.get('description') or 'No description'}
Stars: {repo_data.get('stargazers_count', 0)}
Forks: {repo_data.get('forks_count', 0)}
Primary Language: {repo_data.get('language') or 'Unknown'}

README:
{readme_content}
"""
    return ask_openai(prompt)

def summarize_latest_issue(owner_repo):
    try:
        owner, repo = owner_repo.split("/")
    except ValueError:
        return "Invalid format. Use <owner>/<repo>"

    issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    res = requests.get(issues_url, headers=get_headers(), params={"state": "open", "per_page": 1})
    if not res.ok or not res.json():
        print("[summarize_latest_issue] Issue fetch failed:", res.status_code)
        return None

    issue = res.json()[0]
    return summarize_issue_thread(owner, repo, issue["number"])

def summarize_specific_issue(owner_repo, issue_number):
    try:
        owner, repo = owner_repo.split("/")
    except ValueError:
        return "Invalid format. Use <owner>/<repo>"

    return summarize_issue_thread(owner, repo, issue_number)

def summarize_issue_thread(owner, repo, issue_number):
    issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    comments_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    issue_res = requests.get(issue_url, headers=get_headers())
    comments_res = requests.get(comments_url, headers=get_headers())

    if not issue_res.ok or not comments_res.ok:
        print("[summarize_issue_thread] Failed to fetch issue or comments.")
        return None

    issue = issue_res.json()
    thread = f"Issue #{issue_number}: {issue.get('title')}\n{issue.get('body', '')}"
    for comment in comments_res.json():
        thread += "\n" + comment.get("body", "")

    prompt = f"Summarize this GitHub issue thread:\n{thread}"
    return ask_openai(prompt)

def twilio_reply(message: str):
    print("[twilio_reply] Responding with message:", message)
    escaped = html.escape(message or "No content.")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{escaped}</Message>
</Response>"""
    return Response(content=xml, media_type="application/xml")
