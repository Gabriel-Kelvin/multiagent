# 📤 GitHub Upload Guide

## Step-by-Step Instructions to Upload to GitHub

### Prerequisites

1. **GitHub Account**: You already have one (Gabriel-Kelvin)
2. **Git Installed**: Check with `git --version`
3. **GitHub Personal Access Token** (for authentication)

---

## 🔑 Step 1: Create GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token" → "Generate new token (classic)"**
3. Settings:
   - **Note**: "multiagent_mcp_deployment"
   - **Expiration**: 90 days (or your preference)
   - **Scopes**: Check `repo` (full control)
4. Click **"Generate token"**
5. **COPY THE TOKEN** - you won't see it again!

---

## 📂 Step 2: Prepare Local Repository

```bash
# Navigate to your project directory
cd D:\VEXABOT\Cursor\multiagent\db_multiagent

# Initialize git (if not already done)
git init

# Check current status
git status
```

---

## 🔐 Step 3: Configure Git (If First Time)

```bash
# Set your name and email
git config --global user.name "Gabriel-Kelvin"
git config --global user.email "your-email@example.com"

# Verify
git config --global --list
```

---

## 📝 Step 4: Add Remote Repository

```bash
# Add the GitHub repository as remote
git remote add origin https://github.com/Gabriel-Kelvin/multiagent_mcp.git

# Verify
git remote -v
```

---

## 📦 Step 5: Stage and Commit Files

```bash
# Add all files (respecting .gitignore)
git add .

# Check what will be committed
git status

# Commit with message
git commit -m "Initial commit: Multi-Agent Data Assistant with MCP integration"
```

---

## ⬆️ Step 6: Push to GitHub

```bash
# Push to main branch
git push -u origin main

# When prompted for credentials:
# Username: Gabriel-Kelvin
# Password: <paste your personal access token>
```

**Note**: If the branch is `master` instead of `main`:
```bash
git push -u origin master
```

Or rename to main first:
```bash
git branch -M main
git push -u origin main
```

---

## ✅ Step 7: Verify Upload

1. Go to: https://github.com/Gabriel-Kelvin/multiagent_mcp
2. Refresh the page
3. You should see all your files!

---

## 🔄 Alternative Method: Using PowerShell (Windows)

```powershell
# Navigate to project
cd D:\VEXABOT\Cursor\multiagent\db_multiagent

# Initialize and add files
git init
git add .
git commit -m "Initial commit: Multi-Agent Data Assistant with MCP integration"

# Add remote
git remote add origin https://github.com/Gabriel-Kelvin/multiagent_mcp.git

# Push
git push -u origin main
```

---

## 🚨 Troubleshooting

### Error: "Repository not found"

```bash
# Check remote URL
git remote -v

# If wrong, update it:
git remote set-url origin https://github.com/Gabriel-Kelvin/multiagent_mcp.git
```

### Error: "Authentication failed"

- Make sure you're using your **Personal Access Token** as password, not your GitHub password
- Token must have `repo` scope
- Try: `git config --global credential.helper store`

### Error: "Updates were rejected"

```bash
# Pull first, then push
git pull origin main --rebase
git push origin main
```

### Error: "Large files"

GitHub has a 100MB file limit. If you have large files:

```bash
# Check file sizes
find . -type f -size +50M

# Remove large files from tracking
git rm --cached path/to/large/file

# Add to .gitignore
echo "path/to/large/file" >> .gitignore

# Commit and push again
git add .gitignore
git commit -m "Remove large files"
git push origin main
```

---

## 📋 What Files Will Be Uploaded?

✅ **Included:**
- All Python source code (`.py`)
- Frontend source code (`frontend/src/**`)
- Docker configuration files
- Documentation files (`.md`)
- Configuration templates (`env.example`)
- Package files (`requirements.txt`, `package.json`)

❌ **Excluded (by .gitignore):**
- `node_modules/`
- `venv/`
- `.env` files (secrets)
- `__pycache__/`
- `logs/`
- `artifacts/`
- IDE settings (`.vscode`, `.idea`)

---

## 🔒 Security Checklist

Before pushing, ensure:

- [ ] No `.env` files are committed (check `.gitignore`)
- [ ] No API keys in code
- [ ] No passwords in code
- [ ] No sensitive data in logs

```bash
# Double-check what's being pushed
git diff --staged

# Check for sensitive data
git log --all --full-history -- "*env*"
```

---

## 🎯 Quick Command Summary

```bash
# One-time setup
git init
git remote add origin https://github.com/Gabriel-Kelvin/multiagent_mcp.git

# Regular workflow
git add .
git commit -m "Your commit message"
git push origin main

# Update from GitHub
git pull origin main
```

---

## 📝 After First Push

For future updates:

```bash
# Make your changes...

# Stage changes
git add .

# Commit
git commit -m "Describe your changes"

# Push
git push

# Or all in one:
git add . && git commit -m "Update: description" && git push
```

---

## ✅ Verification Steps

1. **Check GitHub**: https://github.com/Gabriel-Kelvin/multiagent_mcp
2. **Verify files are there**
3. **Check README is displaying**
4. **Test clone on VM**:

```bash
# On your VM
git clone https://github.com/Gabriel-Kelvin/multiagent_mcp.git
cd multiagent_mcp
ls -la
```

---

## 🎉 Success!

Your repository is now on GitHub and ready to be cloned on your VM!

Next step: Follow [QUICKSTART_VM.md](QUICKSTART_VM.md) to deploy on your VM.

