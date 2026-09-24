#!/usr/bin/env bash

set -euo pipefail

# LOCAL ADDITION (2026-07-21) - HARVEST TO CPB: forge-agnostic atomic horizon ID mint.
# The remote tag namespace is the allocator. This script never scaffolds a packet and never
# pushes more than one explicitly named ref.

REMOTE="origin"
MAX_ATTEMPTS=10
TARGET_REF="HEAD"

show_help() {
  cat <<'EOF'
Usage:
  horizon-mint.sh mint [--remote <name>] [--target-ref <ref>] [--max-attempts <count>]
  horizon-mint.sh abandon <HNNN> --reason <text> [--remote <name>]
  horizon-mint.sh help

Commands:
  mint       Reserve the next production horizon ID with an annotated horizon/HNNN tag.
  abandon    Record an abandoned reservation with horizon/HNNN-abandoned. The original
             reservation remains immutable and the ID is never reused.
  help       Show this help text.

Rules:
  - Production IDs are H000-H899. H900-H999 are reserved for protection probes.
  - The script fetches horizon tags before allocation and retries boundedly on a real race.
  - Every push names exactly one ref. `git push --tags` and forced remote updates are forbidden.
  - Tag messages contain immutable mint facts only; slug, owner, and environment belong in the
    horizon packet.

Output:
  On success, stdout contains only the reserved or abandoned horizon ID. Diagnostics go to
  stderr, so callers may safely capture the result.

Examples:
  horizon-mint.sh mint
  horizon-mint.sh mint --remote upstream --target-ref refs/remotes/upstream/integration --max-attempts 5
  horizon-mint.sh abandon H004 --reason "Planning cycle cancelled before packet declaration"
EOF
}

fail() {
  echo "Error: $1" >&2
  exit 1
}

require_value() {
  local option="$1"
  local value="${2:-}"
  [[ -n "$value" && "$value" != --* ]] || fail "$option requires a value"
}

repo_root() {
  git rev-parse --show-toplevel 2>/dev/null || fail "run this command inside a Git working tree"
}

git_identity() {
  local root="$1"
  local name email
  name="$(git -C "$root" config user.name || true)"
  email="$(git -C "$root" config user.email || true)"
  [[ -n "$name" ]] || fail "git user.name is not configured"
  [[ -n "$email" ]] || fail "git user.email is not configured"
  printf '%s <%s>' "$name" "$email"
}

fetch_horizon_tags() {
  local root="$1"
  git -C "$root" fetch --quiet --no-tags "$REMOTE" \
    'refs/tags/horizon/*:refs/tags/horizon/*' || fail "cannot fetch horizon tags from remote '$REMOTE'"
}

