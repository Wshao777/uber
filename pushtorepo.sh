#!/bin/bash

# A simple script to add, commit, and push changes to the main branch.
# Usage: ./pushtorepo.sh "Your commit message"

# Check if a commit message was provided
if [ -z "$1" ]; then
  echo "❌ ERROR: Please provide a commit message."
  echo "Usage: ./pushtorepo.sh \"Your commit message\""
  exit 1
fi

# Add all new and modified files
echo "--- Adding all files to git ---"
git add .

# Commit with the provided message
echo "--- Committing changes ---"
git commit -m "$1"

# Push to the main branch of the origin remote
echo "--- Pushing to origin main ---"
git push -u origin main

echo "✅ Successfully pushed changes to the repository."