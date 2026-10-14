import os
import subprocess

import pytest


def _git(repo, *args, env=None):
    subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, env=env
    )


def _commit(repo, author, date, files, message):
    for name, content in files.items():
        (repo / name).write_text(content)
    _git(repo, "add", *files)
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": author,
        "GIT_AUTHOR_EMAIL": f"{author.lower()}@example.com",
        "GIT_AUTHOR_DATE": date,
        "GIT_COMMITTER_NAME": author,
        "GIT_COMMITTER_EMAIL": f"{author.lower()}@example.com",
        "GIT_COMMITTER_DATE": date,
    }
    _git(repo, "commit", "-m", message, env=env)


@pytest.fixture(autouse=True)
def isolated_git_config(monkeypatch, tmp_path):
    """Keep the user's git config and any enclosing repo out of tests."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))


@pytest.fixture
def empty_repo(tmp_path):
    repo = tmp_path / "empty_repo"
    repo.mkdir()
    _git(repo, "init")
    return str(repo)


@pytest.fixture
def test_repo(tmp_path):
    """A git repo with three commits by two authors on two days."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@test.com")
    _git(repo, "config", "user.name", "Test User")
    _commit(repo, "Alice", "2024-01-01T10:00:00+00:00",
            {"a.txt": "1", "b.txt": "1"}, "first")
    _commit(repo, "Bob", "2024-01-01T12:00:00+00:00",
            {"a.txt": "2"}, "second")
    _commit(repo, "Alice", "2024-01-03T09:00:00+00:00",
            {"a.txt": "3", "c.txt": "1"}, "third")
    return str(repo)


@pytest.fixture
def test_repo_special_filenames(tmp_path):
    """A git repo with files that have non-ASCII names and spaces."""
    repo = tmp_path / "test_repo_special"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@test.com")
    _git(repo, "config", "user.name", "Test User")
    _commit(repo, "Alice", "2024-01-01T10:00:00+00:00",
            {"café.txt": "cafe", "my file.txt": "space"}, "special filenames")
    return str(repo)