next_horizon_id() {
  local root="$1"
  local refs ref suffix value max=-1
  refs="$(git -C "$root" ls-remote --tags --refs "$REMOTE" 'refs/tags/horizon/H???' \
    | awk '{print $2}')" || fail "cannot enumerate horizon tags on remote '$REMOTE'"
  while IFS= read -r ref; do
    suffix="${ref#refs/tags/horizon/H}"
    [[ "$suffix" =~ ^[0-9]{3}$ ]] || continue
    value=$((10#$suffix))
    (( value <= 899 )) || continue
    (( value > max )) && max=$value
  done <<< "$refs"

  (( max < 899 )) || fail "production horizon ID space H000-H899 is exhausted"
  printf 'H%03d' $((max + 1))
}

remote_ref_exists() {
  local root="$1"
  local ref="$2"
  git -C "$root" ls-remote --exit-code --refs "$REMOTE" "$ref" >/dev/null 2>&1
}

delete_local_proposal() {
  local root="$1"
  local tag="$2"
  git -C "$root" tag --delete "$tag" >/dev/null 2>&1 || true
}

mint_message() {
  local horizon="$1"
  local identity="$2"
  local minted_at="$3"
  cat <<EOF
cpb-horizon-mint-v1
horizon: $horizon
minter: $identity
minted-at: $minted_at
reserved-ref: refs/tags/horizon/$horizon
EOF
}

abandonment_message() {
  local horizon="$1"
  local identity="$2"
  local abandoned_at="$3"
  local reason="$4"
  cat <<EOF
cpb-horizon-abandonment-v1
horizon: $horizon
recorded-by: $identity
abandoned-at: $abandoned_at
reserved-ref: refs/tags/horizon/$horizon
reason: $reason
EOF
}

mint() {
  local root identity attempt horizon tag ref minted_at target_sha
  root="$(repo_root)"
  git -C "$root" remote get-url "$REMOTE" >/dev/null 2>&1 || fail "Git remote '$REMOTE' does not exist"
  identity="$(git_identity "$root")"
  target_sha="$(git -C "$root" rev-parse "$TARGET_REF" 2>/dev/null)" || fail "target ref '$TARGET_REF' does not resolve"

  for ((attempt = 1; attempt <= MAX_ATTEMPTS; attempt++)); do
    fetch_horizon_tags "$root"
    horizon="$(next_horizon_id "$root")"
    tag="horizon/$horizon"
    ref="refs/tags/$tag"
    minted_at="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

    git -C "$root" tag -a "$tag" -m "$(mint_message "$horizon" "$identity" "$minted_at")" "$target_sha" \
      || fail "cannot create local annotated proposal $tag"

    if git -C "$root" push --quiet "$REMOTE" "$ref:$ref"; then
      printf '%s\n' "$horizon"
      return 0
    fi

    if remote_ref_exists "$root" "$ref"; then
      echo "Collision: $tag was reserved by another operator; retrying ($attempt/$MAX_ATTEMPTS)." >&2
      delete_local_proposal "$root" "$tag"
      continue
    fi

    delete_local_proposal "$root" "$tag"
    fail "push of $tag failed and the ref does not exist remotely; refusing to report success"
  done

  fail "unable to reserve a horizon ID after $MAX_ATTEMPTS attempts"
}

abandon() {
  local horizon="$1"
  local reason="$2"
  local root identity original_tag original_ref abandoned_tag abandoned_ref abandoned_at target
  [[ "$horizon" =~ ^H[0-8][0-9]{2}$ ]] || fail "abandon requires a production horizon ID H000-H899"
  [[ -n "$reason" ]] || fail "--reason must not be empty"
  [[ "$reason" != *$'\n'* && "$reason" != *$'\r'* ]] || fail "--reason must be a single line"

  root="$(repo_root)"
  git -C "$root" remote get-url "$REMOTE" >/dev/null 2>&1 || fail "Git remote '$REMOTE' does not exist"
  identity="$(git_identity "$root")"
  original_tag="horizon/$horizon"
  original_ref="refs/tags/$original_tag"
  abandoned_tag="$original_tag-abandoned"
  abandoned_ref="refs/tags/$abandoned_tag"

  remote_ref_exists "$root" "$original_ref" || fail "$original_tag does not exist on remote '$REMOTE'"
  if remote_ref_exists "$root" "$abandoned_ref"; then
    fail "$abandoned_tag already exists on remote '$REMOTE'"
  fi

  git -C "$root" fetch --quiet --no-tags "$REMOTE" "$original_ref:$original_ref" \
    || fail "cannot fetch $original_tag from remote '$REMOTE'"
  target="$(git -C "$root" rev-parse "$original_ref^{}")"
  abandoned_at="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
  git -C "$root" tag -a "$abandoned_tag" \
    -m "$(abandonment_message "$horizon" "$identity" "$abandoned_at" "$reason")" "$target" \
    || fail "cannot create local abandonment record $abandoned_tag"

  if ! git -C "$root" push --quiet "$REMOTE" "$abandoned_ref:$abandoned_ref"; then
    delete_local_proposal "$root" "$abandoned_tag"
    fail "push of $abandoned_tag failed; refusing to report success"
  fi

  printf '%s\n' "$horizon"
}

COMMAND="${1:-help}"
shift || true

case "$COMMAND" in
  help|--help|-h)
    [[ $# -eq 0 ]] || fail "help does not accept arguments"
    show_help
    ;;
  mint)
    while (( $# > 0 )); do
      case "$1" in
        --remote)
          require_value "$1" "${2:-}"
          REMOTE="$2"
          shift 2
          ;;
        --max-attempts)
          require_value "$1" "${2:-}"
          [[ "$2" =~ ^[1-9][0-9]*$ ]] || fail "--max-attempts must be a positive integer"
          MAX_ATTEMPTS="$2"
          shift 2
          ;;
        --target-ref)
          require_value "$1" "${2:-}"
          TARGET_REF="$2"
          shift 2
          ;;
        --help|-h)
          show_help
          exit 0
          ;;
        *) fail "unknown mint option: $1" ;;
      esac
    done
    mint
    ;;
  abandon)
    HORIZON="${1:-}"
    [[ -n "$HORIZON" ]] || fail "abandon requires HNNN"
    shift
    REASON=""
    while (( $# > 0 )); do
      case "$1" in
        --reason)
          require_value "$1" "${2:-}"
          REASON="$2"
          shift 2
          ;;
        --remote)
          require_value "$1" "${2:-}"
          REMOTE="$2"
          shift 2
          ;;
        --help|-h)
          show_help
          exit 0
          ;;
        *) fail "unknown abandon option: $1" ;;
      esac
    done
    [[ -n "$REASON" ]] || fail "abandon requires --reason <text>"
    abandon "$HORIZON" "$REASON"
    ;;
  *) fail "unknown command: $COMMAND (use 'help')" ;;
esac