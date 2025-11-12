#!/bin/bash

echo "========================================"
echo "Push to GitHub Repository"
echo "========================================"
echo ""
echo "Repository: https://github.com/Gabriel-Kelvin/multiagent_mcp.git"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    git remote add origin https://github.com/Gabriel-Kelvin/multiagent_mcp.git
    echo ""
fi

# Check git status
echo "Checking repository status..."
git status
echo ""

# Ask for confirmation
read -p "Do you want to commit and push all changes? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Adding all files..."
git add .

echo ""
read -p "Enter commit message (or press Enter for default): " COMMIT_MSG
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Update: Multi-Agent Data Assistant with MCP - Docker deployment ready"
fi

echo ""
echo "Committing with message: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

echo ""
echo "Pushing to GitHub..."
echo "You will be prompted for your credentials:"
echo "  Username: Gabriel-Kelvin"
echo "  Password: [Your Personal Access Token]"
echo ""

git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Success! Code uploaded to GitHub"
    echo "========================================"
    echo ""
    echo "Repository URL: https://github.com/Gabriel-Kelvin/multiagent_mcp"
    echo ""
    echo "Next steps:"
    echo "1. Verify files on GitHub"
    echo "2. Follow QUICKSTART_VM.md to deploy on your VM"
    echo ""
else
    echo ""
    echo "========================================"
    echo "Error occurred during push"
    echo "========================================"
    echo ""
    echo "Common fixes:"
    echo "1. Check your Personal Access Token"
    echo "2. Ensure you have write access to the repository"
    echo "3. Check internet connection"
    echo ""
    echo "See GITHUB_UPLOAD_GUIDE.md for detailed help"
    echo ""
fi

