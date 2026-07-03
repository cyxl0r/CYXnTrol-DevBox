from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitResult:
    pushed: bool


def _git(arguments: list[str], cwd: Path | None, reporter, check: bool = True) -> subprocess.CompletedProcess[str]:
    command = ["git", "-c", "i18n.logOutputEncoding=utf-8", *arguments]
    reporter.info("Git command.", " ".join(command))
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = result.stdout.strip()
    if output:
        reporter.info("Git output.", output)
    if check and result.returncode != 0:
        raise RuntimeError(f"Git command failed ({result.returncode}): {' '.join(command)}")
    return result


def _require_git() -> None:
    if shutil.which("git") is None:
        raise FileNotFoundError("Git was not found in PATH.")


def _ensure_author_identity(workspace: Path) -> None:
    def configured_value(key: str) -> str:
        result = subprocess.run(
            ["git", "-c", "i18n.logOutputEncoding=utf-8", "config", "--get", key],
            cwd=str(workspace),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        return result.stdout.strip() if result.returncode == 0 else ""

    if not configured_value("user.name") or not configured_value("user.email"):
        raise RuntimeError("Git author identity is not configured. Set git config --global user.name and user.email before pushing.")


def _clone_repository(url: str, workspace: Path, reporter) -> None:
    if workspace.exists():
        shutil.rmtree(workspace, ignore_errors=True)
    _git(["clone", url, str(workspace)], None, reporter)


def _checkout_branch(workspace: Path, branch: str, reporter) -> None:
    current = _git(["branch", "--show-current"], workspace, reporter, check=False).stdout.strip()
    if current == branch:
        return
    existing = _git(["show-ref", "--verify", f"refs/heads/{branch}"], workspace, reporter, check=False)
    if existing.returncode == 0:
        _git(["checkout", branch], workspace, reporter)
        return
    remote = _git(["show-ref", "--verify", f"refs/remotes/origin/{branch}"], workspace, reporter, check=False)
    if remote.returncode == 0:
        _git(["checkout", "-B", branch, f"origin/{branch}"], workspace, reporter)
        return
    _git(["checkout", "-B", branch], workspace, reporter)


def _protected_repository_item(item: Path) -> bool:
    return item.name == ".git" or (item.name == "assets" and (item / "pictures").is_dir())


def _remove_obsolete_content(workspace: Path, reporter) -> None:
    for item in workspace.iterdir():
        if _protected_repository_item(item):
            if item.name == "assets":
                for child in item.iterdir():
                    if child.name == "pictures":
                        continue
                    if child.is_dir():
                        shutil.rmtree(child)
                    else:
                        child.unlink()
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    reporter.info("Obsolete repository content removed; assets/pictures was preserved.")


def _copy_publish_root(root_dir: Path, workspace: Path) -> None:
    for source in root_dir.iterdir():
        target = workspace / source.name
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.copy2(source, target)


def _has_staged_changes(workspace: Path, reporter) -> bool:
    _git(["add", "--all"], workspace, reporter)
    return _git(["diff", "--cached", "--quiet"], workspace, reporter, check=False).returncode != 0


def _write_commit_message_file(workspace: Path, commit_text: str) -> Path:
    message_file = workspace / ".git" / "desknode_commit_message.txt"
    message_file.write_text(commit_text, encoding="utf-8", newline="\n")
    return message_file


def sync_and_push(root_dir: Path, repository_url: str, repository_branch: str, repository_workspace: Path, commit_text: str, reporter) -> GitResult:
    _require_git()
    _clone_repository(repository_url, repository_workspace, reporter)
    _ensure_author_identity(repository_workspace)
    branch = repository_branch or "main"
    _checkout_branch(repository_workspace, branch, reporter)
    _remove_obsolete_content(repository_workspace, reporter)
    _copy_publish_root(root_dir, repository_workspace)
    if not _has_staged_changes(repository_workspace, reporter):
        reporter.info("Repository has no content changes.")
        return GitResult(pushed=False)
    message_file = _write_commit_message_file(
        repository_workspace,
        commit_text.strip() or "Update deskNode repository",
    )
    try:
        _git(["-c", "i18n.commitEncoding=utf-8", "commit", "-F", str(message_file)], repository_workspace, reporter)
    finally:
        message_file.unlink(missing_ok=True)
    _git(["push", "-u", "origin", branch], repository_workspace, reporter)
    return GitResult(pushed=True)
