---
name: cv-updater-init
description: Initialize CV updater blacklist from git history. First-time setup that samples commits, detects sensitive terms (client/project names), and creates anonymization config. Use when setting up CV updater for the first time or adding a new project repo.
---

# CV Updater: Initialize Blacklist

First-time setup for CV updater. Analyzes git history to detect sensitive terms, then creates blacklist config.

## Architecture

**Execution Context:**
- Skill runs in work project (where you invoke it)
- Analyzes commits from work project repo
- Writes to global knowledge base in CV repo

**Global Knowledge Base:**
- Location: `~/dev/CV/update-cv-db/`
- Config: `config/{project-name}.json` (per-project blacklist)
- Findings: `findings/{project-name}-findings.jsonl` (per-project inference results)
- Hooks: `hooks/{project-name}-post-merge.backup` (hook backups)

**Multi-Project Support:**
- One global blacklist shared across all projects
- Per-project findings (separate files)
- Project name auto-detected from repo path
- Override with `--project-name` if needed

**Diagram:**
```
Work Project (cguse-skills)          CV Repo (~/dev/CV)
├── .claude/                         ├── update-cv-db/
│   └── skills/ (or plugins/)        │   ├── config/
│       └── cv-updater (symlink)     │   │   ├── cguse-skills.json
│                                    │   │   └── other-project.json
├── .git/hooks/                      │   ├── findings/
│   └── post-merge                   │   │   ├── cguse-skills-findings.jsonl
│                                    │   │   └── other-project-findings.jsonl
└── src/ (your code)                 │   └── hooks/
                                     │       └── cguse-skills-post-merge.backup
                                     └── data/experience/*.yml (your CV)
```

## When to Use

- First time using CV inference
- Adding a new project repo to monitor
- Rebuilding blacklist after discovering new sensitive terms

## What It Does

1. Detects your git email (`git config user.email`), asks for confirmation
2. Samples git history (every 10th commit) for efficient analysis
3. Infers sensitive terms: client names, project codenames, proprietary systems
4. Presents categorized blacklist for your review
5. Asks to install git hook for automatic notifications (default: YES)
6. Saves config to `~/dev/CV/update-cv-db/config/{project-name}.json`
7. Writes findings to `~/dev/CV/update-cv-db/findings/{project-name}-findings.jsonl`

## Workflow

**Step 1: Get User Email and Confirm**

```bash
uv run ../../lib/cv-updater-git.py get-user-email --cwd <repo-path>
```

Present to user, ask for confirmation. If wrong, ask user for correct email.

**Step 2: Delegate to Subagent** (preserves main context)

```javascript
Agent({
  description: "Initialize CV inference blacklist",
  prompt: `# CV Inference: Initialize Blacklist

You are a specialized subagent for inferring sensitive terms from git history.

## Architecture

