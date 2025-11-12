# 🚀 Quick Start - VM Deployment (18.142.146.189)

## One-Command Deploy (After Prerequisites)

```bash
git clone https://github.com/Gabriel-Kelvin/multiagent_mcp.git && \
cd multiagent_mcp && \
cp env.example .env && \
cp frontend/env.example frontend/.env && \
nano .env && \
nano frontend/.env && \
docker-compose up -d --build
```

---

## Step-by-Step (5 Minutes)

### 1️⃣ Prerequisites (One-Time Setup)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt-get install git -y

# Log out and back in
exit
```

### 2️⃣ Clone & Configure

```bash
# Clone repository
git clone https://github.com/Gabriel-Kelvin/multiagent_mcp.git
cd multiagent_mcp

# Copy environment templates
cp env.example .env
cp frontend/env.example frontend/.env

# Edit with your credentials
nano .env
# Update: OPENAI_API_KEY, SENDGRID_API_KEY, SUPABASE credentials, DATA_DSN, DATA_TABLE

nano frontend/.env
# Update: VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY
```

### 3️⃣ Open Firewall Ports

```bash
sudo ufw allow 8017/tcp
sudo ufw allow 8018/tcp
```

### 4️⃣ Deploy

```bash
docker-compose up -d --build
```

### 5️⃣ Verify

```bash
# Wait 30 seconds for services to start, then:
curl http://localhost:8017/health
```

Expected: `{"status":"ok"}`

---

## 🌐 Access Your Application

- **Frontend**: http://18.142.146.189:8018
- **Backend API**: http://18.142.146.189:8017
- **API Docs**: http://18.142.146.189:8017/docs

---

## 📋 Environment Variables You MUST Update

### Backend (.env)
```env
OPENAI_API_KEY=your_key              # Get from OpenAI
SENDGRID_API_KEY=your_key            # Get from SendGrid
EMAIL_FROM=your@email.com
EMAIL_TO=recipient@email.com
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=your_key
SUPABASE_POOLER_DSN=postgresql://...
DATA_DSN=postgresql://...            # Your data database
DATA_TABLE=your_table_name
```

### Frontend (frontend/.env)
```env
VITE_API_BASE_URL=http://18.142.146.189:8017  # Pre-configured
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=your_key
VITE_APP_URL=http://18.142.146.189:8018       # Pre-configured
```

---

## 🔄 Common Commands

```bash
# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down

# Update code and restart
git pull && docker-compose up -d --build

# Check status
docker ps
```

---

## ✅ Success Indicators

When everything is working, you'll see:

```bash
$ docker ps
CONTAINER ID   IMAGE                  STATUS         PORTS
xxxxxxxxx      multiagent-backend     Up 2 minutes   0.0.0.0:8017->8017/tcp
yyyyyyyyy      multiagent-frontend    Up 2 minutes   0.0.0.0:8018->8018/tcp

$ docker logs multiagent-backend | grep MCP
[MCP] DB server started successfully
[MCP] Email server started successfully

$ curl http://localhost:8017/health
{"status":"ok"}
```

---

## 🐛 Quick Troubleshoot

### Can't Access from Browser?
```bash
# Check if containers are running
docker ps

# Check if ports are listening
sudo netstat -tulpn | grep 8017
sudo netstat -tulpn | grep 8018

# Check firewall
sudo ufw status
```

### MCP Not Starting?
```bash
# Check backend logs
docker logs multiagent-backend --tail 50

# Look for errors in MCP initialization
```

### Port Already in Use?
```bash
# Find what's using the port
sudo lsof -i :8017

# Kill it or change ports in docker-compose.yml
```

---

## 📞 Need Help?

Full documentation: [DEPLOYMENT.md](DEPLOYMENT.md)

Check logs: `docker-compose logs -f`

