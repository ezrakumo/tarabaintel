
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
Render defaults to Python 3.14, which breaks Pydantic. Fix it by adding a 
untime.txt:
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
Render defaults to Python 3.14, which breaks Pydantic. Fix it by adding a 
untime.txt:
"python-3.12.3" | Set-Content -Path ai_service\runtime.txt -Encoding UTF8

### Step 3: Connect Django to Cloud AI
1. Copy the new AI service URL (e.g., https://tarabaintel-ai.onrender.com).
2. Add AI_SERVICE_URL to the main Django app's Environment Variables on Render.
3. Update insight/views.py to use os.environ.get('AI_SERVICE_URL', 'http://127.0.0.1:8001').
---

## 📱 PHASE 5: MOBILE APP DEVELOPMENT (FLUTTER)

To allow citizens, volunteers, and security agencies to report incidents on the go, we built a cross-platform mobile app using Flutter.

### Step 1: Environment Setup
1. Download Flutter SDK and extract to `C:\src\flutter`.
2. Add `C:\src\flutter\bin` to Windows System PATH.
3. Run `flutter doctor` to verify installation.
4. **Pro Tip:** Use Chrome (`flutter run -d chrome`) for rapid UI and API testing before building native Android/iOS binaries.

### Step 2: Project Scaffolding & Dependencies
1. Run `flutter create tarabainsight_mobile`.
2. Add the HTTP package to `pubspec.yaml`:
   ```yaml
   dependencies:
     flutter:
       sdk: flutter
     http: ^1.2.0
