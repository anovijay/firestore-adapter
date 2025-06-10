#!/bin/bash
set -e

# Variables
REPO_DIR=$(basename `pwd`)
BRANCH="main"
COMMIT_MSG=${1:-"🚀 Deploy update"}

echo "📤 Committing and pushing code to GitHub: $REPO_DIR -> branch $BRANCH"

# Git operations
# TODO: Add a check to see if the branch is already up to date
git add .
git commit -m "$COMMIT_MSG"
git push origin "$BRANCH"

echo "✅ Code pushed to GitHub."
echo "🛠 Google Cloud Build will now trigger the deployment automatically."
