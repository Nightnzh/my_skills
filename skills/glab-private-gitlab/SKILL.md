---
name: glab-private-gitlab
description: Use when connecting to or working with a self-hosted/private GitLab instance using glab CLI — authentication setup, SSH key config, SSL certificate issues, MR review with inline comments, pipeline/CI operations
---

# Glab Private GitLab

## Overview

Use `glab` (GitLab CLI) to connect and operate a self-hosted or private GitLab instance. Covers authentication, SSH setup, MR review with comments, CI/pipeline inspection, and inline code review via REST API.

Replace `<GITLAB_HOST>` throughout this guide with your actual GitLab hostname or IP (e.g. `gitlab.example.com` or `192.168.1.10`).

---

## Authentication

### Option 1: Personal Access Token (recommended)

```bash
# Login to private GitLab (add --skip-tls-verify for self-signed certs)
glab auth login --hostname <GITLAB_HOST> --token <PAT> --skip-tls-verify

# Confirm auth status
glab auth status --hostname <GITLAB_HOST>
```

Get a PAT from GitLab UI: **User Settings → Access Tokens → check api, read_repository, write_repository**

### Option 2: Environment Variables

```bash
export GITLAB_HOST=<GITLAB_HOST>
export GITLAB_TOKEN=<personal_access_token>
```

### Config File Location

```
~/.config/glab-cli/config.yml
```

Manual edit example:
```yaml
hosts:
  <GITLAB_HOST>:
    token: <PAT>
    api_protocol: https    # use http if your instance is HTTP-only
    git_protocol: ssh
    skip_tls_verify: true  # only needed for self-signed certificates
```

---

## SSH Key Setup

```bash
# 1. Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. Configure ~/.ssh/config
```

```
Host <GITLAB_HOST>
  HostName <GITLAB_HOST>
  User git
  IdentityFile ~/.ssh/id_ed25519
  StrictHostKeyChecking no
  # Port 2222   # uncomment if your GitLab uses a non-standard SSH port
```

```bash
# 3. Upload public key to GitLab
glab ssh-key add ~/.ssh/id_ed25519.pub --title "my-machine" --hostname <GITLAB_HOST>

# 4. Verify SSH connection
ssh -T git@<GITLAB_HOST>
# Success: Welcome to GitLab, @username!
```

---

## Review MR and Leave Comments

```bash
# View MR details (with diff)
glab mr view <MR_ID> --repo <GITLAB_HOST>/<group>/<repo>

# List all comments on an MR
glab mr note list <MR_ID> --repo <GITLAB_HOST>/<group>/<repo>

# Add a general comment
glab mr note <MR_ID> --message "LGTM! Please also fix XXX" \
  --repo <GITLAB_HOST>/<group>/<repo>

# Approve MR
glab mr approve <MR_ID> --repo <GITLAB_HOST>/<group>/<repo>

# Revoke approval
glab mr revoke <MR_ID> --repo <GITLAB_HOST>/<group>/<repo>

# Merge MR (requires Maintainer role)
glab mr merge <MR_ID> --repo <GITLAB_HOST>/<group>/<repo>
```

> **Note:** `glab` does not support inline (per-line) code review natively. Use the **GitLab REST API** directly for that.

### Inline Comment (per-line) — via REST API

GitLab uses the **Discussions API** to create positioned inline comments. You need commit SHAs and the file line number.

**Step 1: Get the MR diff refs (base/head SHA)**

```bash
GITLAB="https://<GITLAB_HOST>"
TOKEN="<PAT>"
PROJECT_ID="<group>%2F<repo>"   # URL-encode the slash as %2F
MR_IID=<MR_ID>

curl -sk --header "PRIVATE-TOKEN: $TOKEN" \
  "$GITLAB/api/v4/projects/$PROJECT_ID/merge_requests/$MR_IID" \
  | python3 -c "import sys,json; d=json.load(sys.stdin)['diff_refs']; print(d)"
# Returns base_sha, start_sha, head_sha
```

**Step 2: Create inline comment**

```bash
curl -sk --request POST \
  --header "PRIVATE-TOKEN: $TOKEN" \
  --header "Content-Type: application/json" \
  "$GITLAB/api/v4/projects/$PROJECT_ID/merge_requests/$MR_IID/discussions" \
  --data '{
    "body": "This looks wrong, please fix",
    "position": {
      "base_sha":  "<base_sha>",
      "start_sha": "<start_sha>",
      "head_sha":  "<head_sha>",
      "position_type": "text",
      "new_path": "path/to/file.go",
      "new_line": 42
    }
  }'
```

**Parameter reference:**

| Parameter | Description |
|-----------|-------------|
| `new_path` | File path relative to repo root |
| `new_line` | Line number in the new version |
| `old_path` / `old_line` | Line number in the old version (for deleted lines) |
| `position_type` | Always `"text"` |

> The `-k` flag in `curl -sk` skips SSL verification — use only for self-signed cert environments.

---

## Quick Reference

| Action | Command |
|--------|---------|
| List MRs | `glab mr list` |
| Create MR | `glab mr create` |
| View MR details | `glab mr view <ID>` |
| Comment on MR | `glab mr note <ID> --message "…"` |
| Approve MR | `glab mr approve <ID>` |
| Merge MR | `glab mr merge <ID>` |
| List pipelines | `glab pipeline list` |
| Pipeline status | `glab pipeline status` |
| Trigger pipeline | `glab pipeline run` |
| List issues | `glab issue list` |
| Create issue | `glab issue create` |
| Clone repo | `glab repo clone <group>/<repo>` |
| Upload SSH key | `glab ssh-key add <pub_key_path> --title "name"` |

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `x509: certificate signed by unknown authority` | Self-signed cert | Add `--skip-tls-verify` or set `skip_tls_verify: true` in config |
| `401 Unauthorized` | Invalid or expired token | Regenerate PAT, ensure scope includes `api` |
| `ssh: connect to host ... port 22: Connection refused` | Non-standard SSH port | Check GitLab SSH port, update `Port` in `~/.ssh/config` |
| `fatal: repository not found` | Wrong path or no permission | Verify group/repo name, confirm account has Developer or higher role |
| `glab: command not found` | Not installed | `brew install glab` or see official install docs |
