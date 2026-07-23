---
name: cv-inference-init
description: Initialize CV inference blacklist from git history. First-time setup that samples commits, detects sensitive terms (client/project names), and creates anonymization config. Use when setting up CV inference for the first time or adding a new project repo.
---

# CV Inference: Initialize Blacklist

First-time setup for CV inference. Analyzes git history to detect sensitive terms, then creates blacklist config.

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
6. Saves config to `.claude/skills/cv-inference/config.json`

## Workflow

**Delegate to subagent** (preserves main context):

```javascript
Agent({
  description: "Initialize CV inference blacklist",
  prompt: `You are setting up CV inference for the first time.

**Steps:**

1. Get git user email:
   \`\`\`bash
   uv run ../cv-inference/cv-inference-git.py get-user-email --cwd /path/to/repo
   \`\`\`
   Present to user: "Detected email: X. Is this correct?"

2. Sample git history:
   \`\`\`bash
   uv run ../cv-inference/cv-inference-git.py sample-commits --rate 10 --branch main --cwd /path/to/repo
   \`\`\`

3. Analyze sampled commits for sensitive terms:
   - Client names (companies, organizations)
   - Project codenames (internal names, acronyms)  
   - Proprietary systems (internal tools)
   - Sensitivity markers (confidential, internal-only, NDA)

4. Write findings to \`.claude/skills/cv-inference/findings.jsonl\`:
   \`\`\`jsonl
   {"type":"blacklist_term","category":"client","term":"Acme Corp","context":"commit abc123","confidence":"high"}
   \`\`\`

5. Return categorized summary for user approval:
   - Client Names (high confidence)
   - Project Codenames (medium confidence)
   - Ambiguous Terms (needs review)
   - Sensitivity Markers

6. Ask about git hook installation (default: YES):
   - Check if hook exists: \`uv run ../cv-inference/cv-inference-git.py check-hook-exists /path/to/repo\`
   - If exists: show preview, ask Merge/Overwrite/Skip
   - If not exists: copy hook, make executable

7. Save config to \`.claude/skills/cv-inference/config.json\`:
   \`\`\`json
   {
     "blacklist": ["term1", "term2"],
     "author_email": "you@email.com",
     "since_date": "2024-01-01",
     "monitored_repos": ["/path/to/repo"]
   }
   \`\`\`

**Read the full subagent instructions from:**
\`../cv-inference/subagents/init-blacklist.md\`

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
- Config saved to `.claude/skills/cv-inference/config.json`
- Git hook installed (if user approved)
- User can now run `/cv-inference-update`

## Common Issues

### "No commits found"
→ Check repo path is correct, branch name (main vs master)

### "Hook already exists"
→ Show user existing hook, offer Merge/Overwrite/Skip

### "Too many blacklist terms"
→ Filter out public tech (AWS, React, Docker), keep only proprietary

## Files

- **Subagent:** `../cv-inference/subagents/init-blacklist.md`
- **Python script:** `../cv-inference/cv-inference-git.py`
- **Hook template:** `../cv-inference/post-merge.hook`
- **Config:** `.claude/skills/cv-inference/config.json` (created)
- **Findings:** `.claude/skills/cv-inference/findings.jsonl` (created)
