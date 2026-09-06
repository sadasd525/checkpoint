# Publish the current project to a private GitHub repository

Use this procedure only for an explicit `$checkpoint publish` operation.

## Preconditions

Run all commands with the computed canonical project root as their working directory.
Require `git` and GitHub CLI (`gh`). Run `gh auth status`; if authentication is absent,
stop and ask the user to authenticate with `gh auth login`. Never accept a token in a
checkpoint, command argument, committed file, or chat-generated configuration file.

Inspect before staging:

- `git status --short --untracked-files=all`
- ignore rules and untracked filenames
- likely secret files such as `.env`, private keys, credentials, local databases, and
  cloud/service configuration containing tokens
- unexpectedly large generated files or dependency directories
- whether `.project-checkpoint/` is already tracked

This is a safety review, not permission to read and print secret contents. If a likely
secret is tracked or would be staged, stop and identify its path. Do not silently add
ignore rules or remove tracked files. Do not upload until the user resolves it.

Checkpoint files are local recovery metadata, not code. Do not stage
`.project-checkpoint/` during the default publish operation. If it is already tracked,
stop and tell the user; removing it from the index is a separate repository decision.

## Prepare local Git state

If the project is not yet a repository, initialize it with `git init -b main`. Do not
initialize a parent or sibling folder. If Git requires an author identity, stop and ask
the user to configure it; do not invent one.

Stage the intended project files while excluding `.project-checkpoint/`, for example
with `git add -A -- . ':(exclude).project-checkpoint/**'`. Review
`git status --short --untracked-files=all`, then create a normal commit with a concise
message such as `Save project progress`. If there are no changes and a commit already
exists, reuse the current HEAD. If there is no commit and no code to stage, stop. Never
amend, rewrite, reset, or force anything as part of this operation.

## Resolve the private remote

### Existing origin

Read `git remote get-url origin`. Require a GitHub HTTPS or SSH remote and derive its
`OWNER/REPO` slug without embedded credentials. Run:

```text
gh repo view OWNER/REPO --json nameWithOwner,url,visibility,defaultBranchRef
```

Continue only if `visibility` is `PRIVATE`. If it is public/internal, inaccessible, or
points elsewhere, stop. Never change visibility or replace `origin` automatically.

### No origin

Sanitize the project folder name to a valid, readable GitHub repository name. Use:

```text
gh repo create REPO --private --source . --remote origin --push
```

This creates the repository in the authenticated user's account. If that name already
exists or ownership is ambiguous, stop and ask for an explicit repository name; do not
attach to the existing repository automatically.

## Push and verify

When an existing private origin is valid, push the current branch normally, using
`git push -u origin <branch>` only when no upstream exists and `git push` otherwise.
Never use `--force` or `--force-with-lease`.

After pushing, verify:

1. `git status --short --branch` shows no unexpected staged or uncommitted files. The
   intentionally untracked `.project-checkpoint/` directory may remain.
2. `git rev-parse HEAD` matches the pushed branch's remote commit.
3. `gh repo view OWNER/REPO --json url,visibility` still reports `PRIVATE`.

Return the repository URL, branch, and commit SHA. Clearly report any files deliberately
left uncommitted and the reason.
