#!/usr/bin/env python3
"""Report deterministic project identity and lightweight Git state."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse


def run_git(cwd: Path, *args: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args], cwd=str(cwd), text=True,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False
    )
    return proc.returncode, proc.stdout.rstrip("\n")


def normalize_remote(remote: str) -> str:
    remote = remote.strip()
    if not remote:
        return ""
    if re.match(r"^[A-Za-z]:[\\/]", remote) or remote.startswith(("/", "\\\\")):
        return ""  # Local paths must not identify another checkout as the same project.
    if "://" in remote:
        parsed = urlparse(remote)
        if parsed.scheme not in {"https", "http", "ssh", "git"} or not parsed.hostname:
            return ""  # Unsupported transports are not useful identity evidence.
        host = parsed.hostname.lower()
        port = parsed.port
        defaults = {"https": 443, "http": 80, "ssh": 22, "git": 9418}
        if port and port != defaults[parsed.scheme]:
            host += f":{port}"
        path = parsed.path
    else:
        match = re.fullmatch(r"(?:[^/@:]+@)?([^/:]+):(.+)", remote)
        if not match:
            return ""  # Local paths are not portable repository identity.
        host, path = match.groups()
        host = host.lower()
        path = path.split("?", 1)[0].split("#", 1)[0]
    path = path.strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return f"{host}/{path}" if path else ""



def collect_context(cwd: Path) -> dict:
    cwd = cwd.resolve()
    rc, top = run_git(cwd, "rev-parse", "--show-toplevel")
    is_git = rc == 0 and bool(top)
    root = Path(top).resolve() if is_git else cwd

    branch = ""
    remote = ""
    status_lines: list[str] = []
    if is_git:
        _, branch = run_git(root, "branch", "--show-current")
        if not branch:
            rc_head, head = run_git(root, "rev-parse", "--short", "HEAD")
            branch = f"detached@{head}" if rc_head == 0 and head else "detached"
        _, remote_raw = run_git(root, "remote", "get-url", "origin")
        remote = normalize_remote(remote_raw)
        _, status = run_git(root, "status", "--short")
        status_lines = [line for line in status.splitlines() if line.strip()]

    return {
        "checked_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "cwd": str(cwd),
        "folder_name": root.name or root.drive,
        "project_root": str(root),
        "is_git": is_git,
        "git_branch": branch,
        "git_head": run_git(root, "rev-parse", "--verify", "HEAD")[1] if is_git else "",
        "git_remote": remote,
        "dirty": bool(status_lines),
        "status_count": len(status_lines),
        "status": status_lines,
        "checkpoint_dir": str(root / ".project-checkpoint"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", default=os.getcwd())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not Path(args.cwd).is_dir():
        parser.error("--cwd must be an existing directory")
    try:
        data = collect_context(Path(args.cwd))
    except (OSError, ValueError):
        parser.error("unable to inspect project; check Git availability and repository configuration")
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for key, value in data.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
