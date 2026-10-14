# QA raw results: repo-pulse (branch anu/2610-build-and-publish-repo-pulse, commit 891c160)

Date: 2026-10-14. Environment: Linux, Python 3.14.4, run in fresh venvs at `/tmp/qa-venv` (editable install) and `/tmp/qa-venv2` (regular install). I did not use the worktree's existing `.venv`.
No tracked files were modified (`git status --short` is clean apart from this file).

Note: `/home/anu/raj/dev/first-project` is the main checkout on branch `main` and has only 1 commit (`e95536b`, README.md). The feature commit lives only on this branch, so "1 commit" is the correct result there. I also ran the tool against this worktree, which has 2 commits.

| # | Check | Verdict |
|---|-------|---------|
| 1 | Text report on first-project | PASS |
| 2 | `--since "7 days ago"` | PASS |
| 3 | `--json` is valid JSON | PASS |
| 4 | pytest | PASS (16/16) |
| 5 | `pip install .` provides `repo-pulse` | PASS |
| 6 | CI matrix 3.9–3.12 | PASS |
| 7 | README install/usage/tests | PASS |
| 8 | Empty repo | PASS |
| 9 | Not a git repo / invalid path | PASS |
| 10 | No commits in `--since` window | PASS (see note) |

## 1. Text report
`python3 -m venv /tmp/qa-venv && /tmp/qa-venv/bin/pip install -e .` → exit 0
`repo-pulse /home/anu/raj/dev/first-project` → exit 0, output:
```
Total commits: 1
Commits per day:   2026-10-14  1
Top changed files:    1  README.md
Contributors:    1  Anu
```
**PASS**

## 2. --since filter
`repo-pulse /home/anu/raj/dev/first-project --since "7 days ago"` → exit 0, 1 commit (2026-10-14, inside the window).
Extra check to confirm the filter actually excludes commits (worktree with 2 commits at 03:18 and 08:18 +05:30):
- `repo-pulse .` → Total commits: 2
- `repo-pulse . --since "2026-10-14T05:00:00+05:30"` → Total commits: 1 (the older commit is excluded and README.md's count drops from 2 to 1)
**PASS**

## 3. --json
`repo-pulse /home/anu/raj/dev/first-project --json > /tmp/qa-out.json` → exit 0
`python -c "import json,sys; json.load(sys.stdin); print('valid JSON')" < /tmp/qa-out.json` → `valid JSON`
Keys: commits_per_day, top_files, contributors, total_commits.
**PASS**

## 4. Tests
`python -m pytest tests/ -v -p no:cacheprovider` → `16 passed in 0.76s`, exit 0
(11 tests in test_analyzer.py and 5 in test_cli.py, covering the empty repo, not-a-repo, invalid path, a since window with no commits, and JSON output.)
**PASS**

## 5. pip install .
`python3 -m venv /tmp/qa-venv2 && /tmp/qa-venv2/bin/pip install .` → exit 0
`/tmp/qa-venv2/bin/repo-pulse --help` → exit 0 and prints usage `repo-pulse [-h] [--since SINCE] [--json] [path]`
**PASS**

## 6. CI workflow
`.github/workflows/ci.yml` exists. `grep -n python-version` → `python-version: ["3.9", "3.10", "3.11", "3.12"]`. Its steps are checkout, setup-python, `pip install .`, `pip install pytest` and `python -m pytest tests/`.
**PASS** (file content only. CI was not run, and only Python 3.14 is available locally, so I could not test 3.9–3.12 here.)

## 7. README
`grep -n "^## " README.md` → `## Installation` (l.7), `## Usage` (l.16), `## Running tests` (l.62). The README also documents output examples and the edge-case behaviour.
**PASS**

## 8. Empty repo
`git init -q /tmp/qa-empty-repo && repo-pulse /tmp/qa-empty-repo` → exit 0, `Total commits: 0 / No commits found.`
The same command with `--json` gives exit 0, `total_commits: 0` and empty collections. With `--since "7 days ago"` it gives exit 0 and 0 commits.
**PASS**

## 9. Not a git repo / invalid path
- `repo-pulse /tmp/qa-notgit` → exit 1, stdout empty, stderr `repo-pulse: error: fatal: not a git repository (or any parent up to mount point /) ...`
- `repo-pulse /tmp` → exit 1, same stderr message
- `repo-pulse /tmp/does-not-exist` → exit 1, stderr `repo-pulse: error: fatal: cannot change to '/tmp/does-not-exist': No such file or directory`
**PASS**

## 10. No commits in --since window
- `repo-pulse /home/anu/raj/dev/first-project --since "2000-01-01"` → exit 0, **1 commit**. This is correct: `--since 2000-01-01` means "after 2000", so every commit is included. The command proposed in the QA brief does not produce an empty window.
- `repo-pulse /home/anu/raj/dev/first-project --since "2099-01-01"` → exit 0, `Total commits: 0 / No commits found.`
- The same command with `--json` → exit 0, `total_commits: 0`
**PASS**

## Bugs / observations (none blocking)
1. **Invalid `--since` values are silently accepted.** `repo-pulse <repo> --since "garbage-date"` exits 0 and reports 0 commits with no warning. This comes from git's own date parsing. It is minor, but it could mislead users.
2. **A subdirectory of a repo is analyzed as the whole repo.** Because the tool uses `git -C <path>`, pointing it at a subdirectory summarizes the enclosing repository. This is probably acceptable, but it is not documented.
3. **Dates are grouped by the author's timezone, not the viewer's.** `commits_per_day` uses the date part of `%aI`, which is the author's local date.
4. **The QA brief has an error.** Check 10's example (`--since 2000-01-01`) does not create an empty window. Use a future date instead.
5. **Python 3.9–3.12 were not run locally.** The code uses `from __future__ import annotations` with `dict[str, int]` and `list[str] | None` hints, which should work on 3.9, but only CI can confirm it.

`python -m repo_pulse.cli <repo>` (run from /tmp) also works, exit 0.

## Overall: PASS
