# 🎯 FINAL INSTRUCTIONS - Deploy to VM 18.142.146.189

## ✅ What's Been Done

I've prepared your application for deployment with:

1. **✅ Docker Configuration Updated**
   - Backend: Port 8017
   - Frontend: Port 8018
   - Configured for VM IP: 18.142.146.189

2. **✅ Documentation Created**
   - Complete deployment guides
   - GitHub upload instructions
   - Troubleshooting guides
   - Quick start guides

3. **✅ Helper Scripts**
   - Automated GitHub push scripts
   - Docker configuration ready

4. **✅ Security Files**
   - .gitignore (protects sensitive data)
   - .dockerignore (optimizes builds)

---

## 📋 YOUR ACTION ITEMS

### STEP 1: Push to GitHub (Do This First!)

**On Windows (Your Current Machine)**:

```powershell
# Option A: Use the automated script (easiest)
.\push_to_github.bat

# Option B: Manual commands
git init
git remote add origin https://github.com/Gabriel-Kelvin/multiagent_mcp.git
git add .
git commit -m "Initial commit: Multi-Agent MCP App - Production Ready"
git branch -M main
git push -u origin main
```

**You'll need**:
- Username: `Gabriel-Kelvin`
- Password: Your GitHub **Personal Access Token** (not your GitHub password!)

**Don't have a token?**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Check "repo" scope
4. Generate and copy the token

### STEP 2: Deploy on VM

**SSH into your VM**:
```bash
ssh your-username@18.142.146.189
```

**Run the deployment commands**:

```bash
# Install prerequisites (one-time)
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo apt-get install git -y

# Open firewall
sudo ufw allow 8017/tcp
sudo ufw allow 8018/tcp

# Log out and back in for Docker permissions
exit
```

**SSH back in and clone**:
```bash
ssh your-username@18.142.146.189
git clone https://github.com/Gabriel-Kelvin/multiagent_mcp.git
cd multiagent_mcp
```

**Configure environment**:
```bash
# Copy templates
cp env.example .env
cp frontend/env.example frontend/.env

# Edit backend config
nano .env
# Update: OPENAI_API_KEY, SENDGRID_API_KEY, SUPABASE_URL, SUPABASE_ANON_KEY, 
#         SUPABASE_POOLER_DSN, DATA_DSN, DATA_TABLE
# Save: Ctrl+O, Enter, Ctrl+X

# Edit frontend config
nano frontend/.env
# Update: VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY
# Save: Ctrl+O, Enter, Ctrl+X
```

**Deploy**:
```bash
docker-compose up -d --build
```

**Verify**:
```bash
# Check containers
docker ps

# Check health
curl http://localhost:8017/health

# Check logs
docker logs multiagent-backend | grep MCP
```

### STEP 3: Access Your Application

Open in browser:
- **Frontend**: http://18.142.146.189:8018
- **API Docs**: http://18.142.146.189:8017/docs

---

## 📚 Documentation Quick Links

**Start with**:
- [START_HERE.md](START_HERE.md) - Complete walkthrough

**Need help with**:
- GitHub upload → [GITHUB_UPLOAD_GUIDE.md](GITHUB_UPLOAD_GUIDE.md)
- VM deployment → [QUICKSTART_VM.md](QUICKSTART_VM.md)
- Troubleshooting → [DEPLOYMENT.md](DEPLOYMENT.md)
- Understanding MCP → [MCP_INTEGRATION.md](MCP_INTEGRATION.md)

---

## 🎯 Key Configuration Files

### Backend (.env) - MUST UPDATE THESE:
```env
OPENAI_API_KEY=your_actual_key           # Get from OpenAI
SENDGRID_API_KEY=your_actual_key         # Get from SendGrid
SUPABASE_URL=https://xxx.supabase.co     # Your Supabase project
SUPABASE_ANON_KEY=your_key               # From Supabase settings
SUPABASE_POOLER_DSN=postgresql://...     # From Supabase settings
DATA_DSN=postgresql://...                # Your data database
DATA_TABLE=employee_survey_data          # Your table name
```

### Frontend (frontend/.env) - MUST UPDATE THESE:
```env
VITE_API_BASE_URL=http://18.142.146.189:8017   # Already set!
VITE_SUPABASE_URL=https://xxx.supabase.co      # Same as backend
VITE_SUPABASE_ANON_KEY=your_key                # Same as backend
VITE_APP_URL=http://18.142.146.189:8018       # Already set!
```

---

## ✅ Success Checklist

### After Pushing to GitHub:
- [ ] Visit https://github.com/Gabriel-Kelvin/multiagent_mcp
- [ ] Verify all files are there
- [ ] Check README is visible

### After VM Deployment:
- [ ] `docker ps` shows 2 containers running
- [ ] `curl http://localhost:8017/health` returns `{"status":"ok"}`
- [ ] `docker logs multiagent-backend | grep MCP` shows success messages
- [ ] Browser loads http://18.142.146.189:8018
- [ ] Can submit a test query in the UI

---

## 🚨 Common Issues & Quick Fixes

### Issue: "Push rejected" or "Authentication failed"
**Fix**: Make sure you're using your **Personal Access Token** as password, not your GitHub password.

### Issue: "Can't access from browser"
**Fix**: 
```bash
# Check firewall
sudo ufw status

# Make sure ports are open
sudo ufw allow 8017/tcp
sudo ufw allow 8018/tcp
```

### Issue: "MCP servers not starting"
**Fix**: 
```bash
# Check logs for errors
docker logs multiagent-backend --tail 50
```

### Issue: "Database connection failed"
**Fix**: Double-check your `DATA_DSN` in `.env` file matches your Supabase connection string.

---

## 📞 Need Help?

1. **Check the logs**: `docker-compose logs -f`
2. **Review**: [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
3. **Verify configuration**: Check your `.env` files

---

## 🎉 You're Ready!

**Next Steps**:
1. Run `.\push_to_github.bat` on Windows
2. Follow [START_HERE.md](START_HERE.md) for deployment
3. Access your app at http://18.142.146.189:8018

**Good luck! 🚀**

