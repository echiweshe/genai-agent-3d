#!/bin/bash

echo "========================================================"
echo "     GenAI Agent 3D - Create Milestone Branch"
echo "========================================================"
echo
echo "This script will:"
echo " 1. Create a milestone branch named 'milestone-v1.0'"
echo " 2. Add all current files to the branch"
echo " 3. Commit the current working state"
echo " 4. Push the milestone branch to the remote repository"
echo
echo "Press Enter to continue or Ctrl+C to cancel..."
read

echo
echo "Step 1: Adding all current files to git..."
git add -A

echo
echo "Step 2: Creating a commit for the current state..."
git commit -m "Milestone v1.0 - First working end-to-end system"

echo
echo "Step 3: Creating milestone branch..."
git branch milestone-v1.0

echo
echo "Step 4: Switching to milestone branch..."
git checkout milestone-v1.0

echo
echo "Step 5: Pushing milestone branch to remote repository..."
git push -u origin milestone-v1.0

echo
echo "Step 6: Switching back to main branch..."
git checkout main

echo
echo "========================================================"
echo "               MILESTONE BRANCH CREATED"
echo "========================================================"
echo "The milestone branch 'milestone-v1.0' has been created and pushed."
echo
echo "To return to this milestone in the future:"
echo "  git checkout milestone-v1.0"
echo
echo "To continue development on main:"
echo "  git checkout main"
echo
echo "If you need to restore this milestone state to main:"
echo "  git checkout main"
echo "  git merge milestone-v1.0"
echo "========================================================"
echo
echo "Press Enter to exit..."
read
