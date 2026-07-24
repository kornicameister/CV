# CV Updater Plugin

**Automatically infer CV updates from git commit history with privacy-first anonymization.**

## Overview

The CV Updater plugin analyzes git commits from your work projects and generates CV-ready YAML entries with automatic anonymization of sensitive client/project names.

## Skills

### `/cv-updater-init`
First-time setup for a new project. Analyzes git history, detects sensitive terms (client names, project codenames), presents categorized blacklist for approval, and optionally installs git hook for notifications.

**Use when:**
- Setting up CV updater for the first time
- Adding a new project repo to monitor
- Rebuilding blacklist after discovering new sensitive terms

### `/cv-updater-update`
Analyzes recent git commits, filters by blacklist, infers CV-worthy achievements, anonymizes sensitive names, and outputs YAML ready for `data/experience/*.yml`.

**Use when:**
- After completing significant work on a project
- When git hook notifies about new commits
- During quarterly CV update routine
- Before job applications or promotions

## Architecture

**Global Knowledge Base:** All state stored in CV repo (`~/dev/CV/update-cv-db/`), not in work repos.

**Multi-Project Support:**
- One global knowledge base
- Per-project config and findings
- Project name auto-detected from repo path

**Execution Flow:**
```
Work Project (cguse-skills)          CV Repo (~/dev/CV)
├── .claude/                         ├── update-cv-db/
│   └── plugins/                     │   ├── config/
│       └── cv-updater (symlink)     │   │   ├── cguse-skills.json
│                                    │   │   └── other-project.json
├── .git/hooks/                      │   ├── findings/
│   └── post-merge                   │   │   ├── cguse-skills-findings.jsonl
│                                    │   │   └── other-project-findings.jsonl
└── src/ (your code)                 │   └── hooks/
                                     │       └── cguse-skills-post-merge.backup
                                     └── data/experience/*.yml (your CV)
```

## Installation

### From Local Marketplace (Recommended)

1. Add marketplace:
   ```bash
   claude plugin marketplace add localhost ~/dev/CV/.claude-plugin
   ```

2. Install plugin:
   ```bash
   /plugin install cv-updater@localhost
   ```

### Manual Symlink

Alternatively, create symlink directly:
```bash
ln -s ~/dev/CV/.claude/plugins/cv-updater ~/.claude/plugins/cv-updater
```

## Quick Start

### 1. Initialize (First Time)

In your work project:
```bash
/cv-updater-init
```

This will:
1. Detect your git email (asks for confirmation)
2. Sample git history to detect sensitive terms
3. Present categorized blacklist for approval
4. Ask to install git hook (default: YES)
5. Save config to `~/dev/CV/update-cv-db/config/{project-name}.json`
6. Write findings to `~/dev/CV/update-cv-db/findings/{project-name}-findings.jsonl`

### 2. Update CV from Recent Work

After working on a project:
```bash
/cv-updater-update
```

This will:
1. Load blacklist from `~/dev/CV/update-cv-db/config/{project-name}.json`
2. Get commits since last run (by your git email)
3. Filter blacklisted commits (privacy > CV completeness)
4. Infer high/medium value achievements
5. Group related commits into single achievements
6. Anonymize client/project names consistently
7. Output YAML matching `data/experience/*.yml` structure
8. Update config with `last_run` date

### 3. Git Hook Notifications

If you approved hook installation during init, every `git pull origin main` shows:
```
✨ CV Updater Notification
Found 5 new commits by you@email.com on main
Consider running: /cv-updater-update
```

## Output Example

```yaml
# CV Updates from 12 commits since 2024-07-01
# Project: cguse-skills

- project: Enterprise Client Data Platform
  entries:
    - Migrated legacy ETL to AWS Glue, reducing processing time by 60%
    - Implemented data quality checks using Great Expectations
    - Set up monitoring with CloudWatch metrics and alarms

---
Skipped 2 commits due to blacklist:
- abc123: "Update internal-only config" (matched: internal-only)
- def456: "Fix client-secret integration" (matched: client-secret-name)

Findings written to: ~/dev/CV/update-cv-db/findings/cguse-skills-findings.jsonl
Config updated: ~/dev/CV/update-cv-db/config/cguse-skills.json (last_run = 2024-07-23)
```

## Design Principles

1. **Privacy first:** Blacklist enforcement is non-negotiable. No exceptions for "valuable" commits.
2. **Author email, not name:** `git config user.email` is unique and reliable.
3. **Subagent architecture:** Heavy analysis delegated to subagents to preserve main context.
4. **Global knowledge base:** All findings written to CV repo, not work repos.
5. **User confirmation:** Init requires approval before saving blacklist.

## Plugin Structure

```
cv-updater/
├── plugin.json          # Plugin manifest
├── README.md            # This file
├── skills/
│   ├── init/           # /cv-updater-init skill
│   │   └── SKILL.md
│   └── update/         # /cv-updater-update skill
│       └── SKILL.md
├── lib/                # Shared resources (NOT skills)
│   ├── cv-updater-git.py
│   ├── subagents/
│   │   ├── init-blacklist.md
│   │   └── update-cv.md
│   ├── post-merge.hook
│   ├── config-template.json
│   ├── findings-schema.md
│   └── README.md
└── .gitignore
```

## Troubleshooting

### "Config not found"
→ Run `/cv-updater-init` first to create `~/dev/CV/update-cv-db/config/{project-name}.json`

### "No commits found"
→ Check repo path is correct, branch name (main vs master)

### "Hook already exists"
→ Show user existing hook, offer Merge/Overwrite/Skip

### "Too many blacklist terms"
→ Filter out public tech (AWS, React, Docker), keep only proprietary

### "Too many blacklist matches"
→ Review blacklist in `~/dev/CV/update-cv-db/config/{project-name}.json`, remove false positives

### "Achievements too generic"
→ Check commit messages have enough context

### "Wrong project name detected"
→ Override with `--project-name` flag in cv-updater-git.py commands

## Requirements

- Python >=3.10
- uv (for running Python scripts)
- Git (configured with user.email)

## Version

1.0.0
