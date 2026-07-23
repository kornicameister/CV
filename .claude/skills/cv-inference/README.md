# CV Inference Skill

**Automatically infer CV updates from git commit history with privacy-first anonymization.**

## What It Does

Analyzes your work repo commits and suggests CV-ready YAML bullets:
- ✅ Filters commits by your git email (not name — more reliable)
- ✅ Infers high-value achievements (features, perf improvements, architecture)
- ✅ Anonymizes client/project names automatically
- ✅ Respects per-project blacklist (never leaks sensitive terms)
- ✅ Outputs YAML matching `data/experience/*.yml` structure

## Quick Start

### 1. Initialize (First Time)

In your CV repo:
```bash
/cv-inference:init
```

This will:
1. Ask for your git email (defaults to `git config user.email`)
2. Sample git history to detect sensitive terms
3. Present categorized blacklist for your approval
4. Ask to install git hook for notifications (default: YES)
5. Save config to `.claude/skills/cv-inference/config.json`

### 2. Update CV from Recent Work

After working on a project:
```bash
/cv-inference:update
```

This will:
1. Load your blacklist from config
2. Get commits since last run (by your git email)
3. Filter blacklisted commits
4. Infer CV-worthy achievements
5. Anonymize client/project names
6. Output YAML ready to paste into `data/experience/*.yml`

### 3. Git Hook Notifications

If you said YES during init, hook is already installed. Otherwise:

```bash
# Manually install in work repo
cp ~/.claude/skills/cv-inference/post-merge.hook /path/to/work/repo/.git/hooks/post-merge
chmod +x /path/to/work/repo/.git/hooks/post-merge
```

Now every `git pull origin main` shows:
```
✨ CV Inference Notification
Found 5 new commits by you@email.com on main
Consider running: /cv-inference:update
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill documentation |
| `cv-inference-git.py` | Git operations helper script |
| `config-template.json` | Config structure (filled by init) |
| `post-merge.hook` | Git hook template for notifications |
| `findings.jsonl` | Local knowledge base (gitignored) |
| `subagents/init-blacklist.md` | Subagent for blacklist initialization |
| `subagents/update-cv.md` | Subagent for CV updates |

## Examples

### Init Output

```
Detected git user.email: you@company.com
Is this correct? (yes)

Detected client names:
- Acme Corp (commit abc123)
- ClientXYZ Inc. (commit def456)

Detected project codenames:
- Project Phoenix (commit 789abc)

Ambiguous terms:
- Phoenix: Could be Elixir framework OR project codename?

Approve blacklist? (yes)
✓ Config saved to .claude/skills/cv-inference/config.json
```

### Update Output

```yaml
# CV Updates from 12 commits since 2024-07-01

- project: Enterprise Client Platform Modernization
  entries:
    - Migrated legacy ETL to AWS Glue, reducing processing time by 60%
    - Implemented data quality checks using Great Expectations
    - Set up monitoring with CloudWatch metrics and alarms

---
Skipped 2 commits due to blacklist:
- abc123: "Update internal-only config" (matched: internal-only)
```

## Design Principles

1. **Privacy first:** Blacklist enforcement is non-negotiable. No exceptions for "valuable" commits.
2. **Author email, not name:** `git config user.email` is unique and reliable.
3. **Subagent architecture:** Heavy analysis delegated to subagents to preserve main context.
4. **Local knowledge base:** All findings written to `findings.jsonl` (gitignored).
5. **User confirmation:** Init requires approval before saving blacklist.

## Troubleshooting

### "No commits found"
- Check your git email matches: `uv run cv-inference-git.py get-user-email`
- Verify since_date in config: older than your first commit?

### "Too many blacklist matches"
- Review blacklist in config.json
- Remove false positives (e.g., "Phoenix" if you use Elixir framework)

### "Achievements too generic"
- Subagent needs more commit context
- Try analyzing smaller date range (more detailed inference)

## Development

### Test Script

```bash
# Get your email
uv run cv-inference-git.py get-user-email

# Get commits
uv run cv-inference-git.py get-commits --author-email "you@email.com" --since 2024-01-01

# Sample for blacklist
uv run cv-inference-git.py sample-commits --rate 10
```

### Run Tests (RED-GREEN-REFACTOR)

See `test-scenarios.md` and `baseline-findings.md` for TDD workflow.
