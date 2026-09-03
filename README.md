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

