import os
import json
import requests
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from summarizers import summarize_any_repo, summarize_latest_issue
from commands import create_repo, create_issue

load_dotenv()

# Azure OpenAI config
endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4o"
token = os.getenv("GITHUB_OPENAI_API_KEY")

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def github_search_repo(query):
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github+json"
    }

    terms = "+".join(query.strip().split())
    url = f"https://api.github.com/search/repositories?q={terms}+in:name,description&sort=stars&order=desc&per_page=10"

    try:
        res = requests.get(url, headers=headers)
        if res.ok:
            items = res.json().get("items", [])
            query_lower = query.lower()

            # Prefer exact or substring match in full_name
            for item in items:
                if item["name"].lower() == query_lower or query_lower in item["full_name"].lower():
                    print("[github_search_repo] Strong match:", item["full_name"])
                    return item["full_name"]

            # Fallback: check description/name contains query
            for item in items:
                if query_lower in (item.get("description") or "").lower() or query_lower in item["name"].lower():
                    print("[github_search_repo] Soft match:", item["full_name"])
                    return item["full_name"]

            if items:
                print("[github_search_repo] Weak fallback match:", items[0]["full_name"])
                return items[0]["full_name"]
    except Exception as e:
        print("[github_search_repo] Error:", e)

    return None

def parse_command_naturally(user_input: str):
    prompt = f'''
You are a GitHub command interpreter. Your job is to extract structured command intents from natural language inputs.

Output your result as JSON with keys: action, repo, title, body, issue_number (use null for any missing fields).

Examples:
Input: "What is internet in a box?"
{{"action": "summarize_repo", "repo": null, "title": null, "body": null, "issue_number": null}}

Input: "Summarize the latest issue in GitHub's OSPO repo"
{{"action": "summarize_latest_issue", "repo": "github/github-ospo", "title": null, "body": null, "issue_number": null}}

Input: "Create a repo called test-ai-bot"
{{"action": "create_repo", "repo": null, "title": null, "body": null, "issue_number": null, "repo_name": "test-ai-bot"}}

Input: "I want to file a bug in next.js"
{{"action": "create_issue", "repo": "vercel/next.js", "title": "Bug report", "body": null, "issue_number": null}}

Now extract the intent from: "{user_input}"
'''.strip()

    try:
        response = client.complete(
            model=model_name,
            temperature=0.2,
            max_tokens=300,
            messages=[
                SystemMessage("You extract structured commands from natural GitHub-related messages."),
                UserMessage(prompt)
            ]
        )
        raw = response.choices[0].message.content.strip()
        print("[parse_command_naturally] Raw output:", raw)

        if raw.startswith("```"):
            raw = raw.strip("`").strip()
            if raw.startswith("json"):
                raw = raw[len("json"):].strip()

        parsed = json.loads(raw)

        # Guess repo if needed
        if parsed.get("action") in ["summarize_repo", "summarize_latest_issue", "create_issue"] and not parsed.get("repo"):
            guess = github_search_repo(user_input)
            if guess:
                parsed["repo"] = guess
                print("[parse_command_naturally] Guessed repo:", guess)

        return parsed
    except Exception as e:
        print("[parse_command_naturally] Parsing failed:", e)
        return {"action": "unknown", "repo": None, "title": None, "body": None, "issue_number": None}

def route_natural_command(user_text: str):
    intent = parse_command_naturally(user_text)
    print("[route_natural_command] Parsed intent:", intent)
    action = intent.get("action")
    repo = intent.get("repo")

    if action == "summarize_repo" and repo:
        return summarize_any_repo(repo)
    if action == "summarize_latest_issue" and repo:
        return summarize_latest_issue(repo)
    if action == "create_repo" and intent.get("repo_name"):
        return "Created repo." if create_repo(intent["repo_name"]) else "Failed to create repo."
    if action == "create_issue" and repo:
        title = intent.get("title") or "Issue"
        body = intent.get("body") or ""
        return "Issue created." if create_issue(repo.split("/")[-1], title, body) else "Failed to create issue."

    return None
