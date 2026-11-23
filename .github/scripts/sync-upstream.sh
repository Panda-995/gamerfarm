#!/usr/bin/env bash
set -euo pipefail

upstream_url="${UPSTREAM_URL:-https://github.com/VisaHolder/gamerfarm.git}"
upstream_branch="${UPSTREAM_BRANCH:-main}"
before="$(git rev-parse HEAD)"

# Run only in a clean checkout. Never overwrite a user's uncommitted changes.
git diff --exit-code
git diff --cached --exit-code
git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git fetch --no-tags "$upstream_url" "$upstream_branch"
upstream_revision="$(git rev-parse FETCH_HEAD)"

if ! git merge-base --is-ancestor "$upstream_revision" HEAD; then
  # A translated README intentionally differs from upstream. Resolve only that
  # file in favor of the fork; all application code uses Git's normal merge.
  if ! git merge --no-ff --no-commit "$upstream_revision"; then
    mapfile -t conflicts < <(git diff --name-only --diff-filter=U)
    if [ "${#conflicts[@]}" -eq 0 ]; then
      echo 'Upstream merge failed before a resolvable README conflict.' >&2
      exit 1
    fi
    for path in "${conflicts[@]}"; do
      if [ "$path" != README.md ]; then
        echo "Unresolved upstream conflict: $path. No changes were pushed." >&2
        git merge --abort
        exit 1
      fi
    done
  fi
  git restore --source="$before" --staged --worktree -- README.md
  git show "$upstream_revision:README.md" > README.upstream.md
  git add README.upstream.md
  git commit -m "chore: sync upstream ${upstream_revision:0:12}"
  # A concurrent update must be reconciled by a later run, never force-pushed.
  git push origin HEAD:main
fi

revision="$(git rev-parse HEAD)"
changed=false
if [ "$before" != "$revision" ]; then
  changed=true
fi
if [ -n "${GITHUB_OUTPUT:-}" ]; then
  {
    echo "revision=$revision"
    echo "upstream_revision=$upstream_revision"
    echo "changed=$changed"
  } >> "$GITHUB_OUTPUT"
fi
if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  {
    echo '## Upstream synchronization'
    echo "- Upstream commit: $upstream_revision"
    echo "- Build commit: $revision"
    echo "- Updated: $changed"
    echo '- Chinese README retained; original upstream README saved as README.upstream.md.'
  } >> "$GITHUB_STEP_SUMMARY"
fi
printf 'Upstream: %s\nBuild: %s\nChanged: %s\n' "$upstream_revision" "$revision" "$changed"
