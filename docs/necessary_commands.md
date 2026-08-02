# 💻 PetGo Backend Necessary Commands Cheat Sheet

This document lists all essential commands required for daily development, database management, user administration, and troubleshooting in the **PetGo Django Backend**.

---

## 🐍 1. Environment & Setup Commands

### Create Python Virtual Environment
```powershell
python -m venv venv
```

### Activate Virtual Environment
- **Windows PowerShell:**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows Command Prompt (cmd):**
  ```cmd
  .\venv\Scripts\activate.bat
  ```
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

### Install Project Dependencies
```powershell
pip install -r requirements.txt
```

### Upgrade pip
```powershell
python -m pip install --upgrade pip
```

---

## 🗄️ 2. Database & Migration Commands

### Create New Migrations (Detect Model Changes)
```powershell
python manage.py makemigrations
```

### Create Migrations for a Specific App
```powershell
python manage.py makemigrations user
```

### Apply Migrations to Database
```powershell
python manage.py migrate
```

### Show Status of All Migrations
```powershell
python manage.py showmigrations
```

---

## 🚀 3. Server Execution Commands

### Start Local Development Server
```powershell
python manage.py runserver
```

### Start Server on Custom Port (e.g. 8080)
```powershell
python manage.py runserver 8080
```

### Start Server Accessible from Local Network
```powershell
python manage.py runserver 0.0.0.0:8000
```

---

## 🔐 4. Admin & User Management Commands

### Create Admin Superuser
```powershell
python manage.py createsuperuser
```

### Change a User's Password
```powershell
python manage.py changepassword <username>
```

---

## 🔍 5. System Health, Shell & Testing

### Check Django Configuration for Errors
```powershell
python manage.py check
```

### Open Django Interactive Python Shell
```powershell
python manage.py shell
```

### Run Test Suite
```powershell
python manage.py test
```

---

## 📁 6. Static Files & Production Preparation

### Collect Static Files for Production
```powershell
python manage.py collectstatic --noinput
```

---

## ⚡ Quick Troubleshooting Cheat Sheet

| Symptom | Cause | Solution Command |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'django'` | Virtual environment not activated | `.\venv\Scripts\Activate.ps1` |
| `OperationalError: no such table` | Pending migrations | `python manage.py migrate` |
| `Port already in use` | Another process running on 8000 | `python manage.py runserver 8080` |
| Settings change not loading | Server needs reload | Restart `python manage.py runserver` |
