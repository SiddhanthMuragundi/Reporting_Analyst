# Research Portal

AI-powered financial analysis tools for extracting financial statements and summarizing earnings calls.

## Project Structure

```
research-portal/
├── README.md                    # This file
├── backend/                     # FastAPI backend
│   ├── main.py
│   ├── requirements.txt
│   ├── test_api.py
│   ├── outputs/                # Generated Excel files (auto-created)
│   └── Dockerfile
└── frontend/                    # Vue.js frontend
    ├── src/
    │   ├── App.vue
    │   └── main.js
    ├── public/
    │   └── index.html
    ├── package.json
    └── vue.config.js
```

## Features

### Option A: Financial Statement Extraction
- Upload financial statement PDFs
- Extracts income statement line items
- Generates Excel files with metadata
- Handles multiple periods/quarters
- Currency and scale identification

### Option B: Earnings Call Summary
- Upload earnings call transcript PDFs
- Analyzes management tone and confidence
- Extracts key positives and concerns
- Identifies forward guidance
- Lists growth initiatives

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- Node.js 16+
- Anthropic API key

### Step 1: Setup Backend

```bash
# Navigate to backend folder
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set API key (Windows CMD)
set ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Set API key (Mac/Linux)
export ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Start backend server on port 5000
python -c "import uvicorn; from main import app; uvicorn.run(app, host='0.0.0.0', port=8000)"
```

**Backend runs at:** `http://localhost:8000`

### Step 2: Setup Frontend (New Terminal)

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies (first time only)
# This downloads all packages listed in package.json into node_modules folder
# Takes 1-3 minutes depending on internet speed
npm install

# Start development server
npm run serve
```

**What happens during `npm install`:**
- Creates `node_modules/` folder with all dependencies (~200-300 MB)
- Creates `package-lock.json` to lock dependency versions
- Downloads Vue.js, axios, and other required packages
- Only needed once, unless you add new packages or delete node_modules

**Note:** `node_modules/` folder should NOT be committed to git (already in .gitignore)

**Frontend runs at:** `http://localhost:8080` (default Vue port)

### Step 3: Use the Application

Open browser at `http://localhost:8080`

---

## Deployment to Render.com (Step by Step)

### Prerequisites
- GitHub account
- Render.com account (free)
- Anthropic API key

### Step 1: Prepare Your Code

**1.1 Create folder structure:**
```
research-portal/
├── backend/     (put all backend files here)
└── frontend/    (put all frontend files here)
```

**1.2 Create .gitignore in root:**
```bash
node_modules/
__pycache__/
*.pyc
.env
outputs/
dist/
```

**1.3 Push to GitHub:**
```bash
cd research-portal
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/research-portal.git
git push -u origin main
```

---

### Step 2: Deploy Backend to Render

**2.1 Go to Render Dashboard**
- Visit https://render.com
- Sign in or create account
- Click "New +" button → Select "Web Service"

**2.2 Connect Repository**
- Click "Connect a repository"
- Select GitHub
- Grant Render access to your repository
- Choose `research-portal` repository

**2.3 Configure Backend**

Fill in these fields:

| Field | Value |
|-------|-------|
| Name | `research-portal-backend` |
| Region | Choose closest to you |
| Branch | `main` |
| Root Directory | `backend` |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | `Free` |

**2.4 Add Environment Variable**
- Scroll to "Environment Variables" section
- Click "Add Environment Variable"
- Key: `ANTHROPIC_API_KEY`
- Value: `sk-ant-api03-your-actual-key-here`
- Click "Add"

**2.5 Deploy**
- Click "Create Web Service" button
- Wait 2-5 minutes for deployment
- You'll see logs in real-time
- Once done, you'll get a URL like: `https://research-portal-backend.onrender.com`

**2.6 Test Backend**
- Click your backend URL
- You should see: `{"status":"online","service":"Research Portal API",...}`
- Visit `/docs`: `https://research-portal-backend.onrender.com/docs`

---

### Step 3: Update Frontend for Production

**3.1 Update API URL**

Before deploying frontend, update `frontend/src/App.vue`:

Find this line (around line 220):
```javascript
apiBaseUrl: 'http://localhost:8000'
```

Change to your Render backend URL:
```javascript
apiBaseUrl: 'https://research-portal-backend.onrender.com'
```

**3.2 Commit the change:**
```bash
git add frontend/src/App.vue
git commit -m "Update API URL for production"
git push
```

---

### Step 4: Deploy Frontend to Render

**4.1 Create Static Site**
- Go back to Render Dashboard
- Click "New +" → "Static Site"
- Connect same repository

**4.2 Configure Frontend**

| Field | Value |
|-------|-------|
| Name | `research-portal-frontend` |
| Branch | `main` |
| Root Directory | `frontend` |
| Build Command | `npm install && npm run build` |
| Publish Directory | `dist` |

**What happens during build:**
- Render runs `npm install` (downloads node_modules on their server)
- Then runs `npm run build` (creates optimized production files in `dist/` folder)
- Only the `dist/` folder is deployed (not node_modules)

**4.3 Deploy**
- Click "Create Static Site"
- Wait 3-5 minutes for build
- Your app URL: `https://research-portal-frontend.onrender.com`

---

