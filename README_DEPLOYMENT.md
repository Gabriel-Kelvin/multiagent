# 🚀 Multi-Agent Data Assistant with MCP - Deployment Edition

## 📦 What's Included

This is a **production-ready** version of the Multi-Agent Data Assistant with full MCP (Model Context Protocol) integration, configured for deployment on VM **18.142.146.189**.

### Key Features
✅ **MCP Integration** - Database queries and email sending through MCP servers  
✅ **Docker Support** - Fully containerized backend and frontend  
✅ **Production Ready** - Configured for ports 8017 (backend) & 8018 (frontend)  
✅ **Auto-scaling** - Docker Compose orchestration  
✅ **Health Checks** - Built-in monitoring  

---

## 🎯 Quick Start Options

### Option 1: Deploy to VM (Recommended)
**For deployment to 18.142.146.189**

📖 **Follow**: [QUICKSTART_VM.md](QUICKSTART_VM.md) (5 minutes)

```bash
git clone https://github.com/Gabriel-Kelvin/multiagent_mcp.git
cd multiagent_mcp
# Configure .env files
docker-compose up -d --build
```

### Option 2: Local Development
**For running on your local machine**

📖 **Follow**: [README.md](README.md)

```bash
git clone https://github.com/Gabriel-Kelvin/multiagent_mcp.git
cd multiagent_mcp
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8017 --reload
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [QUICKSTART_VM.md](QUICKSTART_VM.md) | **Start here** - 5-minute VM deployment guide |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Complete deployment guide with troubleshooting |
| [GITHUB_UPLOAD_GUIDE.md](GITHUB_UPLOAD_GUIDE.md) | How to upload code to GitHub |
| [MCP_INTEGRATION.md](MCP_INTEGRATION.md) | Understanding MCP integration |
| [TESTING_MCP.md](TESTING_MCP.md) | Testing MCP functionality |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture details |
| [README.md](README.md) | General application overview |

---

## 🔧 Configuration

### Required Environment Variables

#### Backend (`.env`)
```env
# Essential
OPENAI_API_KEY=sk-...
SENDGRID_API_KEY=SG....
SUPABASE_POOLER_DSN=postgresql://...
DATA_DSN=postgresql://...
DATA_TABLE=your_table_name

# Endpoints
FRONTEND_URL=http://18.142.146.189:8018
BACKEND_URL=http://18.142.146.189:8017
```

#### Frontend (`frontend/.env`)
```env
VITE_API_BASE_URL=http://18.142.146.189:8017
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_key
```

📝 **Copy from templates**:
```bash
cp env.example .env
cp frontend/env.example frontend/.env
```

---

## 🌐 Access Points (After Deployment)

- **Frontend UI**: http://18.142.146.189:8018
- **Backend API**: http://18.142.146.189:8017
- **API Documentation**: http://18.142.146.189:8017/docs
- **Health Check**: http://18.142.146.189:8017/health

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Docker & Docker Compose installed on VM
- [ ] Git installed on VM  
- [ ] Ports 8017 & 8018 open in firewall
- [ ] Supabase project created
- [ ] SendGrid account set up (optional)
- [ ] OpenAI API key obtained (optional)

### Deployment
- [ ] Repository cloned to VM
- [ ] `.env` files configured
- [ ] `docker-compose up -d --build` executed
- [ ] Containers running (`docker ps`)
- [ ] Health check returns OK

### Post-Deployment
- [ ] Frontend accessible in browser
- [ ] Can log in (if auth configured)
- [ ] Can submit test query
- [ ] MCP servers initialized (check logs)
- [ ] Database connection works
- [ ] Email sending works (if configured)

---

## 🐳 Docker Commands Reference

```bash
# Start everything
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Restart services
docker-compose restart

# View running containers
docker ps

# Check resource usage
docker stats
```

---

## 🔍 Troubleshooting

### Can't access from browser?
```bash
# Check containers are running
docker ps

# Check logs
docker logs multiagent-backend
docker logs multiagent-frontend

# Check firewall
sudo ufw status

# Test locally first
curl http://localhost:8017/health
```

### MCP servers not starting?
```bash
# Check backend logs for MCP initialization
docker logs multiagent-backend | grep MCP

# Should see:
# [MCP] DB server started successfully
# [MCP] Email server started successfully
```

### Database connection issues?
```bash
# Verify DATA_DSN in .env
# Test connection:
docker exec -it multiagent-backend python -c "from app.config import settings; from utils import db_utils; print(db_utils.connect(settings))"
```

📖 **Full troubleshooting guide**: [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│  Browser (http://18.142.146.189:8018)      │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Frontend Container (Port 8018)             │
│  - React + Vite                             │
│  - Nginx                                    │
└────────────────┬────────────────────────────┘
                 │ HTTP API Calls
                 ▼
┌─────────────────────────────────────────────┐
│  Backend Container (Port 8017)              │
│  ┌─────────────────────────────────────┐   │
│  │  FastAPI Server                     │   │
│  │  ↓                                   │   │
│  │  LangGraph Multi-Agent System       │   │
│  │  ↓                                   │   │
│  │  MCP Client Manager                 │   │
│  │  ├─→ DB MCP Server                  │   │
│  │  └─→ Email MCP Server               │   │
│  └─────────────────────────────────────┘   │
└────────────────┬────────────────────────────┘
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
┌──────────┐         ┌──────────┐
│ Supabase │         │ SendGrid │
│ Database │         │ Email    │
└──────────┘         └──────────┘
```

---

## 🔐 Security Notes

- `.env` files are **not** committed to Git (see `.gitignore`)
- Use **strong passwords** for database connections
- Consider adding **HTTPS** with SSL certificate
- Restrict **firewall** to specific IPs if needed
- Use **Docker secrets** for production deployments

---

## 📊 Monitoring

```bash
# Container health
docker ps

# Resource usage
docker stats

# Application logs
docker-compose logs -f

# Application health endpoint
curl http://18.142.146.189:8017/health

# View application logs via API
curl http://18.142.146.189:8017/logs?limit=20
```

---

## 🔄 Updates & Maintenance

### Update Application Code
```bash
cd /path/to/multiagent_mcp
git pull origin main
docker-compose up -d --build
```

### Backup
```bash
# Backup artifacts and logs
tar czf backup-$(date +%Y%m%d).tar.gz artifacts/ logs/

# Backup .env files (store securely!)
tar czf env-backup.tar.gz .env frontend/.env
```

### Clean Up
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune
```

---

## 🆘 Support & Documentation

- **GitHub Repository**: https://github.com/Gabriel-Kelvin/multiagent_mcp
- **Issues**: https://github.com/Gabriel-Kelvin/multiagent_mcp/issues
- **MCP Documentation**: https://modelcontextprotocol.io/

---

## 📜 License

[Your License Here]

---

## 🙏 Acknowledgments

- **MCP Protocol**: Model Context Protocol by Anthropic
- **LangGraph**: Multi-agent framework by LangChain
- **FastAPI**: Modern Python web framework
- **React**: Frontend UI library

---

## ✅ Ready to Deploy?

1. **Read**: [QUICKSTART_VM.md](QUICKSTART_VM.md)
2. **Deploy**: Follow the 5-minute guide
3. **Test**: Access http://18.142.146.189:8018
4. **Enjoy**: Your MCP-powered multi-agent assistant!

🚀 **Let's go!**

