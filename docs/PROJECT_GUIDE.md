
---

## ️ PHASE 4.5: CLOUD AI MICROSERVICE DEPLOYMENT

To make the AI analysis work 24/7 in the cloud, we deployed the i_service as a second Render Web Service.

### Step 1: Deploy AI Service
1. Create a new Web Service on Render connected to the same GitHub repo.
2. **Root Directory:** i_service (Crucial for monorepos).
3. **Build Command:** pip install -r requirements.txt
4. **Start Command:** uvicorn main:app --host 0.0.0.0 --port 
5. Add GROQ_API_KEY to Environment Variables.

### Step 2: Fix Python 3.14 Build Errors
Render defaults to Python 3.14, which breaks Pydantic. Fix it by adding a untime.txt:
"python-3.12.3" | Set-Content -Path ai_service\runtime.txt -Encoding UTF8

### Step 3: Connect Django to Cloud AI
1. Copy the new AI service URL (e.g., https://tarabaintel-ai.onrender.com).
2. Add AI_SERVICE_URL to the main Django app's Environment Variables on Render.
3. Update insight/views.py to use os.environ.get('AI_SERVICE_URL', 'http://127.0.0.1:8001').

---

## ️ PHASE 4.5: CLOUD AI MICROSERVICE DEPLOYMENT

To make the AI analysis work 24/7 in the cloud, we deployed the i_service as a second Render Web Service.

### Step 1: Deploy AI Service
1. Create a new Web Service on Render connected to the same GitHub repo.
2. **Root Directory:** i_service (Crucial for monorepos).
3. **Build Command:** pip install -r requirements.txt
4. **Start Command:** uvicorn main:app --host 0.0.0.0 --port 
5. Add GROQ_API_KEY to Environment Variables.

### Step 2: Fix Python 3.14 Build Errors
Render defaults to Python 3.14, which breaks Pydantic. Fix it by adding a untime.txt:
"python-3.12.3" | Set-Content -Path ai_service\runtime.txt -Encoding UTF8

### Step 3: Connect Django to Cloud AI
1. Copy the new AI service URL (e.g., https://tarabaintel-ai.onrender.com).
2. Add AI_SERVICE_URL to the main Django app's Environment Variables on Render.
3. Update insight/views.py to use os.environ.get('AI_SERVICE_URL', 'http://127.0.0.1:8001').
