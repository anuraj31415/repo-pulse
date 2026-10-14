# repo-pulse

`repo-pulse` is a small command-line tool that summarizes a local git
repository's recent activity: commits per day, the most frequently changed
files, and contributors.

## Installation

Requires Python 3.9+ and `git` on your `PATH`.

```bash
pip install .          # regular install
pip install -e .       # editable install for development
```

## Usage

```bash
repo-pulse                                    # current directory, all commits
repo-pulse /path/to/repo --since "7 days ago" # only recent commits
repo-pulse --since 2024-01-01 --json          # machine-readable output
python -m repo_pulse.cli                      # run without installing
```

`--since` accepts anything `git log --since` understands (`"2 weeks ago"`,
`2024-01-01`, ...).

Example text output:

```
Total commits: 3

Commits per day:
  2024-01-01  2
  2024-01-03  1

Top changed files:
     3  a.txt
     1  b.txt
     1  c.txt

Contributors:
     2  Alice
     1  Bob
```

With `--json`:

```json
{
  "commits_per_day": {"2024-01-01": 2, "2024-01-03": 1},
  "top_files": [["a.txt", 3], ["b.txt", 1], ["c.txt", 1]],
  "contributors": [["Alice", 2], ["Bob", 1]],
  "total_commits": 3
}
```

An empty repository, or a `--since` window with no commits, reports zero
commits. If the path is not a git repository, `repo-pulse` prints an error to
stderr and exits with status 1.

## Running tests

```bash
pip install -e ".[dev]"
python -m pytest tests/
```
