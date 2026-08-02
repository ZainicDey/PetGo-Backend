# 🚀 PetGo Backend Deployment Guide & Diagrams

This guide covers all production deployment strategies for the **PetGo Django Backend**, including complete system architecture diagrams, pre-deployment checklists, configuration examples, and step-by-step instructions.

---

## 🗺️ High-Level Deployment Options Overview

```mermaid
graph TD
    A[PetGo Django Backend] --> B[Option 1: Vercel Serverless]
    A --> C[Option 2: PaaS - Render / Railway]
    A --> D[Option 3: Linux VPS - AWS EC2 / DigitalOcean]
    A --> E[Option 4: Docker Containerization]

    B --> B1[Edge Network + AWS Neon DB]
    C --> C1[Gunicorn + Managed PostgreSQL]
    D --> D1[Nginx Proxy + Gunicorn + Systemd]
    E --> E1[Docker Compose + PostgreSQL Container]
```

---

## ✅ Pre-Deployment Checklist

Before deploying to any production platform:

1. **Set Environment Variables in Production Host:**
   - `DJANGO_ENV="production"`
   - `DEBUG=False`
   - `ALLOWED_HOSTS="your-domain.com,your-app.vercel.app"`
   - `DATABASE_URL="postgresql://user:pass@host/dbname?sslmode=require"`
   - `CLOUDINARY_*` keys
   - `RESEND_API_KEY`
   - `OTP_API_KEY`
2. **Apply Database Migrations:**
   ```powershell
   python manage.py migrate
   ```
3. **Collect Static Files:**
   ```powershell
   python manage.py collectstatic --noinput
   ```

---

## 🌐 Option 1: Deploying to Vercel (Serverless Architecture)

### 📐 Architecture Diagram
```mermaid
sequenceDiagram
    autonumber
    actor User as Client App (React/Mobile)
    participant Vercel as Vercel Edge Network
    participant Function as Vercel Python Serverless Function (WSGI)
    participant DB as Cloud PostgreSQL (Neon / Supabase)
    participant CDN as Cloudinary Media CDN

    User->>Vercel: HTTPS Request (/api/...)
    Vercel->>Function: Invoke Serverless Function
    Function->>DB: Query / Update Database via SSL
    DB-->>Function: SQL Dataset
    Function->>CDN: Fetch / Store Media Assets
    Function-->>Vercel: JSON Response
    Vercel-->>User: HTTP 200/201 Response
```

### Step 1: Create `vercel.json` in Project Root
Create `vercel.json` at the root of `PetGo-Backend/`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "petgoshop/wsgi.py",
      "use": "@vercel/python",
      "config": { "maxLambdaSize": "15mb", "runtime": "python3.12" }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "petgoshop/wsgi.py"
    }
  ]
}
```

### Step 2: Deploy via Vercel CLI or GitHub
- **Via Vercel CLI:**
  ```powershell
  npm i -g vercel
  vercel
  ```
- **Via Vercel Dashboard:**
  1. Import the `PetGo-Backend` GitHub repository in Vercel.
  2. Add your `.env` key-value pairs in **Environment Variables**.
  3. Click **Deploy**.

---

## 🚂 Option 2: Deploying to Render / Railway (PaaS Architecture)

### 📐 Architecture Diagram
```mermaid
graph LR
    User[Client Application] -->|HTTPS| LoadBalancer[Render / Railway Load Balancer]
    LoadBalancer -->|Port 8000| Gunicorn[Gunicorn WSGI Server]
    Gunicorn -->|Python Workers| Django[Django App Core]
    Django -->|SSL Connection| PostgreSQL[(Cloud PostgreSQL DB)]
    Django -->|REST Call| External[Cloudinary / Resend / OTP]
```

### Settings for Render / Railway:

- **Build Command:**
  ```bash
  pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
  ```

- **Start Command:**
  ```bash
  gunicorn petgoshop.wsgi:application --bind 0.0.0.0:$PORT
  ```

- **Environment Variables:** Add all variables from `.env` in the platform dashboard.

---

## 🐧 Option 3: Deploying to Linux VPS (AWS EC2 / DigitalOcean)

### 📐 Architecture Diagram
```mermaid
graph TD
    Client[Internet Client / HTTPS] -->|Port 80 / 443| Nginx[Nginx Reverse Proxy]
    Nginx -->|Unix Socket / petgo.sock| Gunicorn[Gunicorn Daemon (Systemd)]
    Gunicorn -->|Django WSGI| Django[PetGo Django Application]
    Django -->|PostgreSQL Protocol| DB[(Managed Database)]
    Django -->|Static Storage| StaticFiles[/var/www/staticfiles/]
```

### Step 1: Install Dependencies on Server
```bash
sudo apt update && sudo apt install python3-pip python3-venv nginx git -y
```

### Step 2: Clone & Set Up Project
```bash
git clone https://github.com/PurpleDiceNet-ORG/PetGo-Backend.git
cd PetGo-Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

### Step 3: Configure Systemd Service (`/etc/systemd/system/petgo.service`)
```ini
[Unit]
Description=Gunicorn daemon for PetGo Django Backend
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/PetGo-Backend
ExecStart=/home/ubuntu/PetGo-Backend/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ubuntu/PetGo-Backend/petgo.sock petgoshop.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start Gunicorn:
```bash
sudo systemctl start petgo
sudo systemctl enable petgo
```

### Step 4: Configure Nginx Reverse Proxy (`/etc/nginx/sites-available/petgo`)
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location /static/ {
        root /home/ubuntu/PetGo-Backend;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/PetGo-Backend/petgo.sock;
    }
}
```

Enable site & reload Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/petgo /etc/nginx/sites-enabled
sudo systemctl reload nginx
```

---

## 🐳 Option 4: Deploying with Docker & Docker Compose

### 📐 Architecture Diagram
```mermaid
graph TD
    subgraph Docker Host
        subgraph Bridge Network
            WebContainer[Django App Container (Gunicorn)]
            DBContainer[PostgreSQL DB Container]
        end
        Port8000[Port 8000:8000] --> WebContainer
        WebContainer -->|Internal Network| DBContainer
    end
    Client[Client App] -->|HTTP Request| Port8000
```

### Sample `Dockerfile`
```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "petgoshop.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Sample `docker-compose.yml`
```yaml
version: '3.8'

services:
  web:
    build: .
    command: gunicorn petgoshop.wsgi:application --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    env_file:
      - .env
```

To run with Docker:
```bash
docker-compose up -d --build
```
