#!/usr/bin/env python3
"""
Git operations helper for CV inference skill.

Extracts commit history, filters by author, analyzes for sensitive terms.
"""

import argparse
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any

# Global knowledge base - all projects write here
DEFAULT_CV_DB_PATH = Path.home() / "dev" / "CV" / "update-cv-db"
CV_DB_PATH = Path(os.getenv("CV_DB_PATH", DEFAULT_CV_DB_PATH))

logger = logging.getLogger(__name__)


def get_project_name(repo_path: str) -> str:
    """Extract project name from repo path."""
    return Path(repo_path).resolve().name


def ensure_cv_db_exists() -> None:
    """Ensure global CV knowledge base directories exist."""
    CV_DB_PATH.mkdir(parents=True, exist_ok=True)
    (CV_DB_PATH / "config").mkdir(exist_ok=True)
    (CV_DB_PATH / "findings").mkdir(exist_ok=True)


def get_config_path(project_name: str) -> Path:
    """Get path to project config file in global knowledge base."""
    ensure_cv_db_exists()
    return CV_DB_PATH / "config" / f"{project_name}.json"


def get_findings_path(project_name: str) -> Path:
    """Get path to project findings file in global knowledge base."""
    ensure_cv_db_exists()
    return CV_DB_PATH / "findings" / f"{project_name}-findings.jsonl"


