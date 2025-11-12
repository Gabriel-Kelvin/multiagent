# 🎯 START HERE - Complete Deployment Guide

## Welcome! You're About to Deploy Your MCP-Powered Multi-Agent Assistant

This guide will take you from **code on your local machine** to **running application on VM 18.142.146.189** in about **15 minutes**.

---

## 📍 Current Status

You have:
✅ Application code ready  
✅ MCP integration working locally  
✅ Docker files configured for VM deployment  
✅ Documentation prepared  

---

## 🗺️ Deployment Roadmap

```
Step 1: Push to GitHub (5 min)
    ↓
Step 2: Setup VM (One-time, 5 min)
    ↓
Step 3: Deploy Application (5 min)
    ↓
Step 4: Test & Verify
    ↓
🎉 DONE!
```

---

## 📝 STEP 1: Push Code to GitHub (5 minutes)

### Option A: Use the Automated Script (Easiest)

**Windows**:
```bash
push_to_github.bat
```

**Linux/Mac**:
```bash
chmod +x push_to_github.sh
./push_to_github.sh
```

### Option B: Manual Commands

```bash
# Initialize git (if not done)
git init
git remote add origin https://github.com/Gabriel-Kelvin/multiagent_mcp.git

# Add and commit files
git add .
git commit -m "Initial commit: Multi-Agent Data Assistant with MCP"

# Push to GitHub
git branch -M main
git push -u origin main
```

**When prompted**:
- Username: `Gabriel-Kelvin`
- Password: `[Your GitHub Personal Access Token]`

📖 **Need help?** See [GITHUB_UPLOAD_GUIDE.md](GITHUB_UPLOAD_GUIDE.md)

### ✅ Verify Upload

Visit: https://github.com/Gabriel-Kelvin/multiagent_mcp

You should see all your files!

---

## 🖥️ STEP 2: Setup VM (One-Time, 5 minutes)

**Connect to your VM**:
```bash
ssh your-user@18.142.146.189
```

**Run these commands** (copy-paste all at once):

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt-get install git -y

# Open firewall ports
sudo ufw allow 8017/tcp
sudo ufw allow 8018/tcp

# Verify installations
docker --version
docker-compose --version
git --version

echo "✅ VM setup complete! Log out and back in."
```

**Log out and back in** for Docker permissions:
```bash
exit
ssh your-user@18.142.146.189
```

---

## 🚀 STEP 3: Deploy Application (5 minutes)

**On your VM**, run:

```bash
# Clone repository
git clone https://github.com/Gabriel-Kelvin/multiagent_mcp.git
cd multiagent_mcp

# Copy environment templates
cp env.example .env
cp frontend/env.example frontend/.env

# Edit backend .env
nano .env
```

**Update these required fields in .env**:
```env
OPENAI_API_KEY=your_actual_key_here
SENDGRID_API_KEY=your_actual_key_here
SUPABASE_URL=https://your-actual-project.supabase.co
SUPABASE_ANON_KEY=your_actual_key_here
SUPABASE_POOLER_DSN=postgresql://your_actual_connection
DATA_DSN=postgresql://your_actual_data_connection
DATA_TABLE=your_actual_table_name
```

Save with `Ctrl+O`, `Enter`, `Ctrl+X`

**Edit frontend .env**:
```bash
nano frontend/.env
```

**Update these fields**:
```env
VITE_SUPABASE_URL=https://your-actual-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_actual_key_here
```

Save with `Ctrl+O`, `Enter`, `Ctrl+X`

**Deploy**:
```bash
docker-compose up -d --build
```

This will:
- Build backend Docker image (2-3 min)
- Build frontend Docker image (1-2 min)
- Start both containers
- Initialize MCP servers

---

## ✅ STEP 4: Test & Verify

**Check if containers are running**:
```bash
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE                  STATUS         PORTS
xxxxxxxxx      multiagent-backend     Up 2 minutes   0.0.0.0:8017->8017/tcp
yyyyyyyyy      multiagent-frontend    Up 2 minutes   0.0.0.0:8018->8018/tcp
```

**Check backend health**:
```bash
curl http://localhost:8017/health
```

Expected: `{"status":"ok"}`

**Check backend logs**:
```bash
docker logs multiagent-backend | grep MCP
```

Expected:
```
[MCP] DB server started successfully
[MCP] Email server started successfully
```

**Access the application**:

Open in your browser:
- **Frontend**: http://18.142.146.189:8018
- **API Docs**: http://18.142.146.189:8017/docs

---

## 🎉 SUCCESS!

Your application is now live at:
### **http://18.142.146.189:8018**

---

## 📚 What's Next?

### Use the Application
1. Open http://18.142.146.189:8018
2. Enter your database connection details in the UI
3. Ask questions like "Show me all data"
4. View results, download CSV/PDF reports

### Monitor the Application
```bash
# View logs
docker-compose logs -f

# Check resource usage
docker stats

# View application logs
curl http://18.142.146.189:8017/logs?limit=20
```

### Manage the Application
```bash
# Restart services
docker-compose restart

# Stop services
docker-compose down

# Update and restart
git pull && docker-compose up -d --build
```

---

## 🐛 Troubleshooting

### Can't access from browser?

```bash
# 1. Check containers are running
docker ps

# 2. Check backend health
curl http://localhost:8017/health

# 3. Check firewall
sudo ufw status

# 4. Check logs
docker-compose logs
```

### MCP servers not starting?

```bash
# Check backend logs
docker logs multiagent-backend --tail 50

# Look for MCP initialization messages
```

### Database connection issues?

```bash
# Verify your DATA_DSN in .env
cat .env | grep DATA_DSN

# Test connection
docker exec -it multiagent-backend python -c "from app.config import settings; from utils import db_utils; print(db_utils.connect(settings))"
```

📖 **Full troubleshooting**: [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting)

---

## 📖 Additional Documentation

| Document | When to Use |
|----------|-------------|
| [QUICKSTART_VM.md](QUICKSTART_VM.md) | Quick reference for VM deployment |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Detailed deployment guide with all options |
| [GITHUB_UPLOAD_GUIDE.md](GITHUB_UPLOAD_GUIDE.md) | GitHub upload troubleshooting |
| [MCP_INTEGRATION.md](MCP_INTEGRATION.md) | Understanding MCP features |
| [TESTING_MCP.md](TESTING_MCP.md) | Testing MCP functionality |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture details |

---

## 🆘 Need Help?

1. **Check logs**: `docker-compose logs -f`
2. **Review documentation** in this repository
3. **Check GitHub issues**: https://github.com/Gabriel-Kelvin/multiagent_mcp/issues

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub successfully
- [ ] VM has Docker & Docker Compose installed
- [ ] Repository cloned on VM
- [ ] `.env` files configured with real credentials
- [ ] Firewall ports 8017 & 8018 open
- [ ] Containers built and running (`docker ps`)
- [ ] Backend health check returns OK
- [ ] Frontend loads in browser
- [ ] MCP servers initialized (check logs)
- [ ] Can submit test queries

---

## 🎯 Quick Command Reference

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Restart
docker-compose restart

# Update
git pull && docker-compose up -d --build

# Health check
curl http://18.142.146.189:8017/health
```

---

## 🚀 You're Ready!

Follow the steps above and you'll have your MCP-powered multi-agent assistant running on your VM in about 15 minutes!

**Any questions?** Check the documentation or review the logs for details.

**Good luck! 🎉**

