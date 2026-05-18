#!/usr/bin/env bash
# ============================================================================
# setup_repo.sh — one-command GitHub publish for Synthetic Archaeology
# ============================================================================
#
# What this does:
#   1. Cleans any half-finished .git/ that may have been left behind
#   2. Re-runs the .env safety checks (nothing with sk-proj gets committed)
#   3. git init → git add → git commit
#   4. Creates a public repo on GitHub (via `gh` CLI) and pushes
#      OR prints the manual instructions if `gh` is not installed
#
# Usage:
#   cd "<the outputs folder>"
#   bash setup_repo.sh                       # interactive (will ask for repo name)
#   bash setup_repo.sh my-repo-name          # use a specific name
#   bash setup_repo.sh my-repo-name --private  # make it private (NOT for this assignment — must be public)
#
# Requires: git (everywhere), optionally `gh` (GitHub CLI) for one-command publish
# ============================================================================

set -e
cd "$(dirname "$0")"

REPO_NAME="${1:-synthetic-archaeology}"
VISIBILITY_FLAG="--public"
if [[ "$*" == *"--private"* ]]; then
    VISIBILITY_FLAG="--private"
    echo "⚠  WARNING: --private specified. The assignment requires the repo to be PUBLIC."
    read -p "    Continue anyway? [y/N] " yn
    [[ "$yn" != "y" && "$yn" != "Y" ]] && exit 1
fi

GREEN="\033[1;32m"; RED="\033[1;31m"; YELLOW="\033[1;33m"; RESET="\033[0m"

# ---- 0. Sanity ----
[ -f sa_utils.py ] || { echo -e "${RED}ERROR: not in the project root (sa_utils.py missing).${RESET}"; exit 1; }
command -v git >/dev/null || { echo -e "${RED}ERROR: git is not installed. Install it via: brew install git${RESET}"; exit 1; }

# ---- 1. Clean any half-finished previous init ----
if [ -d .git ]; then
    if [ -f .git/index.lock ] || [ ! -f .git/HEAD ] || [ ! -d .git/refs ]; then
        echo -e "${YELLOW}Removing incomplete previous .git/ ...${RESET}"
        rm -rf .git
    fi
fi

# ---- 2. Security checks ----
echo -e "${GREEN}=== Security check 1 — .env is gitignored ===${RESET}"
grep -E "^\.env$" .gitignore >/dev/null || { echo -e "${RED}.gitignore is missing the .env line!${RESET}"; exit 1; }
echo "  ✓ .gitignore contains .env"

echo -e "${GREEN}=== Security check 2 — no real-looking API key anywhere except .env ===${RESET}"
# Real OpenAI keys are 'sk-proj-' + 80+ char/digit/dash/underscore. We require
# 30+ key-characters after the dash so the regex does NOT trip on the literal
# substring 'sk-proj' that appears as documentation in this very script and
# in SUBMISSION_CHECKLIST.md. We also exclude those two files explicitly as
# belt-and-braces.
LEAK=$(grep -rlnE "sk-proj-[A-Za-z0-9_-]{30,}" \
       --exclude-dir=.git \
       --exclude=.env \
       --exclude=setup_repo.sh \
       --exclude=SUBMISSION_CHECKLIST.md \
       . 2>/dev/null || true)
if [ -n "$LEAK" ]; then
    echo -e "${RED}REAL-KEY LEAK DETECTED in these files:${RESET}"
    echo "$LEAK"
    echo -e "${RED}Aborting. Remove the leak before continuing.${RESET}"
    exit 1
fi
echo "  ✓ no real-looking API key leaks outside .env"

# ---- 3. git init + commit ----
echo -e "${GREEN}=== git init + first commit ===${RESET}"
[ -d .git ] || git init -q
git branch -M main 2>/dev/null || true

# only set identity if not already configured
if [ -z "$(git config user.email)" ]; then
    read -p "  Your email for git commits: " GIT_EMAIL
    read -p "  Your name for git commits:  " GIT_NAME
    git config user.email "$GIT_EMAIL"
    git config user.name  "$GIT_NAME"
fi

git add -A
N_STAGED=$(git diff --cached --numstat | wc -l | tr -d ' ')
SIZE_MB=$(git ls-files --cached | xargs -I{} du -k "{}" 2>/dev/null | awk '{s+=$1} END{printf "%.1f", s/1024}')
echo "  $N_STAGED files staged, ~${SIZE_MB} MB"

if git diff --cached --name-only | grep -E "^\.env$" >/dev/null; then
    echo -e "${RED}ERROR: .env got staged. Aborting.${RESET}"
    git reset
    exit 1
fi

git commit -q -m "Initial commit — Synthetic Archaeology (BARC0053 25/26)"
echo "  ✓ first commit made"

# ---- 4. Push to GitHub ----
echo -e "${GREEN}=== Publish to GitHub ===${RESET}"
if command -v gh >/dev/null; then
    if ! gh auth status >/dev/null 2>&1; then
        echo "  GitHub CLI not authenticated. Running: gh auth login"
        gh auth login
    fi
    echo "  Creating $VISIBILITY_FLAG repo '$REPO_NAME' and pushing ..."
    gh repo create "$REPO_NAME" $VISIBILITY_FLAG --source=. --push \
        --description "BARC0053 final assignment 25/26 — Synthetic Archaeology"
    REPO_URL=$(gh repo view --json url -q .url)
    echo -e "${GREEN}  ✓ pushed: $REPO_URL${RESET}"
else
    cat <<EOF
${YELLOW}  'gh' CLI not installed. Either install it (brew install gh) and rerun,
   or do these three steps manually:${RESET}

     1. Create a NEW PUBLIC repo on https://github.com/new
        Name it: $REPO_NAME
        Do NOT initialise with README / .gitignore / license.

     2. Copy the URL it gives you, then run here:

        git remote add origin https://github.com/<your-username>/$REPO_NAME.git
        git push -u origin main

     3. Open the repo URL in a browser and visually verify .env is NOT there.
EOF
fi

# ---- 5. Final verification ----
echo -e "${GREEN}=== Final report ===${RESET}"
echo "  staged files     : $N_STAGED"
echo "  commit size      : ~${SIZE_MB} MB"
echo "  branch           : $(git rev-parse --abbrev-ref HEAD)"
echo "  last commit      : $(git log -1 --format='%h %s' 2>/dev/null)"
echo -e "${GREEN}Done.${RESET}"
