# 🤖 DPIA Analysis AI Chatbot

An intelligent conversational assistant for analyzing research text and creating validated Data Privacy Impact Assessment (DPIA) cases. This AI-powered chatbot automatically detects key information from research descriptions and guides users through an interactive process to create complete DPIA cases.

## ✨ Features

- **🔍 Intelligent Text Analysis**: Automatically detects therapeutic areas, procedures, assay types, and other key information from research text
- **💬 Interactive Conversations**: Conversational interface that asks contextual questions for missing information
- **✅ Field Validation**: Ensures all mandatory fields are completed before case creation
- **🏢 Pega Integration**: Creates validated DPIA cases in Pega systems
- **📱 Modern UI**: Beautiful, responsive web interface optimized for all devices
- **🎯 Smart Recommendations**: Provides intelligent suggestions based on text analysis

## 🚀 Live Demo

**[Try the Live Demo](https://your-username.github.io/dpia-analysis-chatbot/dpia_chatbot.html)**

*Note: The demo version simulates the AI analysis. For full Pega integration, deploy with the backend server.*

## 🛠️ Technology Stack

- **Frontend**: Pure HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python 3.9+ with FastAPI
- **AI Analysis**: Custom NLP algorithms for field detection
- **Integration**: Pega REST API
- **Deployment**: GitHub Pages compatible

## 📋 Detected Fields

The AI chatbot automatically detects and validates these mandatory fields:

1. **👨‍🔬 Primary Investigator (PI)**: Project lead researcher
2. **🔬 Pathologist**: Assigned pathologist for the study
3. **🏥 Therapeutic Area**: Research domain (CVRM, Neurology, Oncology, etc.)
4. **🔬 Procedure**: Analysis type (Bright-field, Fluorescence, Combined)
5. **🧪 Assay Type/Staining Type**: Staining methodology (H&E, IHC, Special Stain, Other)
6. **📋 Project Title**: Descriptive project name
7. **🎯 Request Purpose**: Objective of the analysis

## 🎮 How to Use

1. **Start Conversation**: Open the chatbot and describe your research
2. **AI Analysis**: The bot automatically detects information from your text
3. **Interactive Questions**: Answer any follow-up questions for missing fields
4. **Validation**: All mandatory fields are validated
5. **Case Creation**: Complete DPIA case is created in Pega

### Example Research Text

```
We have 4 groups (healthy, injured+vehicle control, treatment 1(Rmim), treatment 2 (Wmim).
Lung stem cells (AT2-TRITC) and total cells (DAPI) are stained. N=9-10 per group were 
stained and need imaging and quantification. I am interested in imaging of AT2 (TRITC) 
stem cells and DAPI and quantification of: 1. # of AT2 cells per lung section 
2. # of AT2 cells normalized by total area of lung section 3. # of AT2 cells 
normalized by # of DAPI cells per lung section
```

## 🚀 Quick Start

### Option 1: GitHub Pages (Demo Mode)

1. Fork this repository
2. Enable GitHub Pages in repository settings
3. Visit `https://your-username.github.io/dpia-analysis-chatbot/dpia_chatbot.html`

### Option 2: Full Deployment with Backend

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/dpia-analysis-chatbot.git
   cd dpia-analysis-chatbot
   ```

2. **Set up Python environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your Pega credentials
   ```

4. **Start the backend server**:
   ```bash
   python simple_mcp_server.py
   ```

5. **Open the web interface**:
   - Navigate to `http://localhost:8080/web`
   - Or open `dpia_chatbot.html` in your browser

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with your Pega configuration:

```env
PEGA_BASE_URL=https://your-pega-instance.pegacloud.net/prweb/api/v1
PEGA_USERNAME=your-username
PEGA_PASSWORD=your-password
```

### API Configuration

Update the `CONFIG` object in `dpia_chatbot.html` for your deployment:

```javascript
const CONFIG = {
    // For local development
    API_URL: 'http://localhost:8080/tools/call',
    // For production deployment
    // API_URL: 'https://your-backend-url.com/tools/call'
};
```

## 📁 Project Structure

```
dpia-analysis-chatbot/
├── dpia_chatbot.html          # Main chatbot interface
├── simple_mcp_server.py       # Backend API server
├── scanning_summarizer.py     # AI analysis engine
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── README.md                 # This file
└── docs/                     # Documentation
    ├── api.md               # API documentation
    ├── deployment.md        # Deployment guide
    └── screenshots/         # Interface screenshots
```

## 🔧 API Endpoints

### Analyze and Create DPIA

```http
POST /tools/call
Content-Type: application/json

{
  "name": "analyze_and_create_dpia",
  "arguments": {
    "research_text": "Your research description...",
    "auto_create": true,
    "prompt_responses": {
      "Pathologist": "Dr. Smith",
      "Therapeutic Area": "Neurology"
    }
  }
}
```

### Response Format

```json
{
  "success": true,
  "analysis": {
    "detected_fields": {
      "Therapeutic Area": "Neurology",
      "Procedure": "Fluorescence (IF)",
      "Request Purpose": "Quantification and analysis"
    },
    "interactive_prompts": [...]
  },
  "case_created": true,
  "case_id": "C-16371"
}
```

## 🎨 Customization

### Styling

The chatbot uses CSS custom properties for easy theming:

```css
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --message-user-bg: #007bff;
  --message-bot-bg: white;
  --border-radius: 18px;
}
```

### AI Detection Logic

Customize field detection in `scanning_summarizer.py`:

```python
def detect_therapeutic_area(self, text):
    # Add your custom detection logic
    keywords = {
        'neurology': ['brain', 'neural', 'neuron'],
        'oncology': ['cancer', 'tumor', 'malignant']
    }
    # Implementation...
```

## 🧪 Testing

### Run Backend Tests

```bash
python test_interactive_bot.py
```

### Manual Testing Scenarios

1. **Complete Detection**: Text with all fields detectable
2. **Partial Detection**: Text requiring interactive prompts
3. **Error Handling**: Invalid inputs and network errors
4. **Mobile Responsiveness**: Test on various screen sizes

## 📊 Analytics & Monitoring

The chatbot includes built-in analytics for:

- **Field Detection Accuracy**: Track automatic detection rates
- **User Interaction Patterns**: Monitor conversation flows
- **Case Creation Success**: Measure completion rates
- **Performance Metrics**: Response times and error rates

## 🔒 Security & Privacy

- **Data Encryption**: All API communications use HTTPS
- **Authentication**: Secure Pega API authentication
- **Input Validation**: Comprehensive input sanitization
- **Privacy Compliance**: GDPR and HIPAA considerations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow JavaScript ES6+ standards
- Use semantic HTML5 elements
- Maintain responsive design principles
- Include comprehensive error handling
- Write clear, documented code

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Wiki](https://github.com/your-username/dpia-analysis-chatbot/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-username/dpia-analysis-chatbot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/dpia-analysis-chatbot/discussions)

## 🎯 Roadmap

- [ ] **Multi-language Support**: Internationalization
- [ ] **Voice Interface**: Speech-to-text integration
- [ ] **Advanced AI**: Machine learning improvements
- [ ] **Mobile App**: Native mobile applications
- [ ] **Batch Processing**: Multiple case creation
- [ ] **Dashboard**: Analytics and reporting interface

## 🏆 Acknowledgments

- **Pega Platform**: For robust case management capabilities
- **FastAPI**: For excellent Python web framework
- **Modern Web Standards**: For responsive, accessible design

---

**Made with ❤️ for streamlined DPIA case creation**

*For questions or support, please open an issue or contact the development team.* 