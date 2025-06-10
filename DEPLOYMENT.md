# 🚀 DPIA Server Deployment Guide

This guide will help you deploy your DPIA server to various cloud platforms so it can work with your GitHub Pages chatbot.

## 📋 Prerequisites

- Your DPIA server code (Python FastAPI application)
- Git repository with your code
- Account on your chosen cloud platform

## 🌐 Deployment Options

### 1. Heroku (Recommended)

**Step 1: Install Heroku CLI**
```bash
# macOS
brew install heroku/brew/heroku

# Or download from https://devcenter.heroku.com/articles/heroku-cli
```

**Step 2: Login and Create App**
```bash
heroku login
heroku create dpia-server-production
```

**Step 3: Add Procfile**
Create a `Procfile` in your project root:
```
web: uvicorn main_claude:app --host=0.0.0.0 --port=${PORT:-8080}
```

**Step 4: Deploy**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

**Step 5: Set Environment Variables**
```bash
heroku config:set GALILEO_API_KEY=your_api_key
heroku config:set PEGA_USERNAME=your_username
heroku config:set PEGA_PASSWORD=your_password
```

### 2. Render

**Step 1: Connect GitHub Repository**
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository

**Step 2: Configure Service**
- **Name**: `dpia-server`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main_claude:app --host=0.0.0.0 --port=$PORT`

**Step 3: Add Environment Variables**
Add your environment variables in the Render dashboard.

### 3. Railway

**Step 1: Install Railway CLI**
```bash
npm install -g @railway/cli
```

**Step 2: Login and Deploy**
```bash
railway login
railway init
railway up
```

**Step 3: Add Environment Variables**
```bash
railway variables set GALILEO_API_KEY=your_api_key
railway variables set PEGA_USERNAME=your_username
railway variables set PEGA_PASSWORD=your_password
```

### 4. Google Cloud Run

**Step 1: Create Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main_claude:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Step 2: Deploy**
```bash
gcloud run deploy dpia-server \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🔧 Update GitHub Pages Configuration

After deploying, update your server URL in the chatbot:

1. **Option 1: Update the code directly**
   - Edit `dpia_chatbot_production.html`
   - Replace `https://dpia-server-production.herokuapp.com` with your actual server URL

2. **Option 2: Use URL parameter**
   - Visit your GitHub Pages site with: `?api=YOUR_SERVER_URL`
   - Example: `https://bhashyem.github.io/dpia-ai-chatbot/dpia_chatbot_production.html?api=https://your-server.herokuapp.com`

## 🔍 Testing Your Deployment

1. **Check Server Health**
   ```bash
   curl https://your-server-url.com/health
   ```

2. **Test API Endpoint**
   ```bash
   curl -X POST https://your-server-url.com/analyze \
     -H "Content-Type: application/json" \
     -d '{"research_text": "Test analysis"}'
   ```

3. **Visit Your Chatbot**
   - Go to: `https://bhashyem.github.io/dpia-ai-chatbot/dpia_chatbot_production.html`
   - Should show "✅ Server Connected" instead of "🔴 Server Disconnected"

## 🛠️ Troubleshooting

### Common Issues:

1. **CORS Errors**
   - Make sure your server includes CORS middleware
   - Check that your server allows requests from `bhashyem.github.io`

2. **Environment Variables**
   - Ensure all required environment variables are set on your cloud platform
   - Check logs for missing configuration

3. **Port Configuration**
   - Most cloud platforms use dynamic ports
   - Make sure your app uses `PORT` environment variable

4. **Dependencies**
   - Ensure `requirements.txt` includes all dependencies
   - Check that Python version matches your local development

### Checking Logs:

**Heroku:**
```bash
heroku logs --tail -a dpia-server-production
```

**Render:**
Check logs in the Render dashboard

**Railway:**
```bash
railway logs
```

## 📝 Next Steps

1. Deploy your server using one of the methods above
2. Update the API URL in your GitHub Pages chatbot
3. Test the connection
4. Your chatbot should now work on GitHub Pages!

## 🔒 Security Notes

- Never commit API keys or passwords to your repository
- Use environment variables for all sensitive configuration
- Consider adding authentication to your API endpoints
- Enable HTTPS on your deployed server

## 📞 Support

If you encounter issues:
1. Check the server logs
2. Verify environment variables are set correctly
3. Test API endpoints directly
4. Check CORS configuration 