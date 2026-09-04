# 🛡️ TarabaInsight - National Security Intelligence Platform

<div align="center">

![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Django](https://img.shields.io/badge/Django-6.1-green)
![Flutter](https://img.shields.io/badge/Flutter-3.x-blue)
![Render](https://img.shields.io/badge/Deployed%20on-Render-purple)

**Real-time crowdsourced intelligence platform for national security, agricultural monitoring, and infrastructure assessment in Taraba State, Nigeria.**

[🌐 Live Dashboard](https://tarabaintel.onrender.com) • [ Full Project Guide](./PROJECT_GUIDE.md)

</div>

---

##  Overview
**TarabaInsight** empowers citizens and field agents to report security threats, infrastructure issues, and agricultural concerns in real-time. It combines a native Flutter mobile app for field data collection with a Django-powered web dashboard for real-time geospatial intelligence and AI-driven threat analysis.

## ✨ Key Features
- 📱 **Native Mobile App:** Android app with offline capabilities, GPS geotagging, and Base64 photo evidence.
- 🗺️ **Interactive Command Center:** Real-time Leaflet.js map with color-coded threat markers (Critical, High, Medium).
- 🤖 **AI-Powered Analytics:** Automatic threat categorization, urgency assessment, and sentiment analysis.
- 🔐 **Secure Architecture:** JWT authentication, role-based access (Citizen/Agent), and secure API routing.
- ⚡ **Live Intelligence Feed:** Auto-refreshing dashboard with cross-component interactivity (click feed to fly-to map).

## 🛠️ Tech Stack
- **Backend:** Django 6.1, Django REST Framework, GeoDjango, PostgreSQL + PostGIS.
- **Frontend (Web):** HTML5, Tailwind CSS, Leaflet.js, Vanilla JS.
- **Mobile:** Flutter 3.x, Dart, Dio, Image Picker, Geolocator.
- **DevOps:** Render, Gunicorn, WhiteNoise, Git/GitHub.

## 🚀 Quick Start

### 1. Backend Setup
```bash
git clone https://github.com/ezrakumo/tarabaintel.git
cd tarabaintel
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate && python manage.py runserver

# 🛡️ TarabaInsight: Autonomous Intelligence Platform

**TarabaInsight** is a full-stack, AI-powered national security and agricultural intelligence platform. It empowers field agents to submit geolocated reports (even offline), automatically analyzes the data for temporal and geospatial patterns, and delivers actionable executive briefings to stakeholders.

---

## 🚀 Key Features

### 📱 1. Offline-First Mobile Field App
- **Resilient Data Collection:** Field agents can submit reports with photo evidence in network dead zones.
- **Auto-Sync Queue:** Reports are saved locally and automatically sync to the cloud the moment connectivity is restored.
- **Modern UI:** Beautiful, intuitive interface built with Flutter and Material 3.

### 🧠 2. AI Intelligence Engine
- **Temporal Analysis:** Detects surges or drops in reporting activity compared to historical baselines.
- **Geospatial Clustering:** Uses DBSCAN algorithms to identify geographic threat hotspots automatically.
- **Automated SITREPs:** Generates natural-language executive briefings, key findings, and strategic recommendations.

### 📊 3. Stakeholder Command Center
- **Interactive Map:** Live Leaflet.js map with real-time report filtering and Base64 image rendering.
- **Executive Briefing Dashboard:** Dark-themed, glassmorphism UI displaying 7-day trend charts (Chart.js), emerging threats, and system alerts.
- **One-Click Export:** Download all intelligence data as a formatted CSV for offline briefings or inter-agency sharing.

### ⚡ 4. Enterprise Automation & Security
- **Flash Alerts:** Automatically triggers email notifications to command staff when the AI flags a `CRITICAL` threat.
- **Autonomous Scheduling:** Secured external Cron jobs trigger daily AI analysis at 08:00 AM without manual intervention.
- **Token-Based Security:** All automation endpoints are protected by secret tokens to prevent unauthorized access or DoS attacks.

---

## 🏗️ Tech Stack

- **Frontend (Mobile):** Flutter, Dart, `connectivity_plus`, `path_provider`
- **Frontend (Web):** Django Templates, Tailwind CSS, Chart.js, Leaflet.js
- **Backend:** Python, Django 6.1, Django REST Framework
- **Database:** PostgreSQL with PostGIS (GeoDjango)
- **AI/ML:** Python, NumPy, scikit-learn (DBSCAN), NetworkX
- **DevOps:** GitHub, Render (Cloud Hosting), cron-job.org (Automation)

---

## ⚙️ Setup & Installation

### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/tarabaintel.git
   cd tarabaintel