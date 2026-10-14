import pytest

from repo_pulse.analyzer import GitError, RepoSummary, _build_report, analyze_repo


def test_analyze_repo_basic(test_repo):
    assert analyze_repo(test_repo).total_commits == 3


def test_analyze_repo_commits_per_day(test_repo):
    assert analyze_repo(test_repo).commits_per_day == {"2024-01-01": 2, "2024-01-03": 1}


def test_analyze_repo_top_files(test_repo):
    assert analyze_repo(test_repo).top_files == [("a.txt", 3), ("b.txt", 1), ("c.txt", 1)]


def test_analyze_repo_contributors(test_repo):
    assert analyze_repo(test_repo).contributors == [("Alice", 2), ("Bob", 1)]


def test_analyze_repo_with_since(test_repo):
    summary = analyze_repo(test_repo, since="2024-01-02")
    assert summary.total_commits == 1
    assert summary.commits_per_day == {"2024-01-03": 1}
    assert summary.contributors == [("Alice", 1)]


def test_analyze_repo_since_no_commits(test_repo):
    assert analyze_repo(test_repo, since="2030-01-01") == RepoSummary()


def test_analyze_repo_empty(empty_repo):
    assert analyze_repo(empty_repo) == RepoSummary()


def test_analyze_repo_not_a_repo(tmp_path):
    with pytest.raises(GitError):
        analyze_repo(str(tmp_path))


def test_analyze_repo_invalid_path(tmp_path):
    with pytest.raises(GitError):
        analyze_repo(str(tmp_path / "does-not-exist"))


def test_build_report(test_repo):
    report = _build_report(analyze_repo(test_repo))
    assert "Total commits: 3" in report
    assert "2024-01-01  2" in report
    assert "a.txt" in report
    assert "Alice" in report


def test_build_report_empty():
    assert "No commits found." in _build_report(RepoSummary())