### Step 5: Test Production Deployment

1. Visit `https://research-portal-frontend.onrender.com`
2. Click "Extract Financials" tab
3. Upload a test PDF
4. Click "Process Document"
5. Should work! (first request may take 30s if backend spun down)

---

## Important Notes for Render Deployment

### Free Tier Limitations

**Backend:**
- Spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- This is normal for free tier

**Frontend:**
- No spin-down issues
- Instant loading
- 100 GB bandwidth/month

### Keeping Backend Awake (Optional)

To prevent spin-down, upgrade to paid tier ($7/month) OR use a ping service:

**Option 1: UptimeRobot (Free)**
1. Sign up at https://uptimerobot.com
2. Add monitor: `https://research-portal-backend.onrender.com`
3. Check interval: 5 minutes
4. This keeps backend awake

**Option 2: Cron-job.org (Free)**
1. Sign up at https://cron-job.org
2. Create job to ping your backend every 5 minutes

### Updating Deployed App

**Backend changes:**
```bash
# Make changes to backend/main.py
git add backend/
git commit -m "Update backend"
git push
# Render auto-deploys (takes 2-3 minutes)
```

**Frontend changes:**
```bash
# Make changes to frontend/src/App.vue
git add frontend/
git commit -m "Update frontend"
git push
# Render auto-deploys (takes 3-5 minutes)
```

---

## Configuration

### Backend Port (Local: 5000)

To change port, modify the start command:

```bash
# Port 8000
python -c "import uvicorn; from main import app; uvicorn.run(app, host='0.0.0.0', port=8000)"
```

Or create `backend/start.py`:
```python
import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
```

Then run: `python start.py`

### Frontend API URL

Edit `frontend/src/App.vue`:
```javascript
data() {
  return {
    apiBaseUrl: 'http://localhost:5000'  // Local
    // apiBaseUrl: 'https://your-backend.onrender.com'  // Production
  }
}
```

---

## Troubleshooting

### Local Development

**Backend won't start:**
```bash
pip install -r requirements.txt --force-reinstall
python --version  # Should be 3.9+
```

**Frontend won't start:**
```bash
rm -rf node_modules package-lock.json
npm install
node --version  # Should be 16+
```

**node_modules issues:**
- If you get errors, delete `node_modules/` and `package-lock.json`
- Run `npm install` again
- This is common when switching Node versions

**CORS errors:**
- Check backend is on port 5000
- Verify `apiBaseUrl` in `frontend/src/App.vue`

### Render Deployment

**Backend build fails:**
- Check `backend/requirements.txt` exists
- Check logs in Render dashboard
- Verify Python version

**Frontend build fails:**
- Check `frontend/package.json` exists
- Verify Node.js version in settings
- Check build logs

**API calls fail in production:**
- Verify backend URL in `frontend/src/App.vue`
- Test backend: `https://your-backend.onrender.com/`
- Check browser console for errors

**Backend spins down:**
- Normal for free tier
- First request takes 30-60s to wake up
- Use UptimeRobot to keep awake (see above)

---

## API Documentation

**Local:** http://localhost:5000/docs

**Production:** https://your-backend.onrender.com/docs

### Endpoints

**POST /api/extract-financials**
- Upload: Financial statement PDF
- Returns: Excel file path + metadata
- Time: 15-30 seconds

**POST /api/summarize-earnings-call**
- Upload: Earnings call PDF
- Returns: Structured summary JSON
- Time: 10-20 seconds

**GET /api/download/{filename}**
- Returns: Excel file

---

## Tech Stack

**Backend:** FastAPI + Claude Sonnet 4 + pandas + openpyxl

**Frontend:** Vue.js 3 + Axios + CSS

**Deployment:** Render.com (free tier)

---

## Quick Commands Reference

### Local Development
```bash
# Terminal 1 - Backend
cd backend
set ANTHROPIC_API_KEY=sk-ant-api03-your-key
python -c "import uvicorn; from main import app; uvicorn.run(app, host='0.0.0.0', port=5000)"

# Terminal 2 - Frontend  
cd frontend
npm install  # First time only
npm run serve
```

### Production URLs
```
Frontend: https://research-portal-frontend.onrender.com
Backend:  https://research-portal-backend.onrender.com
API Docs: https://research-portal-backend.onrender.com/docs
```

### Git Deployment
```bash
git add .
git commit -m "Update"
git push
# Render auto-deploys in 2-5 minutes
```

---

## Cost Estimates

**Anthropic API:**
- Financial extraction: ~$0.03 per document
- Earnings summary: ~$0.02 per document

**Render Hosting:**
- Free tier: $0/month (with spin-down)
- Paid tier: $7/month backend + $0 frontend (no spin-down)

---

## Security Checklist

- API key in environment variables (not code)
- `.env` in `.gitignore`
- HTTPS enabled (automatic on Render)
- CORS restricted in production (optional)
- File upload validation enabled
- No sensitive data in git history

---

## Support

**Issues:**
1. Check troubleshooting section
2. Review Render deployment logs
3. Test backend directly via `/docs`
4. Check browser console (F12)

**Documentation:**
- Backend API: Visit `/docs` endpoint
- Frontend: Check `frontend/README.md`
- Render: https://render.com/docs

---

## License

MIT

---