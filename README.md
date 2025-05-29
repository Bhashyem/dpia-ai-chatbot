# 🤖 Claude-Enhanced DPIA Chatbot

An intelligent Data Privacy Impact Assessment (DPIA) chatbot that combines **Claude LLM** with **Pega case management** for automated biomedical research analysis and compliance workflows.

## 🌟 Features

### 🧠 **Claude AI Integration**
- **Intelligent Text Analysis**: Automatically extracts DPIA fields from research text
- **Conversational Interface**: Natural language interaction with Claude LLM
- **Field Enhancement**: Smart detection and validation of mandatory fields
- **Confidence Scoring**: AI confidence levels for extracted information

### 🔬 **Biomedical Research Focus**
- **Therapeutic Area Detection**: CVRM, Neurology, Oncology, Ophthalmology, etc.
- **Procedure Classification**: Bright-field (BF), Fluorescence (IF), BF+IF
- **Assay Type Recognition**: H&E, IHC, Special Stain, and custom staining
- **Research Context Understanding**: Imaging, time-lapse, molecular distribution

### 🏢 **Enterprise Integration**
- **Pega Case Management**: Seamless DPIA case creation in Pega systems
- **Dual Workflow Support**: AI-powered analysis + traditional questionnaire
- **Session Management**: Persistent conversation state and field tracking
- **API-First Design**: RESTful endpoints for integration

### 🎯 **Mandatory Field Extraction**
- Principal Investigator (PI)
- Pathologist
- Therapeutic Area
- Procedure Type
- Assay/Staining Type
- Project Title
- Request Purpose

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Anthropic API key (Claude)
- Pega system access (optional for demo mode)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd pega_model_context_server
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and Pega credentials
```

5. **Start the server**
```bash
python main_claude.py
```

6. **Access the interface**
- Web UI: http://localhost:8080
- API Documentation: http://localhost:8080/docs
- Health Check: http://localhost:8080/health

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Claude AI Configuration
ANTHROPIC_API_KEY=your_claude_api_key_here

# Pega System Configuration
PEGA_BASE_URL=https://your-pega-instance.pegacloud.net/prweb/api/v1
PEGA_USERNAME=your_username
PEGA_PASSWORD=your_password
```

## 📚 API Endpoints

### 🤖 **Claude-Enhanced Endpoints**

#### Chat with Claude
```bash
POST /chat
{
  "message": "Leica SP8 - Time-lapse imaging to monitor small molecule distribution",
  "user_id": "optional_user_id",
  "session_id": "optional_session_id"
}
```

#### Analyze Research Text
```bash
POST /analyze
{
  "research_text": "Your research description here",
  "enhance_fields": true
}
```

#### Create DPIA Case
```bash
POST /create-case
{
  "detected_fields": {
    "PI": "Dr. Smith",
    "Pathologist": "Dr. Johnson",
    "Therapeutic Area": "Neurology",
    "Procedure": "Fluorescence (IF)",
    "Assay Type/Staining Type": "Time-lapse imaging",
    "Project Title": "Molecular Distribution Study",
    "Request Purpose": "Monitor small molecule distribution"
  },
  "research_text": "Original research text"
}
```

### 🏢 **Traditional Endpoints**

#### Questionnaire Flow
```bash
POST /question
{
  "current_state": "start",
  "answer": "Yes",
  "user_id": "user123"
}
```

#### Direct Case Creation
```bash
POST /cases
{
  "caseTypeID": "Roche-Pathworks-Work-DPIA",
  "processID": "pyStartCase",
  "content": {}
}
```

## 🎯 Usage Examples

### Example 1: AI-Powered Analysis
```python
import requests

# Analyze research text with Claude
response = requests.post("http://localhost:8080/analyze", json={
    "research_text": "Leica SP8 confocal microscopy for TRITC-stained lung tissue analysis in CVRM research",
    "enhance_fields": True
})

analysis = response.json()
print(f"Detected fields: {analysis['detected_fields']}")
print(f"Missing fields: {analysis['missing_fields']}")
```

### Example 2: Conversational Interface
```python
# Chat with Claude about DPIA requirements
response = requests.post("http://localhost:8080/chat", json={
    "message": "I need help creating a DPIA for my stem cell imaging study",
    "user_id": "researcher123"
})

print(response.json()["response"])
```

### Example 3: Complete Workflow
```python
# 1. Analyze text
analysis = requests.post("http://localhost:8080/analyze", json={
    "research_text": "Time-lapse imaging study of AT2 cells in lung tissue"
}).json()

# 2. Create case if all fields detected
if not analysis["missing_fields"]:
    case = requests.post("http://localhost:8080/create-case", json={
        "detected_fields": analysis["detected_fields"],
        "research_text": "Time-lapse imaging study of AT2 cells in lung tissue"
    }).json()
    print(f"Created case: {case['ID']}")
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   FastAPI Server │    │   Claude LLM    │
│                 │◄──►│                  │◄──►│                 │
│ - Chat Interface│    │ - Session Mgmt   │    │ - Text Analysis │
│ - Field Forms   │    │ - API Endpoints  │    │ - Field Extract │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Pega System   │
                       │                 │
                       │ - Case Creation │
                       │ - Workflow Mgmt │
                       └─────────────────┘
```

## 🔍 Key Components

### 1. **Claude Integration** (`claude_integration.py`)
- `ClaudeIntegration`: Main class for AI interactions
- `AnalysisResult`: Structured analysis results
- Field detection and enhancement algorithms

### 2. **FastAPI Server** (`main_claude.py`)
- RESTful API endpoints
- Session management
- Pega integration
- Error handling and fallbacks

### 3. **Web Interface** (`dpia_chatbot_claude.html`)
- Modern, responsive UI
- Real-time chat interface
- Field validation and forms
- Progress tracking

### 4. **Legacy Support** (`scanning_summarizer.py`)
- Traditional keyword-based analysis
- Fallback when Claude is unavailable
- Interactive field prompting

## 🧪 Testing

### Run Analysis Tests
```bash
python test_interactive_bot.py
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8080/health

# Analyze sample text
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"research_text": "TRITC staining of lung tissue for CVRM research"}'
```

### Interactive Testing
```bash
python test_full_interactive_flow.py
```

## 🔒 Security & Privacy

- **API Key Protection**: Environment variables for sensitive data
- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Graceful fallbacks and error messages
- **Session Isolation**: User-specific session management

## 🚀 Deployment

### Local Development
```bash
python main_claude.py
```

### Production Deployment
```bash
# Using uvicorn directly
uvicorn main_claude:app --host 0.0.0.0 --port 8080

# Using Docker (create Dockerfile)
docker build -t dpia-chatbot .
docker run -p 8080:8080 dpia-chatbot
```

## 📈 Performance Features

- **Async Processing**: Non-blocking API calls
- **Session Caching**: Persistent conversation state
- **Fallback Mechanisms**: Graceful degradation when services unavailable
- **Confidence Scoring**: Quality assessment of AI extractions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint when server is running
- **Issues**: Create GitHub issues for bugs or feature requests
- **API Reference**: Available at `http://localhost:8080/docs`

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Batch processing capabilities
- [ ] Integration with additional LLM providers
- [ ] Enhanced security features
- [ ] Mobile-responsive improvements

---

**Built with ❤️ for biomedical research compliance and automation** 