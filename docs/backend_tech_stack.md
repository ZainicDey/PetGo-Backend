# 🧰 PetGo Backend Tech Stack Overview

This document lists all technologies, frameworks, libraries, cloud services, and tools used in the **PetGo Backend**.

---

## ⚡ 1. Core Framework & Language

| Technology | Version | Purpose & Usage |
| :--- | :--- | :--- |
| **Python** | `3.12` | Core programming language for all backend services |
| **Django** | `6.0.7` | High-level Python Web Framework providing ORM, Admin Panel, and App Architecture |
| **Django REST Framework (DRF)** | `3.17.1` | Toolkit for building powerful, scalable RESTful APIs |

---

## 🔐 2. Authentication, Security & CORS

| Library / Tool | Purpose & Usage |
| :--- | :--- |
| **Django REST Framework SimpleJWT** | Stateless JWT authentication producing short-lived `access` tokens and long-lived `refresh` tokens |
| **Google Auth SDK** | Google OAuth 2.0 integration for seamless Google Social Sign-In |
| **Custom Phone OTP Engine** | 2-Step Phone Registration with 6-digit OTP verification via SMS API |
| **django-cors-headers** | Cross-Origin Resource Sharing middleware enabling React / Next.js / Mobile clients to connect safely |

---

## 🗄️ 3. Database & ORM

| Technology | Purpose & Usage |
| :--- | :--- |
| **PostgreSQL** | Primary relational database (Hosted on AWS Cloud via Neon / Supabase) |
| **psycopg2-binary** | High-performance PostgreSQL database adapter for Python |
| **Django ORM** | Object-Relational Mapper for database modeling, migrations, and relationship management |
| **SQLite3** | Lightweight local file-based fallback database |

---

## ☁️ 4. Cloud Services & Third-Party APIs

| Service | Library | Purpose & Usage |
| :--- | :--- | :--- |
| **Cloudinary** | `cloudinary` (v1.45.0) | Cloud-based media storage and image CDN for user avatars, pet photos, and clinic images |
| **Pillow** | `Pillow` (v12.3.0) | Python imaging library for image processing, cropping, and validation before cloud uploads |
| **Resend API** | `resend` | Cloud transaction email service for welcome emails, booking confirmations, and password resets |
| **OTP Service** | `requests` | External SMS Gateway integration for sending phone verification codes |

---

## 📄 5. API Documentation & Tooling

| Library | Purpose & Usage |
| :--- | :--- |
| **drf-spectacular** | Generates OpenAPI 3.0 specifications and serves interactive **Swagger UI** (`/api/docs/`) and Schema (`/api/schema/`) |
| **django-filter** | Provides URL query filtering capabilities for products, appointments, and foster houses |

---

## 🚀 6. Server, Static Files & Environment

| Library / Tool | Purpose & Usage |
| :--- | :--- |
| **python-dotenv** | Loads secret environment variables from `.env` into Django `os.environ` |
| **Whitenoise** | Efficient static file serving directly from Django in production environments |
| **Gunicorn** | Production WSGI HTTP server for deploying on Linux/Cloud hosts |
| **Vercel / Cloud Host** | Production deployment target configured via `.vercelignore` and WSGI entry point |

---

## 📊 Summary Stack Architecture Map

```text
[ React / Next.js / Mobile Frontend ]
                 │
                 ▼ (HTTP REST Requests)
[ django-cors-headers (CORS Filtering) ]
                 │
                 ▼
[ SimpleJWT / Google Auth (Security & Token Check) ]
                 │
                 ▼
[ Django REST Framework (Views + Serializers) ]
                 │
      ┌──────────┼──────────┐
      ▼          ▼          ▼
[ PostgreSQL ] [Cloudinary] [Resend / OTP]
 (Neon AWS)    (Image CDN)   (Email / SMS)
```