class GitCommandRunner:
    """Seam for git command execution — isolates subprocess calls for testing."""

    def __init__(self, cwd: str = "."):
        self.cwd = cwd

    def run(self, args: list[str]) -> str:
        """Run git command and return output."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.cwd,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error("Git command failed: %s", e.stderr)
            raise RuntimeError(f"Git command failed: {e.stderr}") from e


class FileSystemOperations:
    """Seam for filesystem operations — isolates file I/O for testing."""

    def file_exists(self, path: str) -> bool:
        """Check if file exists."""
        return os.path.exists(path)

    def read_file(self, path: str) -> str:
        """Read file content."""
        with open(path) as f:
            return f.read()

    def is_executable(self, path: str) -> bool:
        """Check if file is executable."""
        return os.access(path, os.X_OK)

    def join_path(self, *parts: str) -> str:
        """Join path components."""
        return os.path.join(*parts)


def is_merge_commit(commit_hash: str, *, runner: GitCommandRunner) -> bool:
    """Check if commit is a merge commit (has >1 parent)."""
    output = runner.run(["rev-list", "--parents", "-n", "1", commit_hash])
    return len(output.split()) > 2


def get_commits(
    *,
    author_email: str,
    runner: GitCommandRunner,
    since_date: str | None = None,
    since_commit: str | None = None,
    branch: str = "main",
    include_merges: bool = False,
) -> list[dict[str, Any]]:
    """
    Get commits by author email since date or commit on specified branch.

    Args:
        author_email: Git author email to filter by (more reliable than name)
        runner: Git command runner
        since_date: ISO date string (YYYY-MM-DD) or None for all commits
        since_commit: Commit hash to start from (exclusive) or None
        branch: Branch name (default: main)
        include_merges: Include merge commits (default: False)

    Returns:
        List of commit dicts with: hash, author, email, date, message, is_merge

    Note:
        If both since_date and since_commit are provided, since_commit takes precedence.
    """
    cmd = [
        "log",
        f"--author={author_email}",
        "--format=%H|%an|%ae|%ad|%s",
        "--date=iso-strict",
    ]

    # Commit range takes precedence over date
    if since_commit:
        cmd.insert(1, f"{since_commit}..{branch}")
    else:
        cmd.insert(1, branch)
        if since_date:
            cmd.append(f"--since={since_date}")

    if not include_merges:
        cmd.append("--no-merges")

    output = runner.run(cmd)
    if not output:
        return []

    commits = []
    for line in output.split("\n"):
        if not line:
            continue
        parts = line.split("|", maxsplit=4)
        if len(parts) != 5:
            continue

        commit_hash, author_name, author_email, date_str, message = parts
        commits.append(
            {
                "hash": commit_hash,
                "author": author_name,
                "email": author_email,
                "date": date_str,
                "message": message,
                "is_merge": False,  # already filtered by --no-merges
            }
        )

    return commits


def get_commit_details(commit_hash: str, *, runner: GitCommandRunner) -> dict[str, Any]:
    """
    Get full commit details including diff stats and changed files.

    Returns:
        Dict with: hash, author, date, message, files, stats, diff
    """
    metadata_output = runner.run(
        ["show", "--format=%H|%an|%ad|%s", "--quiet", commit_hash]
    )
    parts = metadata_output.split("|", maxsplit=3)
    if len(parts) != 4:
        raise ValueError(f"Unexpected git show output for {commit_hash}")

    commit_hash_verified, author, date_str, message = parts

    files = runner.run(
        ["diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash]
    ).split("\n")
    stats_output = runner.run(["show", "--stat", "--format=", commit_hash])
    stats_lines = [line for line in stats_output.split("\n") if line.strip()]
    stats_summary = stats_lines[-1] if stats_lines else ""
    diff = runner.run(["show", commit_hash])

    return {
        "hash": commit_hash_verified,
        "author": author,
        "date": date_str,
        "message": message,
        "files": [f for f in files if f],
        "stats": stats_summary,
        "diff": diff,
    }


def sample_commits(
    *,
    runner: GitCommandRunner,
    branch: str = "main",
    sample_rate: int = 10,
) -> list[dict[str, str]]:
    """
    Sample commits for blacklist inference (every Nth commit).

    Args:
        runner: Git command runner
        branch: Branch to sample from
        sample_rate: Take every Nth commit (default: 10)

    Returns:
        List of dicts with: hash, message
    """
    output = runner.run(["log", branch, "--all", "--format=%H|%s"])
    if not output:
        return []

    lines = output.split("\n")
    sampled = []

    for i, line in enumerate(lines):
        if i % sample_rate == 0 and line:
            parts = line.split("|", maxsplit=1)
            if len(parts) == 2:
                sampled.append({"hash": parts[0], "message": parts[1]})

    return sampled


def get_git_user_email(*, runner: GitCommandRunner) -> str:
    """Get configured git user.email from git config."""
    return runner.run(["config", "user.email"])


def check_hook_exists(
    repo_path: str,
    *,
    fs_ops: FileSystemOperations,
    hook_name: str = "post-merge",
) -> dict[str, Any]:
    """
    Check if git hook exists in repo.

    Returns:
        Dict with: exists (bool), path (str), content (str|None), executable (bool)
    """
    hook_path = fs_ops.join_path(repo_path, ".git", "hooks", hook_name)

    if not fs_ops.file_exists(hook_path):
        return {
            "exists": False,
            "path": hook_path,
            "content": None,
            "executable": False,
        }

    content = fs_ops.read_file(hook_path)
    executable = fs_ops.is_executable(hook_path)

    return {
        "exists": True,
        "path": hook_path,
        "content": content,
        "executable": executable,
    }


def _format_hook_result_for_display(result: dict[str, Any]) -> dict[str, Any]:
    """Format hook check result for CLI display (preview instead of full content)."""
    if not result.get("content"):
        return result

    lines = result["content"].split("\n")
    preview_lines = lines[:5]
    has_more = len(lines) > 5

    return {
        **{k: v for k, v in result.items() if k != "content"},
        "content_preview": "\n".join(preview_lines) + ("\n..." if has_more else ""),
        "content_lines": len(lines),
    }


def get_commit_messages(
    *,
    author_email: str,
    runner: GitCommandRunner,
    since_date: str | None = None,
    since_commit: str | None = None,
    branch: str = "main",
) -> list[str]:
    """
    Get just commit messages (for LLM analysis).

    Returns:
        List of commit message strings
    """
    commits = get_commits(
        author_email=author_email,
        runner=runner,
        since_date=since_date,
        since_commit=since_commit,
        branch=branch,
    )
    return [c["message"] for c in commits]


def main() -> None:
    """CLI entrypoint."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="Git operations for CV inference")
    parser.add_argument(
        "--project-name",
        help="Project name for global knowledge base (default: inferred from repo path)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # get-user-email command
    email_parser = subparsers.add_parser(
        "get-user-email", help="Get configured git user.email"
    )
    email_parser.add_argument("--cwd", default=".", help="Repository path")

    # check-hook-exists command
    hook_check_parser = subparsers.add_parser(
        "check-hook-exists", help="Check if git hook exists"
    )
    hook_check_parser.add_argument("repo_path", help="Repository path")
    hook_check_parser.add_argument(
        "--hook-name", default="post-merge", help="Hook name"
    )

    # get-commits command
    get_parser = subparsers.add_parser(
        "get-commits", help="Get commits by author email"
    )
    get_parser.add_argument(
        "--author-email", required=True, help="Author email to filter by"
    )
    get_parser.add_argument("--since", help="Start date (YYYY-MM-DD)")
    get_parser.add_argument(
        "--since-commit", help="Start commit hash (exclusive, takes precedence over --since)"
    )
    get_parser.add_argument("--branch", default="main", help="Branch name")
    get_parser.add_argument("--cwd", default=".", help="Repository path")

    # get-commit-details command
    details_parser = subparsers.add_parser(
        "get-commit-details", help="Get full commit details"
    )
    details_parser.add_argument("hash", help="Commit hash")
    details_parser.add_argument("--cwd", default=".", help="Repository path")

    # sample-commits command
    sample_parser = subparsers.add_parser(
        "sample-commits", help="Sample commits for analysis"
    )
    sample_parser.add_argument("--branch", default="main", help="Branch name")
    sample_parser.add_argument(
        "--rate", type=int, default=10, help="Sample rate (every Nth)"
    )
    sample_parser.add_argument("--cwd", default=".", help="Repository path")

    # get-messages command
    messages_parser = subparsers.add_parser(
        "get-messages", help="Get commit messages only"
    )
    messages_parser.add_argument("--author-email", required=True, help="Author email")
    messages_parser.add_argument("--since", help="Start date (YYYY-MM-DD)")
    messages_parser.add_argument(
        "--since-commit", help="Start commit hash (exclusive, takes precedence over --since)"
    )
    messages_parser.add_argument("--branch", default="main", help="Branch name")
    messages_parser.add_argument("--cwd", default=".", help="Repository path")

    args = parser.parse_args()
    runner = GitCommandRunner(cwd=getattr(args, "cwd", "."))
    fs_ops = FileSystemOperations()

    # Infer project name if not provided
    cwd = getattr(args, "cwd", ".")
    project_name = args.project_name or get_project_name(cwd)

    # Log global knowledge base paths (for visibility)
    logger.info("Global CV DB: %s", CV_DB_PATH)
    logger.info("Project name: %s", project_name)
    logger.info("Config path: %s", get_config_path(project_name))
    logger.info("Findings path: %s", get_findings_path(project_name))

    if args.command == "get-user-email":
        email = get_git_user_email(runner=runner)
        print(json.dumps({"email": email}, indent=2))

    elif args.command == "check-hook-exists":
        result = check_hook_exists(
            args.repo_path, fs_ops=fs_ops, hook_name=args.hook_name
        )
        display_result = _format_hook_result_for_display(result)
        print(json.dumps(display_result, indent=2))

    elif args.command == "get-commits":
        commits = get_commits(
            author_email=args.author_email,
            runner=runner,
            since_date=args.since,
            since_commit=getattr(args, "since_commit", None),
            branch=args.branch,
        )
        print(json.dumps({"commits": commits}, indent=2))

    elif args.command == "get-commit-details":
        details = get_commit_details(args.hash, runner=runner)
        print(json.dumps(details, indent=2))

    elif args.command == "sample-commits":
        sampled = sample_commits(
            runner=runner, branch=args.branch, sample_rate=args.rate
        )
        print(json.dumps({"sampled": sampled}, indent=2))

    elif args.command == "get-messages":
        messages = get_commit_messages(
            author_email=args.author_email,
            runner=runner,
            since_date=args.since,
            since_commit=getattr(args, "since_commit", None),
            branch=args.branch,
        )
        print(json.dumps({"messages": messages}, indent=2))


if __name__ == "__main__":
    main()
