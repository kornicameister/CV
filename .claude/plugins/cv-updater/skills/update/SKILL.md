---
name: cv-updater-update
description: Analyze recent git commits for CV updates. Filters by blacklist, infers achievements, anonymizes client/project names, outputs YAML ready for data/experience/*.yml. Use after completing work to update CV from commit history.
---

# CV Updater: Update CV from Commits

Analyzes recent git commits, infers CV-worthy achievements, outputs anonymized YAML.

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

- After completing significant work on a project
- When git hook notifies about new commits
- Quarterly CV update routine
- Before job applications / promotions

## What It Does

1. Loads blacklist from `~/dev/CV/update-cv-db/config/{project-name}.json`
2. Gets commits since last run (by your git email)
3. Filters blacklisted commits (privacy > CV completeness)
4. Analyzes remaining commits for high/medium value achievements
5. Groups related commits into single achievements
6. Anonymizes client/project names consistently
7. Outputs YAML matching `data/experience/*.yml` structure
8. Writes findings to `~/dev/CV/update-cv-db/findings/{project-name}-findings.jsonl`
9. Updates `last_run` date in config

## Prerequisites

- Config exists: `~/dev/CV/update-cv-db/config/{project-name}.json`
- If NOT: run `/cv-updater-init` first

## Workflow

**Delegate to subagent** (preserves main context):

```javascript
Agent({
  description: "Analyze commits for CV updates",
  prompt: `You are updating CV from recent git commit history.

**User Input Required:**
- Ask user for branch name to analyze (default: main)
- For repos without local main/master: use origin/main or current branch

**Steps:**

1. Load config from \`~/dev/CV/update-cv-db/config/{project-name}.json\`:
   - blacklist: terms to filter
   - author_email: whose commits to analyze
   - last_run: start date for analysis
   - anonymization_map: client name → replacement
   - project_name: auto-detected from repo path
   - branch: branch to analyze (from user or config default)

2. Get commits since last run:
   \`\`\`bash
   uv run ../../lib/cv-updater-git.py get-commits \\
     --author-email "you@email.com" \\
     --since "2024-07-01" \\
     --branch <user-specified-branch> \\
     --cwd /path/to/work/repo \\
     --project-name cguse-skills
   \`\`\`

3. Filter blacklisted commits:
   - Check if message OR file paths contain blacklisted terms
   - Case-insensitive, partial match
   - Log skipped commits to ~/dev/CV/update-cv-db/findings/{project-name}-findings.jsonl

4. Analyze remaining for CV value:
   - **High-value:** new features, perf improvements, architecture
   - **Medium-value:** significant bug fixes, non-trivial refactors
   - **Low-value (skip):** typos, formatting, trivial config

5. Group related commits:
   - Multiple commits on same feature → one achievement
   - Example: 5 GraphQL commits → "Built GraphQL API"

6. Anonymize using anonymization_map:
   - Acme Corp → Enterprise client
   - Project Phoenix → Internal platform
   - Preserve: tech skills, frameworks, metrics

7. Output YAML matching \`data/experience/*.yml\`:
   \`\`\`yaml
   - project: Enterprise Client Platform
     entries:
       - Migrated ETL to AWS Glue, reducing time by 60%
       - Implemented data quality checks with Great Expectations
   \`\`\`

8. Update config in \`~/dev/CV/update-cv-db/config/{project-name}.json\`: \`last_run = today\`

**Read the full subagent instructions from:**
\`../../lib/subagents/update-cv.md\`

**Important:**
- NEVER skip blacklist filtering (privacy > CV value)
- ALWAYS anonymize at source (not "fix it later")
- Group related commits for better CV bullets
- Only high/medium value → achievements`,
  model: "sonnet",
  run_in_background: false
})
```

## Success Criteria

- All blacklisted commits skipped (logged)
- Only high/medium value commits → achievements
- Client/project names anonymized consistently
- YAML matches `data/experience/*.yml` structure
- Findings written to `~/dev/CV/update-cv-db/findings/{project-name}-findings.jsonl`
- Config updated with `last_run` date in `~/dev/CV/update-cv-db/config/{project-name}.json`
- Skipped commits logged for transparency

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

## Common Issues

### "Config not found"
→ Run `/cv-updater-init` first to create `~/dev/CV/update-cv-db/config/{project-name}.json`

### "No new commits"
→ Check `last_run` date in config, verify repo path

### "Too many blacklist matches"
→ Review blacklist in `~/dev/CV/update-cv-db/config/{project-name}.json`, remove false positives

### "Achievements too generic"
→ Check commit messages have enough context

### "Wrong project name detected"
→ Override with `--project-name` flag in cv-updater-git.py commands

### "Branch main does not exist"
→ Use `--branch origin/main` for repos without local main branch (worktrees, feature branches)
→ Or specify current branch: `--branch $(git rev-parse --abbrev-ref HEAD)`

## Files

- **Subagent:** `../../lib/subagents/update-cv.md`
- **Python script:** `../../lib/cv-updater-git.py`
- **Config (read):** `~/dev/CV/update-cv-db/config/{project-name}.json`
- **Findings (written):** `~/dev/CV/update-cv-db/findings/{project-name}-findings.jsonl`
