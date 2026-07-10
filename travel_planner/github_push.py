"""
github_push.py
==============
Pushes all travel_planner project files to GitHub via the REST API.
No Git installation required.

Usage:
    python github_push.py <YOUR_GITHUB_PAT>

How to get a PAT:
    GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic)
    Scopes needed: repo (full control of private repositories)
"""

import sys
import os
import base64
import json
import urllib.request
import urllib.error

# ── Configuration ─────────────────────────────────────────────────────────────
GITHUB_API   = "https://api.github.com"
REPO_OWNER   = "Jahnavilanke01"
REPO_NAME    = "ibm"
BRANCH       = "main"
COMMIT_MSG   = "Add AI Travel Planner — Flask + IBM watsonx.ai Granite LLM"

# Files to push  (source path relative to this script, → GitHub path)
HERE = os.path.dirname(os.path.abspath(__file__))

FILES = [
    ("app.py",                    "travel_planner/app.py"),
    ("run.py",                    "travel_planner/run.py"),
    ("requirements.txt",          "travel_planner/requirements.txt"),
    ("README.md",                 "travel_planner/README.md"),
    (".env.example",              "travel_planner/.env.example"),
    ("github_push.py",            "travel_planner/github_push.py"),
    ("templates/index.html",      "travel_planner/templates/index.html"),
    ("static/css/style.css",      "travel_planner/static/css/style.css"),
    ("static/js/app.js",          "travel_planner/static/js/app.js"),
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def api_request(token: str, method: str, path: str, body: dict = None):
    url = f"{GITHUB_API}{path}"
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization",  f"token {token}")
    req.add_header("Accept",         "application/vnd.github+json")
    req.add_header("Content-Type",   "application/json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent",     "travel-planner-pusher/1.0")
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            try:
                return resp.status, json.loads(raw) if raw else {}
            except Exception:
                return resp.status, {}
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw) if raw else {}
        except Exception:
            return e.code, {}


def get_file_sha(token: str, github_path: str):
    """Return the SHA of an existing file (needed for updates), or None."""
    status, data = api_request(token, "GET",
        f"/repos/{REPO_OWNER}/{REPO_NAME}/contents/{github_path}?ref={BRANCH}")
    if status == 200:
        return data.get("sha")
    return None


def ensure_repo_exists(token: str):
    """Create the repo if it doesn't already exist."""
    status, data = api_request(token, "GET",
        f"/repos/{REPO_OWNER}/{REPO_NAME}")
    if status == 200:
        print(f"  Repository {REPO_OWNER}/{REPO_NAME} already exists.")
        return True
    # Try to create it
    status, data = api_request(token, "POST", "/user/repos", {
        "name":        REPO_NAME,
        "description": "AI Travel Planner — Flask + IBM watsonx.ai Granite LLM",
        "private":     False,
        "auto_init":   True,
    })
    if status in (200, 201):
        print(f"  Created repository {REPO_OWNER}/{REPO_NAME}.")
        return True
    print(f"  ERROR creating repo: {data.get('message')}")
    return False


def push_file(token: str, local_path: str, github_path: str):
    full_path = os.path.join(HERE, local_path)
    if not os.path.exists(full_path):
        print(f"  SKIP  {local_path}  (file not found locally)")
        return False

    with open(full_path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode()

    sha = get_file_sha(token, github_path)

    body = {
        "message": COMMIT_MSG,
        "content": content_b64,
        "branch":  BRANCH,
    }
    if sha:
        body["sha"] = sha   # required for updates

    status, data = api_request(token, "PUT",
        f"/repos/{REPO_OWNER}/{REPO_NAME}/contents/{github_path}", body)

    if status in (200, 201):
        action = "Updated" if sha else "Created"
        print(f"  OK    [{action}] {github_path}")
        return True
    else:
        print(f"  FAIL  {github_path}  ({status}) {data.get('message','')}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nERROR: Please provide your GitHub PAT as an argument.")
        print("  python github_push.py ghp_xxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)

    token = sys.argv[1].strip()

    # Quick auth check
    status, user = api_request(token, "GET", "/user")
    if status != 200:
        print(f"ERROR: Authentication failed ({status}). Check your PAT.")
        sys.exit(1)
    print(f"\nAuthenticated as: {user.get('login')} ({user.get('name','–')})")

    # Ensure repo exists
    print(f"\nChecking repository {REPO_OWNER}/{REPO_NAME} ...")
    if not ensure_repo_exists(token):
        sys.exit(1)

    # Push all files
    print(f"\nPushing {len(FILES)} files to branch '{BRANCH}' ...")
    ok = fail = 0
    for local, remote in FILES:
        if push_file(token, local, remote):
            ok += 1
        else:
            fail += 1

    # Summary
    print(f"\n{'='*55}")
    print(f"  Done!  {ok} files pushed,  {fail} failed.")
    print(f"  Repository: https://github.com/{REPO_OWNER}/{REPO_NAME}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
