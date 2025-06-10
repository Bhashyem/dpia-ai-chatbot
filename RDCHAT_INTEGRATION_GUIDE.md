# RDChat Integration Guide for DPIA AI Chatbot

## Overview

This guide explains how to integrate your DPIA AI Chatbot with Roche's internal rdchat platform (https://rdchat.roche.com/). The integration allows users to interact with the DPIA chatbot directly within their familiar chat environment.

## Integration Architecture

```
rdchat.roche.com → Webhook → Your DPIA Server → Claude Analysis → Response → rdchat
```

## Integration Options

### 1. Webhook Integration (Recommended)

**Pros:**
- Real-time message processing
- Seamless user experience
- Supports rich message formatting
- Easy to implement and maintain

**Cons:**
- Requires webhook configuration in rdchat
- Need public endpoint or VPN access

### 2. Bot User Integration

**Pros:**
- Native bot presence in channels
- Can initiate conversations
- Full API access

**Cons:**
- Requires bot user creation
- More complex authentication

### 3. Slash Command Integration

**Pros:**
- Simple command-based interface
- Easy to discover and use
- Minimal setup required

**Cons:**
- Limited to command-response pattern
- Less conversational

## Setup Instructions

### Step 1: Configure Environment Variables

Add these variables to your `.env` file:

```bash
# RDChat Integration Configuration
RDCHAT_WEBHOOK_TOKEN=your_rdchat_webhook_token
RDCHAT_BOT_USERNAME=DPIA-AI-Bot
RDCHAT_WEBHOOK_URL=https://rdchat.roche.com/hooks/your_webhook_id
RDCHAT_BOT_AVATAR=https://your-domain.com/dpia-bot-avatar.png
RDCHAT_ALLOWED_CHANNELS=dpia-channel,research-channel,pathology-channel
```

### Step 2: Install Dependencies

```bash
pip install httpx>=0.25.0
```

### Step 3: Configure RDChat Webhook

1. **Access RDChat Admin Panel:**
   - Log into https://rdchat.roche.com/
   - Navigate to Administration → Integrations

2. **Create Incoming Webhook:**
   - Click "New Integration" → "Incoming WebHook"
   - Set channel: `#dpia-requests` (or your preferred channel)
   - Enable "Script Enabled"
   - Set webhook URL to: `https://your-server.com/rdchat/webhook`

3. **Configure Outgoing Webhook (Optional):**
   - For bidirectional communication
   - Set trigger words: `dpia`, `analyze`, `privacy assessment`
   - Set URL: `https://your-server.com/rdchat/webhook`

### Step 4: Deploy Your Server

Ensure your DPIA server is accessible from rdchat:

```bash
# Start the server with rdchat integration
python main_claude.py
```

### Step 5: Test Integration

Use the test endpoint:

```bash
curl -X POST "http://localhost:8080/rdchat/test" \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "test123",
    "user_id": "user123",
    "username": "testuser",
    "channel_id": "channel123",
    "channel_name": "dpia-test",
    "text": "Please analyze this research text: Leica SP8 time-lapse imaging study",
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

## Usage Examples

### 1. Research Text Analysis

**User in rdchat:**
```
@DPIA-AI-Bot Please analyze this research text:
Leica SP8 - Bldg 12 Time-lapse imaging to monitor small molecule distribution in mammalian cells
```

**Bot Response:**
```
🔬 **DPIA Analysis Results**

**📋 Detected Fields:**
• **Project Title**: Leica SP8 Time-lapse Imaging Study (confidence: 1.0)
• **Request Purpose**: Monitor small molecule distribution in mammalian cells (confidence: 1.0)
• **Procedure**: Fluorescence (IF) (confidence: 0.9)
• **Assay Type/Staining Type**: Time-lapse imaging (confidence: 0.9)

**❓ Missing Information:**
• PI
• Pathologist
• Therapeutic Area

**🎯 Next Steps:**
Please provide the missing information to create a complete DPIA case.
You can use `/dpia field <field_name> <value>` to update specific fields.
```

### 2. DPIA Commands

```
/dpia help                    # Show available commands
/dpia analyze <text>          # Analyze research text
/dpia field PI John Smith     # Set specific field
/dpia status                  # Show current analysis status
/dpia create                  # Create DPIA case
```

### 3. Conversational Interaction

```
User: What information do you need for a DPIA assessment?
Bot: For a complete DPIA assessment, I need these mandatory fields:
     • PI (Primary Investigator)
     • Pathologist
     • Therapeutic Area
     • Procedure
     • Assay Type/Staining Type
     • Project Title
     • Request Purpose
     
     You can provide research text and I'll extract what I can automatically! 🔬
