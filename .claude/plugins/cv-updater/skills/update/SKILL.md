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

**Step 1: Ask User for Branch**

Ask user for branch name to analyze (default: main). For repos without local main/master, suggest origin/main or current branch.

**Step 2: Delegate to Subagent** (preserves main context)

```javascript
Agent({
  description: "Analyze commits for CV updates",
  prompt: `# CV Inference: Update CV from Commits

You are a specialized subagent for analyzing commits and inferring CV achievements.

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

Analyze git commits since last run, filter blacklist, infer CV-worthy achievements, anonymize, output YAML.

## Workflow

### 1. Load Config

Read \`~/dev/CV/update-cv-db/config/{project-name}.json\`:
\`\`\`python
import json
from pathlib import Path

project_name = "<detected-or-provided-project-name>"
config_path = Path.home() / "dev/CV/update-cv-db/config" / f"{project_name}.json"

with open(config_path) as f:
    config = json.load(f)

blacklist = config["blacklist"]
author_email = config["author_email"]
anonymization_map = config.get("anonymization_map", {})
last_run = config.get("last_run", "2024-01-01")
\`\`\`

### 2. Get Commits Since Last Run

\`\`\`bash
uv run ~/dev/CV/.claude/plugins/cv-updater/lib/cv-updater-git.py \\
  get-commits \\
  --author-email "<author-email>" \\
  --since "<last-run-date>" \\
  --branch <user-specified-branch> \\
  --cwd <repo-path> \\
  --project-name <project-name>
\`\`\`

### 3. Filter Blacklisted Commits

For each commit:
- Check if message OR file paths contain blacklisted terms (case-insensitive, partial match)
- If match: skip commit, log to findings.jsonl as type "skipped_commit"

\`\`\`python
def is_blacklisted(commit, blacklist):
    text = commit["message"] + " " + " ".join(commit.get("files", []))
    return any(term.lower() in text.lower() for term in blacklist)
\`\`\`

### 4. Analyze Remaining Commits for CV Value

**High-value commits (KEEP):**
- New features ("feat:", "add", "implement")
- Performance improvements ("perf:", "optimize", "reduce latency")
- Architecture decisions ("refactor major", "migrate", "redesign")
- Metrics-driven improvements (numbers, percentages)

**Medium-value commits (KEEP):**
- Significant bug fixes ("fix critical", "resolve production issue")
- Non-trivial refactors ("refactor:", "restructure")
- Minor features with clear user impact

**Low-value commits (SKIP):**
- Typo fixes ("typo", "fix spelling")
- Formatting ("prettier", "lint", "format")
- Trivial config ("update .gitignore", "bump version")
- Documentation only ("docs:", "update README")

### 5. Group Related Commits

Multiple small commits → one achievement:
- Example: 5 commits implementing GraphQL API → "Built GraphQL API for user data access"
- Look for commits within same date range touching same files/modules

### 6. Anonymize References

Apply anonymization_map from config:
\`\`\`python
def anonymize(text, anonymization_map):
    for original, replacement in anonymization_map.items():
        text = text.replace(original, replacement)
    return text
\`\`\`

**If term NOT in anonymization_map:**
- Client name → "Enterprise client" / "Client A"
- Project codename → "Internal platform" / "Data pipeline"
- Proprietary tech → "Custom system" / industry-standard equivalent

**Preserve:**
- Technical skills (Python, AWS, GraphQL)
- Frameworks (React, Django, CDK)
- Metrics (60% improvement, $12K savings)

### 7. Output YAML Matching \`data/experience/*.yml\`

Format:
\`\`\`yaml
- project: <Anonymized Project Name>
  entries:
    - <Achievement bullet 1>
    - <Achievement bullet 2>
\`\`\`

Example:
\`\`\`yaml
- project: Enterprise Client Platform Modernization
  entries:
    - Migrated legacy ETL to AWS Glue, reducing processing time by 60%
    - Implemented data quality checks using Great Expectations
    - Set up monitoring with CloudWatch metrics and alarms
\`\`\`

### 8. Write Findings to Database

Clear old findings, then append:
\`\`\`python
from pathlib import Path

project_name = "<detected-or-provided-project-name>"
findings_dir = Path.home() / "dev/CV/update-cv-db/findings"
findings_dir.mkdir(parents=True, exist_ok=True)
findings_path = findings_dir / f"{project_name}-findings.jsonl"

# Clear
with open(findings_path, "w") as f:
    pass

# Append achievements
for achievement in achievements:
    finding = {
        "type": "achievement",
        "commits": [c["hash"] for c in achievement["commits"]],
        "category": "experience",
        "project": achievement["project"],
        "bullet": achievement["bullet"],
        "value": achievement["value"],  # high|medium
        "anonymized": True,
        "anonymization_map": achievement["anonymization_map"],
        "timestamp": datetime.utcnow().isoformat()
    }
    with open(findings_path, "a") as f:
        f.write(json.dumps(finding) + "\\n")

# Append skipped commits
for skipped in skipped_commits:
    finding = {
        "type": "skipped_commit",
        "hash": skipped["hash"],
        "reason": "blacklist_match",
        "matched_term": skipped["matched_term"],
        "message": skipped["message"],
        "timestamp": datetime.utcnow().isoformat()
    }
    with open(findings_path, "a") as f:
        f.write(json.dumps(finding) + "\\n")
\`\`\`

### 9. Update Config with Last Run Date

\`\`\`python
config["last_run"] = datetime.utcnow().strftime("%Y-%m-%d")
config_path = Path.home() / "dev/CV/update-cv-db/config" / f"{project_name}.json"
with open(config_path, "w") as f:
    json.dump(config, f, indent=2)
\`\`\`

### 10. Return YAML Summary

Return to main agent:

\`\`\`yaml
# CV Updates from <N> commits since <last-run-date>

- project: Enterprise Client Platform Modernization
  entries:
    - Migrated legacy ETL to AWS Glue, reducing processing time by 60%
    - Implemented data quality checks using Great Expectations

---
Skipped 3 commits due to blacklist:
- abc123: "Update internal-only config" (matched: internal-only)
- def456: "Fix client-secret integration" (matched: client-secret-name)

Findings written to: ~/dev/CV/update-cv-db/findings/{project-name}-findings.jsonl
Config updated: last_run = 2024-07-23
\`\`\`

## Red Flags

- **Using real client names:** ALWAYS anonymize, even if "valuable"
- **Ignoring blacklist:** Privacy > CV completeness
- **Over-inferring:** Typo fixes are NOT achievements
- **Inconsistent anonymization:** "Client A" in one place, "Acme Corp" in another
- **Wrong YAML structure:** Must match \`data/experience/*.yml\` exactly

## Success Criteria

- All blacklisted commits skipped (logged to findings.jsonl)
- Only high/medium value commits → achievements
- All client/project names anonymized consistently
- YAML output matches \`data/experience/*.yml\` structure
- Config updated with last_run date
- Summary returned to main agent under 300 words`,
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

- **Python script:** `../../lib/cv-updater-git.py`
- **Config (read):** `~/dev/CV/update-cv-db/config/{project-name}.json`
- **Findings (written):** `~/dev/CV/update-cv-db/findings/{project-name}-findings.jsonl`
