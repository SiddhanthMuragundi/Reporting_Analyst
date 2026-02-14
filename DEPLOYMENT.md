# Deployment Guide

## Quick Deploy Options

### Option 1: Render.com (Recommended)

1. **Create Render Account**: https://render.com

2. **Connect GitHub**:
   - Push this code to a GitHub repository
   - Connect your GitHub account to Render

3. **Create New Web Service**:
   - Select "Web Service"
   - Connect your repository
   - Configure:
     - Name: `research-portal-api`
     - Environment: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variable**:
   - Key: `ANTHROPIC_API_KEY`
   - Value: Your Anthropic API key

5. **Deploy**: Click "Create Web Service"

Your API will be live at: `https://research-portal-api.onrender.com`

### Option 2: Railway.app

1. **Create Railway Account**: https://railway.app

2. **Deploy from GitHub**:
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli
   
   # Login
   railway login
   
   # Initialize
   railway init
   
   # Add environment variable
   railway variables set ANTHROPIC_API_KEY=your_key_here
   
   # Deploy
   railway up
   ```

3. **Get URL**: Railway will provide a public URL

### Option 3: Fly.io

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login and Deploy**:
   ```bash
   fly auth login
   fly launch
   fly secrets set ANTHROPIC_API_KEY=your_key_here
   fly deploy
   ```

### Option 4: Docker (Local or Any Host)

1. **Build Image**:
   ```bash
   docker build -t research-portal .
   ```

2. **Run Container**:
   ```bash
   docker run -p 8000:8000 \
     -e ANTHROPIC_API_KEY=your_key_here \
     research-portal
   ```

## Testing Your Deployment

### Using cURL:

```bash
# Replace with your deployed URL
BASE_URL="https://your-app.onrender.com"

# Test health check
curl $BASE_URL/

# Test financial extraction
curl -X POST "$BASE_URL/api/extract-financials" \
  -F "file=@financial_statement.pdf"

# Test earnings call summary
curl -X POST "$BASE_URL/api/summarize-earnings-call" \
  -F "file=@earnings_call.pdf"
```

### Using Python:

```python
import requests

BASE_URL = "https://your-app.onrender.com"

# Upload financial statement
with open("statement.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/api/extract-financials",
        files={"file": f}
    )
    print(response.json())
```

## Monitoring

### Render.com:
- View logs in Render dashboard
- Monitor performance metrics
- Set up alerts

### Railway.app:
- Use `railway logs` command
- View metrics in dashboard

### Fly.io:
- Use `fly logs` command
- Monitor with Fly dashboard

## Limitations on Free Tier

| Platform | Request Timeout | Memory | Storage |
|----------|----------------|---------|---------|
| Render   | 60s            | 512MB   | 1GB     |
| Railway  | 30s            | 512MB   | 1GB     |
| Fly.io   | 60s            | 256MB   | 3GB     |

**Recommendations**:
- Keep PDF files under 10MB
- Expect 10-30s processing time per document
- Use Render for most reliable free tier

## Production Checklist

- Environment variables set
- API key secured (not in code)
- CORS configured for your frontend domain
- Error logging enabled
- Health check endpoint working
- Rate limiting configured (if needed)
- File size limits appropriate
- Timeout handling implemented

## API Documentation

Once deployed, visit:
- API Docs: `https://your-app.onrender.com/docs`
- Health Check: `https://your-app.onrender.com/`

## Support

For issues:
1. Check deployment logs
2. Verify environment variables
3. Test with sample files first
4. Check API key validity
