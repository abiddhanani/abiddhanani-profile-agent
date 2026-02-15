#!/bin/bash
# Push this repo to GitHub. Run from project root.
#
# First time:
# 1. Create a new repo at https://github.com/new named "abiddhanani-profile-agent"
#    (leave "Add README" unchecked so the repo is empty).
# 2. Replace YOUR_GITHUB_USERNAME below with your GitHub username (or set GITHUB_USER).
# 3. Run: chmod +x push_to_github.sh && ./push_to_github.sh

set -e
GITHUB_USER="${GITHUB_USER:-YOUR_GITHUB_USERNAME}"
REPO="abiddhanani-profile-agent"
REMOTE="https://github.com/${GITHUB_USER}/${REPO}.git"

git add .
git commit -m "Initial commit: RAG profile agent with Gradio and HF Spaces deploy" || true
if ! git remote get-url origin 2>/dev/null; then
  git remote add origin "$REMOTE"
fi
git push -u origin main 2>/dev/null || git push -u origin master
echo "Done: https://github.com/${GITHUB_USER}/${REPO}"
