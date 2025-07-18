# commands.py

import os
import requests

def get_headers():
    # Only read-only access with no authentication token
    return {
        "Accept": "application/vnd.github+json"
    }

def get_authenticated_username():
    user_url = "https://api.github.com/user"
    user_res = requests.get(user_url, headers=get_headers())
    if not user_res.ok:
        return None
    return user_res.json().get("login")
