# 🚀 Deployment Guide - DPIA Analysis AI Chatbot

This guide covers multiple deployment options for the DPIA Analysis AI Chatbot, from simple GitHub Pages hosting to full production deployment with backend integration.

## 📋 Table of Contents

1. [Quick GitHub Pages Deployment](#quick-github-pages-deployment)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Troubleshooting](#troubleshooting)

## 🌐 Quick GitHub Pages Deployment

**Perfect for demos and showcasing the chatbot interface**

### Step 1: Fork the Repository

1. Go to the [repository page](https://github.com/your-username/dpia-analysis-chatbot)
2. Click the "Fork" button in the top-right corner
3. Choose your GitHub account as the destination

### Step 2: Enable GitHub Pages

1. Go to your forked repository
2. Click on "Settings" tab
3. Scroll down to "Pages" in the left sidebar
4. Under "Source", select "Deploy from a branch"
5. Choose "main" branch and "/ (root)" folder
6. Click "Save"

### Step 3: Access Your Deployment

Your chatbot will be available at:
```
https://your-username.github.io/dpia-analysis-chatbot/
```

**Note:** GitHub Pages deployment runs in demo mode with simulated AI responses. For full Pega integration, use the production deployment option.

### Step 4: Customize Your Deployment

1. Edit `index.html` and `dpia_chatbot.html` to update:
   - Repository URLs
   - Your GitHub username
   - Contact information
   - Branding elements

2. Commit and push changes:
   ```bash
   git add .
   git commit -m "Customize deployment"
   git push origin main
   ```

## 💻 Local Development Setup

**For development and testing with full backend functionality**

### Prerequisites

- Python 3.9 or higher
- Git
- Modern web browser

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/dpia-analysis-chatbot.git
cd dpia-analysis-chatbot
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your Pega credentials
nano .env  # or use your preferred editor
```

Example `.env` configuration:
```env
PEGA_BASE_URL=https://your-pega-instance.pegacloud.net/prweb/api/v1
PEGA_USERNAME=your-username
PEGA_PASSWORD=your-password
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
DEBUG=true
```

### Step 4: Start the Development Server

```bash
python simple_mcp_server.py
```

The server will start on `http://localhost:8080`

### Step 5: Access the Application

- **Web Interface**: http://localhost:8080/web
- **Direct Chatbot**: Open `dpia_chatbot.html` in your browser
- **API Documentation**: http://localhost:8080/docs (FastAPI auto-generated)

## 🏭 Production Deployment

**For enterprise deployment with full functionality**

### Option 1: Cloud Platform Deployment

#### Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Windows/Linux - download from heroku.com
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-dpia-chatbot
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set PEGA_BASE_URL=https://your-pega-instance.pegacloud.net/prweb/api/v1
   heroku config:set PEGA_USERNAME=your-username
   heroku config:set PEGA_PASSWORD=your-password
   ```

4. **Create Procfile**
   ```bash
   echo "web: python simple_mcp_server.py" > Procfile
   ```

5. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

#### AWS/Azure/GCP Deployment

1. **Containerize the Application**
   
   Create `Dockerfile`:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8080
   CMD ["python", "simple_mcp_server.py"]
   ```

2. **Build and Deploy**
   ```bash
   docker build -t dpia-chatbot .
   docker run -p 8080:8080 --env-file .env dpia-chatbot
   ```

### Option 2: Self-Hosted Deployment

#### Using systemd (Linux)

1. **Create Service File**
   ```bash
   sudo nano /etc/systemd/system/dpia-chatbot.service
   ```

   ```ini
   [Unit]
   Description=DPIA Analysis AI Chatbot
   After=network.target
   
   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/path/to/dpia-analysis-chatbot
   Environment=PATH=/path/to/dpia-analysis-chatbot/venv/bin
   ExecStart=/path/to/dpia-analysis-chatbot/venv/bin/python simple_mcp_server.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable dpia-chatbot
   sudo systemctl start dpia-chatbot
   ```

#### Using Nginx Reverse Proxy

1. **Install Nginx**
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

2. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/dpia-chatbot
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Enable Site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/dpia-chatbot /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## ⚙️ Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PEGA_BASE_URL` | Pega API base URL | `https://instance.pegacloud.net/prweb/api/v1` |
| `PEGA_USERNAME` | Pega username | `your-username` |
| `PEGA_PASSWORD` | Pega password | `your-password` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SERVER_HOST` | Server host | `0.0.0.0` |
| `SERVER_PORT` | Server port | `8080` |
| `DEBUG` | Debug mode | `false` |

### Security Considerations

1. **Never commit `.env` files** to version control
2. **Use environment-specific configurations**
3. **Implement proper authentication** for production
4. **Use HTTPS** in production environments
5. **Regularly rotate credentials**

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>
```

#### 2. Python Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. Pega API Connection Issues
- Verify `PEGA_BASE_URL` is correct
- Check username/password credentials
- Ensure network connectivity to Pega instance
- Verify API permissions

#### 4. CORS Issues in Browser
- Ensure proper CORS headers in `simple_mcp_server.py`
- Use the web interface at `/web` endpoint
- Check browser console for specific errors

### Debug Mode

Enable debug mode for detailed logging:
```bash
export DEBUG=true
python simple_mcp_server.py
```

### Health Checks

Test the deployment:
```bash
# Check server health
curl http://localhost:8080/health

# Test API endpoint
curl -X POST http://localhost:8080/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "analyze_and_create_dpia", "arguments": {"research_text": "test"}}'
```

## 📊 Monitoring and Analytics

### Application Monitoring

1. **Health Endpoint**: `/health`
2. **Metrics Endpoint**: `/metrics` (if implemented)
3. **Logs**: Check application logs for errors

### Performance Optimization

1. **Enable caching** for static assets
2. **Use CDN** for global distribution
3. **Implement rate limiting** for API endpoints
4. **Monitor resource usage**

## 🔄 Updates and Maintenance

### Updating the Application

1. **Pull latest changes**
   ```bash
   git pull origin main
   ```

2. **Update dependencies**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **Restart services**
   ```bash
   sudo systemctl restart dpia-chatbot
   ```

### Backup and Recovery

1. **Backup configuration files**
2. **Document environment variables**
3. **Test recovery procedures**

## 📞 Support

For deployment issues:

1. **Check the logs** first
2. **Review this guide** for common solutions
3. **Open an issue** on GitHub with:
   - Deployment method used
   - Error messages
   - Environment details
   - Steps to reproduce

---

**Happy Deploying! 🚀**

*For additional support, please refer to the main [README.md](README.md) or open an issue on GitHub.* 