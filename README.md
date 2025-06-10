# 🤖 DPIA Analysis AI Chatbot

An intelligent chatbot for Digital Pathology and Image Analysis (DPIA) case creation, powered by Galileo AI and integrated with Pega systems.

## 🌟 Features

- **AI-Powered Analysis**: Uses Galileo AI to analyze research text and extract relevant fields
- **Smart Case Type Recommendation**: Automatically suggests CALM vs DPIA case types
- **Real-time Field Detection**: Identifies therapeutic areas, PI names, pathologists, and more
- **Pega Integration**: Creates cases directly in Pega systems
- **GitHub Pages Ready**: Works both locally and on GitHub Pages

## 🚀 Quick Start

### Option 1: GitHub Pages (Demo Mode)

Visit the live demo: [https://bhashyem.github.io/dpia-ai-chatbot/dpia_chatbot_production.html](https://bhashyem.github.io/dpia-ai-chatbot/dpia_chatbot_production.html)

**Note**: For full functionality, you need to deploy the server (see below).

### Option 2: Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/pega_model_context_server.git
   cd pega_model_context_server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export GALILEO_API_KEY=your_api_key
   export PEGA_USERNAME=your_username
   export PEGA_PASSWORD=your_password
   ```

4. **Start the server**
   ```bash
   python3 main_claude.py
   ```

5. **Open the chatbot**
   Visit: `http://localhost:8080/dpia_chatbot_production.html`

## 🌐 Deploying to Production

To use the chatbot on GitHub Pages with full functionality, you need to deploy the server to a cloud platform.

### Quick Deploy Options:

#### Heroku (Recommended)
```bash
heroku create dpia-server-production
git push heroku main
heroku config:set GALILEO_API_KEY=your_key
heroku config:set PEGA_USERNAME=your_username
heroku config:set PEGA_PASSWORD=your_password
```

#### Render
1. Connect your GitHub repo to [Render](https://render.com)
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn main_claude:app --host=0.0.0.0 --port=$PORT`
4. Add environment variables

#### Railway
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GALILEO_API_KEY` | Galileo AI API key | Yes |
| `PEGA_USERNAME` | Pega system username | Yes |
| `PEGA_PASSWORD` | Pega system password | Yes |
| `PEGA_BASE_URL` | Pega API base URL | No (has default) |

### Custom Server URL

You can use a custom server by adding the `api` parameter to the URL:
```
https://bhashyem.github.io/dpia-ai-chatbot/dpia_chatbot_production.html?api=https://your-server.com
```

## 📖 Usage

1. **Enter Research Text**: Paste your research description into the chatbot
2. **AI Analysis**: The system analyzes the text and extracts relevant fields
3. **Case Type Recommendation**: Get AI-powered suggestions for CALM vs DPIA cases
4. **Field Validation**: Review and complete any missing mandatory fields
5. **Case Creation**: Create the case directly in your Pega system

### Example Research Texts

**DPIA Example:**
```
Leica SP8 - Bldg 12 Time-lapse imaging to monitor small molecule distribution in mammalian cells
```

**CALM Example:**
```
CALM request for CD19/CD20 Allo1 CAR-T MS
```

## 🧪 Testing Features

The chatbot includes several testing features:

- **🔧 Test Validation**: Debug field validation logic
- **🧪 Test Case Type Logic**: Test AI recommendation system
- **💡 Show Examples**: View sample research texts

## 🏗️ Architecture

```
Frontend (GitHub Pages)
    ↓
FastAPI Server (Cloud Platform)
    ↓
Galileo AI (Analysis)
    ↓
Pega System (Case Creation)
```

## 🔒 Security

- Environment variables for sensitive data
- HTTPS encryption for all communications
- CORS protection for cross-origin requests
- No sensitive data stored in frontend code

## 🛠️ Development

### Project Structure
```
├── main_claude.py              # Main FastAPI server
├── galileo_claude_adapter.py   # Galileo AI integration
├── galileo_integration.py      # Galileo AI client
├── dpia_chatbot_production.html # Main chatbot interface
├── context_upload.html         # Context management
├── requirements.txt            # Python dependencies
├── DEPLOYMENT.md              # Deployment guide
└── README.md                  # This file
```

### API Endpoints

- `GET /health` - Health check
- `POST /analyze` - Analyze research text
- `POST /chat` - Chat with AI
- `POST /tools/call` - Call analysis tools
- `POST /create-case` - Create Pega case
- `GET /docs` - API documentation

## 📊 Monitoring

The system includes comprehensive logging and monitoring:

- Request/response logging
- Performance metrics
- Error tracking
- Galileo AI integration metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For issues and questions:

1. Check the [DEPLOYMENT.md](DEPLOYMENT.md) guide
2. Review the API documentation at `/docs`
3. Open an issue on GitHub
4. Check server logs for error details

## 🎯 Roadmap

- [ ] Enhanced AI model training
- [ ] Additional case type support
- [ ] Advanced field validation
- [ ] Multi-language support
- [ ] Mobile app integration

---

**Made with ❤️ for Digital Pathology and Research Excellence** 