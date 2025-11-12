# 🚀 VM Deployment Guide - Multi-Agent Data Assistant with MCP

## Server Information
- **VM IP**: 18.142.146.189
- **Backend Port**: 8017
- **Frontend Port**: 8018

---

## 📋 Prerequisites on VM

### 1. Install Docker & Docker Compose

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version

# Log out and log back in for group changes to take effect
```

### 2. Install Git

```bash
sudo apt-get install git -y
git --version
```

---

## 🔧 Deployment Steps

### Step 1: Clone the Repository

```bash
# Navigate to your deployment directory
cd /home/ubuntu  # or wherever you want to deploy

# Clone the repository
git clone https://github.com/Gabriel-Kelvin/multiagent_mcp.git

# Enter the directory
cd multiagent_mcp
```

### Step 2: Configure Environment Variables

```bash
# Create .env file for backend
cat > .env << 'EOF'
# General
ENV=production
SCHEDULER_TIMEZONE=UTC

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration (SendGrid)
SENDGRID_API_KEY=your_sendgrid_api_key_here
EMAIL_FROM=your_email@example.com
EMAIL_TO=recipient@example.com

# Supabase/PostgreSQL - Internal App Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SUPABASE_POOLER_DSN=postgresql://postgres.xxxxx:password@aws-0-region.pooler.supabase.com:6543/postgres

# External Data Source Configuration
DATA_DB_TYPE=postgres
DATA_DSN=postgresql://user:password@host:port/database
DATA_TABLE=your_table_name

# Application URLs
FRONTEND_URL=http://18.142.146.189:8018
BACKEND_URL=http://18.142.146.189:8017

# Logging
DB_PATH=logs/app.db
LOG_FILE=logs/events.jsonl
EOF

# Create .env file for frontend
cat > frontend/.env << 'EOF'
VITE_API_BASE_URL=http://18.142.146.189:8017
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_APP_URL=http://18.142.146.189:8018
EOF
```

**⚠️ IMPORTANT**: Edit these files with your actual credentials:

```bash
nano .env
nano frontend/.env
```

### Step 3: Open Firewall Ports

```bash
# Allow Docker ports
sudo ufw allow 8017/tcp comment 'Backend API'
sudo ufw allow 8018/tcp comment 'Frontend'

# Check firewall status
sudo ufw status
```

### Step 4: Build and Start the Application

```bash
# Build and start containers
docker-compose up -d --build

# This will:
# 1. Build backend Docker image
# 2. Build frontend Docker image
# 3. Start both containers
# 4. Initialize MCP servers
```

### Step 5: Verify Deployment

```bash
# Check if containers are running
docker ps

# Expected output:
# CONTAINER ID   IMAGE                     STATUS         PORTS
# xxxxxxxxx      multiagent-backend        Up x minutes   0.0.0.0:8017->8017/tcp
# yyyyyyyyy      multiagent-frontend       Up x minutes   0.0.0.0:8018->8018/tcp

# Check backend logs
docker logs multiagent-backend

# Look for:
# [Server] Initializing MCP servers...
# [MCP] DB server started successfully
# [MCP] Email server started successfully
# INFO: Uvicorn running on http://0.0.0.0:8017

# Check frontend logs
docker logs multiagent-frontend

# Test backend health
curl http://localhost:8017/health

# Should return: {"status":"ok"}

# Test from outside the VM
curl http://18.142.146.189:8017/health
```

### Step 6: Access the Application

- **Frontend**: http://18.142.146.189:8018
- **Backend API**: http://18.142.146.189:8017
- **API Docs**: http://18.142.146.189:8017/docs

---

## 🔄 Managing the Application

### View Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker logs multiagent-backend -f
docker logs multiagent-frontend -f

# View last 50 lines
docker logs multiagent-backend --tail 50
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend

# Stop all services
docker-compose stop

# Start all services
docker-compose start
```

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Or just rebuild specific service
docker-compose up -d --build backend
```

### Stop and Remove Everything

```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v

