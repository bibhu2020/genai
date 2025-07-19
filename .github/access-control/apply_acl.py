import os
import yaml
import requests

def main():
    # Load ACL YAML
    with open(".github/access-control/acl.yaml", "r") as f:
        acl = yaml.safe_load(f)

    repo_owner, repo_name = os.getenv("GITHUB_REPOSITORY").split("/")
    token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    for entry in acl.get("configuration", {}).get("manageAccess", []):
        username = entry["member"]
        role = entry["role"].lower()
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/collaborators/{username}"
        payload = {"permission": role}

        response = requests.put(url, headers=headers, json=payload)
        if response.status_code in [201, 204]:
            print(f"Set {username} permission to {role} successfully.")
        else:
            print(f"Failed to set {username}: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()
