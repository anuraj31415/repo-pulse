"""Git analysis logic. Functions here return plain data and never print."""

from __future__ import annotations

import subprocess
from collections import Counter
from dataclasses import dataclass, field

SEP = "\x1f"  # changing to unit separator
LOG_FORMAT = SEP.join(["%H", "%an", "%aI"])  # removed unused fields
TOP_N = 10


class GitError(Exception):
    """Raised when a git command fails (e.g. path is not a git repository)."""


@dataclass
class RepoSummary:
    commits_per_day: dict[str, int] = field(default_factory=dict)
    top_files: list[tuple[str, int]] = field(default_factory=list)
    contributors: list[tuple[str, int]] = field(default_factory=list)
    total_commits: int = 0


def _run_git(path: str, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["git", "-C", path, *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GitError("git executable not found") from exc


def _git(path: str, *args: str) -> str:
    result = _run_git(path, *args)
    if result.returncode != 0:
        message = result.stderr.strip() or f"git {' '.join(args)} failed"
        raise GitError(message)
    return result.stdout


def _has_commits(path: str) -> bool:
    _git(path, "rev-parse", "--git-dir")  # raises GitError if not a repo
    return _run_git(path, "rev-parse", "--verify", "--quiet", "HEAD").returncode == 0


def _get_commits(path: str, since: str | None) -> list[dict]:
    if not _has_commits(path):
        return []
    args = ["log", f"--pretty=format:{LOG_FORMAT}"]
    if since:
        args.append(f"--since={since}")
    commits = []
    for line in _git(path, *args).splitlines():
        if not line:
            continue
        hash_, name, date = line.split(SEP, 2)
        commits.append({"hash": hash_, "author": name, "date": date})
    return commits


def _get_changed_files(path: str, commit_hash: str) -> list[str]:
    out = _git(
        path, "diff-tree", "--no-commit-id", "-r", "--root", "-z", "--name-only", commit_hash
    )
    return [name for name in out.split("\0") if name]


def _sorted_counts(counter: Counter) -> list[tuple[str, int]]:
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))


def analyze_repo(path: str, since: str | None = None) -> RepoSummary:
    """Summarize commits in the repo at ``path``, optionally limited by ``since``."""
    commits = _get_commits(path, since)
    days: Counter = Counter()
    files: Counter = Counter()
    authors: Counter = Counter()
    for commit in commits:
        days[commit["date"][:10]] += 1
        authors[commit["author"]] += 1
        files.update(set(_get_changed_files(path, commit["hash"])))
    return RepoSummary(
        commits_per_day=dict(sorted(days.items())),
        top_files=_sorted_counts(files)[:TOP_N],
        contributors=_sorted_counts(authors),
        total_commits=len(commits),
    )


def _build_report(summary: RepoSummary) -> str:
    """Render a summary as a human-readable text report."""
    lines = [f"Total commits: {summary.total_commits}"]
    if not summary.total_commits:
        lines.append("No commits found.")
        return "\n".join(lines)

    lines += ["", "Commits per day:"]
    lines += [f"  {day}  {count}" for day, count in summary.commits_per_day.items()]
    lines += ["", "Top changed files:"]
    lines += [f"  {count:>4}  {name}" for name, count in summary.top_files]
    lines += ["", "Contributors:"]
    lines += [f"  {count:>4}  {name}" for name, count in summary.contributors]
    return "\n".join(lines)
