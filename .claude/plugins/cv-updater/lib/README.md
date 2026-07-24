# CV Updater Library Resources

**Shared resources for cv-updater plugin skills.**

This directory contains shared resources used by the cv-updater-init and cv-updater-update skills:

## Contents

- `cv-updater-git.py` — Python script for git operations (get commits, check hooks, etc.)
- `subagents/` — Subagent instruction files for init and update workflows
- `post-merge.hook` — Git hook template for notifications
- `config-template.json` — Configuration structure template
- `findings-schema.md` — Schema for findings JSONL output
- `baseline-findings.md` — TDD baseline for testing
- `test-scenarios.md` — Test scenarios for validation
- `test-artifacts/` — Sample artifacts for testing

## Global Knowledge Base

All cv-updater state is stored in the CV repo, not in work repos:

**Location:** `~/dev/CV/update-cv-db/`

**Structure:**
```
~/dev/CV/update-cv-db/
├── config/
│   ├── project1.json          # Per-project blacklist config
│   └── project2.json
├── findings/
│   ├── project1-findings.jsonl  # Per-project analysis results
│   └── project2-findings.jsonl
└── hooks/
    └── project1-post-merge.backup  # Hook backups
```

## Multi-Project Support

- One global knowledge base shared across all projects
- Per-project config and findings (separate files)
- Project name auto-detected from repo path
- Override with `--project-name` if needed

## Usage

These resources are referenced by the plugin skills:

- `/cv-updater-init` — First-time setup (uses `cv-updater-git.py`, `subagents/init-blacklist.md`)
- `/cv-updater-update` — Regular CV updates (uses `cv-updater-git.py`, `subagents/update-cv.md`)

## Development

### Test Script

```bash
# Get your email
uv run cv-updater-git.py get-user-email --cwd /path/to/repo

# Get commits
uv run cv-updater-git.py get-commits --author-email "you@email.com" --since 2024-01-01 --cwd /path/to/repo

# Sample for blacklist
uv run cv-updater-git.py sample-commits --rate 10 --cwd /path/to/repo
```

### Run Tests (RED-GREEN-REFACTOR)

See `test-scenarios.md` and `baseline-findings.md` for TDD workflow.