```

## Advanced Configuration

### Channel Restrictions

Limit bot responses to specific channels:

```bash
RDCHAT_ALLOWED_CHANNELS=dpia-requests,research-analysis,pathology-review
```

### Keyword Triggers

The bot responds to these keywords by default:
- `dpia`
- `data privacy`
- `privacy assessment`
- `scanning request`
- `pathology`
- `biospecimen`
- `research analysis`
- `claude analysis`

### Custom Bot Avatar

Set a custom avatar for your bot:

```bash
RDCHAT_BOT_AVATAR=https://your-domain.com/assets/dpia-bot-avatar.png
```

## Security Considerations

### 1. Webhook Authentication

Always use webhook tokens:

```bash
RDCHAT_WEBHOOK_TOKEN=secure_random_token_here
```

### 2. Channel Restrictions

Limit bot access to authorized channels:

```bash
RDCHAT_ALLOWED_CHANNELS=authorized-channel-1,authorized-channel-2
```

### 3. Rate Limiting

The integration includes built-in rate limiting to prevent abuse.

### 4. Data Privacy

- Bot only processes messages containing DPIA keywords
- No persistent storage of chat messages
- All analysis data follows existing DPIA security protocols

## Monitoring and Logging

### Health Check

Monitor integration status:

```bash
curl http://localhost:8080/rdchat/status
```

Response:
```json
{
  "status": "active",
  "bot_username": "DPIA-AI-Bot",
  "webhook_configured": true,
  "allowed_channels": ["dpia-requests", "research-analysis"],
  "dpia_keywords": ["dpia", "data privacy", "privacy assessment"]
}
```

### Logs

Monitor these log entries:
- `rdchat_integration.py` - Integration events
- `claude_integration.py` - AI analysis events
- `main_claude.py` - Server events

## Troubleshooting

### Common Issues

1. **Bot not responding:**
   - Check webhook URL is accessible
   - Verify webhook token
   - Ensure bot is mentioned or keywords are used

2. **Authentication errors:**
   - Verify RDCHAT_WEBHOOK_TOKEN
   - Check webhook configuration in rdchat admin

3. **Channel restrictions:**
   - Verify RDCHAT_ALLOWED_CHANNELS setting
   - Ensure bot has access to target channels

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger("rdchat_integration").setLevel(logging.DEBUG)
```

## API Endpoints

### RDChat Integration Endpoints

- `POST /rdchat/webhook` - Main webhook endpoint
- `GET /rdchat/status` - Integration status
- `POST /rdchat/test` - Test integration

### Example Webhook Payload

```json
{
  "message_id": "msg_123",
  "user_id": "user_456",
  "username": "researcher1",
  "channel_id": "ch_789",
  "channel_name": "dpia-requests",
  "text": "@DPIA-AI-Bot analyze this research",
  "timestamp": "2024-01-01T12:00:00Z",
  "type": "message"
}
```

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Server accessible from rdchat
- [ ] Webhook configured in rdchat admin
- [ ] Bot username registered
- [ ] Channel permissions set
- [ ] Test integration working
- [ ] Monitoring enabled
- [ ] Security tokens configured

## Support and Maintenance

### Regular Tasks

1. **Monitor webhook health**
2. **Update authentication tokens**
3. **Review channel permissions**
4. **Check integration logs**
5. **Test bot responses**

### Updates

When updating the integration:

1. Test in development environment
2. Update webhook configuration if needed
3. Deploy during maintenance window
4. Verify functionality post-deployment

## Contact Information

For technical support with the DPIA AI Chatbot rdchat integration:

- **GitHub Repository:** https://github.com/Bhashyem/dpia-ai-chatbot
- **Documentation:** Available in repository README
- **Issues:** Use GitHub Issues for bug reports

---

*This integration guide is part of the DPIA AI Chatbot project. For general DPIA questions, consult your organization's data privacy team.* 