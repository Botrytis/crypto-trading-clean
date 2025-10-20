#!/bin/bash
# Quick push script for crypto-analysis-fork

echo "======================================================================"
echo "PUSH CRYPTO TRADING FORK TO GITHUB"
echo "======================================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "DEVELOPMENT_PLAN.md" ]; then
    echo "ERROR: Run this from /home/david/crypto-analysis-fork/"
    exit 1
fi

echo "What's your GitHub username?"
read -p "Username: " GITHUB_USER

echo ""
echo "What do you want to name the repo? (default: crypto-trading-clean)"
read -p "Repo name: " REPO_NAME
REPO_NAME=${REPO_NAME:-crypto-trading-clean}

echo ""
echo "Public or private? (default: public)"
read -p "Visibility (public/private): " VISIBILITY
VISIBILITY=${VISIBILITY:-public}

echo ""
echo "======================================================================"
echo "STEP 1: Create GitHub repo manually"
echo "======================================================================"
echo ""
echo "Go to: https://github.com/new"
echo ""
echo "Settings:"
echo "  - Repository name: $REPO_NAME"
echo "  - Description: Production-ready crypto trading framework - clean fork"
echo "  - Visibility: $VISIBILITY"
echo "  - DO NOT initialize with README/gitignore/license"
echo ""
read -p "Press ENTER when you've created the repo..."

echo ""
echo "======================================================================"
echo "STEP 2: Pushing to GitHub"
echo "======================================================================"
echo ""

# Rename branch to main
git branch -M main

# Add remote
git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git" 2>/dev/null || \
    git remote set-url origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"

# Push
echo "Pushing to https://github.com/$GITHUB_USER/$REPO_NAME..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "SUCCESS!"
    echo "======================================================================"
    echo ""
    echo "Your fork is now live at:"
    echo "https://github.com/$GITHUB_USER/$REPO_NAME"
    echo ""
    echo "Next steps:"
    echo "1. Add topics: cryptocurrency, trading, backtesting, python"
    echo "2. Add description on GitHub"
    echo "3. Start Phase 1 development"
    echo ""
else
    echo ""
    echo "======================================================================"
    echo "PUSH FAILED"
    echo "======================================================================"
    echo ""
    echo "Possible issues:"
    echo "1. Check your GitHub credentials"
    echo "2. Make sure the repo exists"
    echo "3. Try: git config --global credential.helper store"
    echo ""
fi