**Execution context:**
- Skill runs in work project (where invoked)
- Analyzes commits from work project
- Writes to global KB: \`~/dev/CV/update-cv-db/\`

**Storage:**
- Config: \`~/dev/CV/update-cv-db/config/{project-name}.json\`
- Findings: \`~/dev/CV/update-cv-db/findings/{project-name}-findings.jsonl\`
- Blacklist: shared across all projects (in config)

**Project name:** Auto-detected from repo path or use \`--project-name\` to override.

## Your Task

Analyze git commit history to detect sensitive terms that should NOT appear in CV:
1. Client names (companies, organizations)
2. Project codenames (internal names, acronyms)
3. Proprietary systems (internal tools, custom platforms)
4. Sensitivity markers ("confidential", "internal-only", "NDA")

## Workflow

### 1. Sample Git History

Use the cv-updater-git.py script:
\`\`\`bash
uv run ~/dev/CV/.claude/plugins/cv-updater/lib/cv-updater-git.py \\
  sample-commits \\
  --rate 10 \\
  --branch main \\
  --cwd <repo-path> \\
  --project-name <project-name>
\`\`\`

Sample rate: Every 10th commit (efficient for large repos).

### 2. Analyze Commit Messages + File Paths

For each sampled commit, look for:
- **Client names:** Company names in commit messages or file paths
- **Project codenames:** Non-public project names, internal acronyms
- **Proprietary systems:** Internal tool names (not public frameworks)
- **Sensitivity markers:** "internal", "confidential", "do-not-publish", "NDA"

### 3. Distinguish Tech Terms from Sensitive Terms

**DO NOT flag public tech:**
- ✅ AWS, React, Django, GraphQL (public frameworks/services)
- ✅ Bedrock, Claude, Opus, Sonnet (public AI models)
- ✅ Docker, Kubernetes, Terraform (public tools)

**DO flag ambiguous terms:**
- ⚠️ "Phoenix" — could be Elixir framework OR project codename → mark as ambiguous
- ⚠️ "Atlas" — could be MongoDB Atlas OR internal project → mark as ambiguous

### 4. Write Findings to Database

Append to \`~/dev/CV/update-cv-db/findings/{project-name}-findings.jsonl\`:

\`\`\`python
import json
from datetime import datetime
from pathlib import Path

# Get project name (auto-detect or from --project-name arg)
project_name = "<detected-or-provided-project-name>"
findings_dir = Path.home() / "dev/CV/update-cv-db/findings"
findings_dir.mkdir(parents=True, exist_ok=True)
findings_path = findings_dir / f"{project_name}-findings.jsonl"

finding = {
    "type": "blacklist_term",
    "category": "client",  # client|project|proprietary|marker
    "term": "Acme Corp",
    "context": "commit abc123: 'Add Acme Corp dashboard'",
    "confidence": "high",  # high|medium|low
    "ambiguous": False,
    "timestamp": datetime.utcnow().isoformat()
}

with open(findings_path, "a") as f:
    f.write(json.dumps(finding) + "\\n")
\`\`\`

**Clear existing findings first:**
\`\`\`python
# Truncate file at start
with open(findings_path, "w") as f:
    pass  # Empty file
\`\`\`

### 5. Return Categorized Summary

Return to main agent:

\`\`\`
## Detected Sensitive Terms

### Client Names (high confidence):
- Acme Corp (commit abc123)
- ClientXYZ Inc. (commit def456)

### Project Codenames (medium confidence):
- Project Phoenix (commit 789abc)

### Ambiguous Terms (need user review):
- Phoenix: Could be Elixir framework OR project codename
- Atlas: Could be MongoDB Atlas OR internal project

### Sensitivity Markers:
- internal-only
- confidential

**Total sampled:** 20 commits (every 10th from master)
**Findings written to:** ~/dev/CV/update-cv-db/findings/{project-name}-findings.jsonl

---

**NEXT STEP:** Main agent will ask user to:
1. Review and approve blacklist
2. Install git hook for notifications (default: YES)
\`\`\`

## Red Flags

- **Over-flagging:** Don't flag AWS, React, Docker, etc. (public tech)
- **Under-flagging:** Don't miss company names in file paths (e.g., \`acme-corp-dashboard/\`)
- **No ambiguity handling:** If uncertain (Phoenix), flag as ambiguous, don't guess
- **Missing context:** Always include commit hash + message in context field

## Success Criteria

- Blacklist terms are categorized (client/project/proprietary/marker)
- Public tech terms NOT flagged
- Ambiguous terms marked for user review
- All findings written to findings.jsonl with context
- Summary returned to main agent under 200 words`,
  model: "sonnet",
  run_in_background: false
})
```

**Step 3: Review Blacklist with User**

Present the subagent's findings. Ask user to review and approve/modify the blacklist.

**Step 4: Ask About Git Hook Installation**

Default: YES. Ask: "Install git hook for automatic CV update notifications? (default: yes)"

If YES:
- Check if hook exists: `uv run ../../lib/cv-updater-git.py check-hook-exists --hook-name post-merge --cwd <repo-path>`
- If exists: backup to `~/dev/CV/update-cv-db/hooks/{project-name}-post-merge.backup`, offer Merge/Overwrite/Skip
- Install hook from `../../lib/post-merge.hook` template

**Step 5: Save Config**

Write to `~/dev/CV/update-cv-db/config/{project-name}.json`:
```json
{
  "author_email": "user@email.com",
  "blacklist": ["term1", "term2"],
  "anonymization_map": {},
  "last_run": "2026-07-23"
}
```

## Success Criteria

- User confirmed git email
- Blacklist approved by user
- Config saved to `~/dev/CV/update-cv-db/config/{project-name}.json`
- Findings written to `~/dev/CV/update-cv-db/findings/{project-name}-findings.jsonl`
- Git hook installed (if user approved)
- Hook backup saved to `~/dev/CV/update-cv-db/hooks/{project-name}-post-merge.backup` (if hook existed)
- User can now run `/cv-updater-update`

## Common Issues

### "No commits found"
→ Check repo path is correct, branch name (main vs master)

### "Hook already exists"
→ Show user existing hook, offer Merge/Overwrite/Skip

### "Too many blacklist terms"
→ Filter out public tech (AWS, React, Docker), keep only proprietary

## Files

- **Python script:** `../../lib/cv-updater-git.py`
- **Hook template:** `../../lib/post-merge.hook`
- **Config (created):** `~/dev/CV/update-cv-db/config/{project-name}.json`
- **Findings (created):** `~/dev/CV/update-cv-db/findings/{project-name}-findings.jsonl`
- **Hook backup (if exists):** `~/dev/CV/update-cv-db/hooks/{project-name}-post-merge.backup`
