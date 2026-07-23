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

**Delegate to subagent** (preserves main context):

```javascript
Agent({
  description: "Initialize CV inference blacklist",
  prompt: `You are setting up CV inference for the first time.

**Steps:**

1. Get git user email:
   \`\`\`bash
   uv run ../../lib/cv-updater-git.py get-user-email --cwd /path/to/work/repo
   \`\`\`
   Present to user: "Detected email: X. Is this correct?"

2. Sample git history:
   \`\`\`bash
   uv run ../../lib/cv-updater-git.py sample-commits --rate 10 --branch main --cwd /path/to/work/repo --project-name cguse-skills
   \`\`\`

3. Analyze sampled commits for sensitive terms:
   - Client names (companies, organizations)
   - Project codenames (internal names, acronyms)  
   - Proprietary systems (internal tools)
   - Sensitivity markers (confidential, internal-only, NDA)

4. Write findings to \`~/dev/CV/update-cv-db/findings/{project-name}-findings.jsonl\`:
   \`\`\`jsonl
   {"type":"blacklist_term","category":"client","term":"Acme Corp","context":"commit abc123","confidence":"high","project":"cguse-skills"}
   \`\`\`

5. Return categorized summary for user approval:
   - Client Names (high confidence)
   - Project Codenames (medium confidence)
   - Ambiguous Terms (needs review)
   - Sensitivity Markers

6. Ask about git hook installation (default: YES):
   - Check if hook exists: \`uv run ../../lib/cv-updater-git.py check-hook-exists /path/to/repo\`
   - If exists: show preview, ask Merge/Overwrite/Skip
   - If not exists: copy hook, make executable

7. Save config to \`~/dev/CV/update-cv-db/config/{project-name}.json\`:
   \`\`\`json
   {
     "project_name": "cguse-skills",
     "blacklist": ["term1", "term2"],
     "author_email": "you@email.com",
     "since_date": "2024-01-01",
     "repo_path": "/path/to/work/repo"
   }
   \`\`\`

**Read the full subagent instructions from:**
\`../../lib/subagents/init-blacklist.md\`

**Important:**
- ALWAYS check for existing hooks before installing
- NEVER overwrite hooks without user permission
- Present categorized blacklist for user approval
- Flag ambiguous terms (Phoenix = framework or codename?)`,
  model: "sonnet",
  run_in_background: false
})
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

- **Subagent:** `../../lib/subagents/init-blacklist.md`
- **Python script:** `../../lib/cv-updater-git.py`
- **Hook template:** `../../lib/post-merge.hook`
- **Config (created):** `~/dev/CV/update-cv-db/config/{project-name}.json`
- **Findings (created):** `~/dev/CV/update-cv-db/findings/{project-name}-findings.jsonl`
- **Hook backup (if exists):** `~/dev/CV/update-cv-db/hooks/{project-name}-post-merge.backup`
