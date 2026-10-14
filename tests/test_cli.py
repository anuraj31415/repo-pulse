import json

from repo_pulse.cli import main


def test_main_defaults(test_repo, monkeypatch, capsys):
    monkeypatch.chdir(test_repo)
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "Total commits: 3" in out
    assert "Contributors:" in out


def test_main_json_flag(test_repo, capsys):
    assert main([test_repo, "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["total_commits"] == 3
    assert data["commits_per_day"] == {"2024-01-01": 2, "2024-01-03": 1}
    assert data["contributors"] == [["Alice", 2], ["Bob", 1]]


def test_main_since(test_repo, capsys):
    assert main([test_repo, "--since", "2024-01-02", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["total_commits"] == 1


def test_main_empty_repo(empty_repo, capsys):
    assert main([empty_repo]) == 0
    assert "No commits found." in capsys.readouterr().out


def test_main_not_a_repo(tmp_path, capsys):
    assert main([str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "repo-pulse: error:" in captured.err