# Remove all images
docker rmi $(docker images -q multiagent*)
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check container status
docker ps -a

# Check logs for errors
docker logs multiagent-backend
docker logs multiagent-frontend

# Check Docker events
docker events

# Inspect container
docker inspect multiagent-backend
```

### Port Already in Use

```bash
# Check what's using the port
sudo lsof -i :8017
sudo lsof -i :8018

# Kill the process if needed
sudo kill -9 <PID>

# Or change ports in docker-compose.yml
```

### Cannot Connect from Browser

1. Check firewall:
```bash
sudo ufw status
```

2. Check if containers are running:
```bash
docker ps
```

3. Check if ports are exposed:
```bash
sudo netstat -tulpn | grep 8017
sudo netstat -tulpn | grep 8018
```

4. Test locally first:
```bash
curl http://localhost:8017/health
curl http://localhost:8018
```

### MCP Servers Not Starting

```bash
# Check backend logs
docker logs multiagent-backend | grep MCP

# Should see:
# [MCP] DB server started successfully
# [MCP] Email server started successfully

# If not, check for errors:
docker logs multiagent-backend --tail 100
```

### Database Connection Issues

```bash
# Enter backend container
docker exec -it multiagent-backend bash

# Test database connection
python -c "from app.config import settings; from utils import db_utils; print(db_utils.connect(settings))"

# Exit container
exit
```

---

## 📊 Monitoring

### Check Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

### Check Application Health

```bash
# Backend health
curl http://18.142.146.189:8017/health

# Check logs
curl http://18.142.146.189:8017/logs?limit=10

# Test a query
curl -X POST http://18.142.146.189:8017/run \
  -H "Content-Type: application/json" \
  -d '{"question":"test query","use_env":true}'
```

---

## 🔒 Security Recommendations

1. **Use HTTPS** (add Nginx reverse proxy with SSL):
```bash
sudo apt install nginx certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

2. **Restrict Access** (optional):
```bash
# Allow only specific IPs
sudo ufw allow from YOUR_IP to any port 8017
sudo ufw allow from YOUR_IP to any port 8018
```

3. **Use Docker Secrets** for sensitive data instead of .env files

4. **Regular Updates**:
```bash
# Update system
sudo apt update && sudo apt upgrade

# Update containers
docker-compose pull
docker-compose up -d
```

---

## 📝 Maintenance

### Backup

```bash
# Backup volumes
docker run --rm -v multiagent_mcp_artifacts:/artifacts -v $(pwd):/backup ubuntu tar czf /backup/artifacts-backup.tar.gz /artifacts

# Backup .env files
tar czf env-backup.tar.gz .env frontend/.env

# Backup logs
tar czf logs-backup.tar.gz logs/
```

### Restore

```bash
# Restore volumes
docker run --rm -v multiagent_mcp_artifacts:/artifacts -v $(pwd):/backup ubuntu tar xzf /backup/artifacts-backup.tar.gz -C /

# Restore .env files
tar xzf env-backup.tar.gz
```

---

## 🎯 Quick Reference

```bash
# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f

# Restart after code changes
git pull && docker-compose up -d --build

# Check health
curl http://18.142.146.189:8017/health
```

---

## 📞 Support

If you encounter issues:

1. Check logs: `docker-compose logs`
2. Check container status: `docker ps -a`
3. Check firewall: `sudo ufw status`
4. Test locally: `curl http://localhost:8017/health`
5. Review error messages in application logs

---

## ✅ Post-Deployment Checklist

- [ ] VM has Docker and Docker Compose installed
- [ ] Repository cloned successfully
- [ ] .env files configured with correct credentials
- [ ] Firewall ports 8017 and 8018 are open
- [ ] Containers are running (`docker ps`)
- [ ] Backend health check returns OK
- [ ] Frontend loads in browser
- [ ] Can submit queries through UI
- [ ] MCP servers initialized successfully
- [ ] Database connections working
- [ ] Email sending configured (optional)

🎉 **Your application is now deployed!**

Access it at: http://18.142.146.189:8018

