# 🚀 DPIA Context Upload - Coworker Access Guide

## 🎯 Quick Access Options

### Option 1: Use Custom API Parameter (Immediate Solution)
If the DPIA server is running on a specific machine, you can access it by adding the API parameter to the URL:

```
https://bhashyem.github.io/dpia-ai-chatbot/context_upload.html?api=http://SERVER_IP:8080
```

**Example:**
- If the server is running on IP `192.168.1.100`: 
  ```
  https://bhashyem.github.io/dpia-ai-chatbot/context_upload.html?api=http://192.168.1.100:8080
  ```

### Option 2: Local Server Access (Same Network)
If you're on the same network as the server:

1. **Find the server's IP address** (ask the person running the server)
2. **Use the URL format above** with the correct IP
3. **Make sure the server allows external connections** (not just localhost)

### Option 3: Ngrok Tunnel (Temporary Public Access)
If the server owner sets up ngrok:

1. Server owner runs: `ngrok http 8080`
2. Ngrok provides a public URL like: `https://abc123.ngrok.io`
3. Use: `https://bhashyem.github.io/dpia-ai-chatbot/context_upload.html?api=https://abc123.ngrok.io`

## 🔧 For Server Owners

### Make Server Accessible to Coworkers

1. **Find your IP address:**
   ```bash
   # On Mac/Linux:
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # On Windows:
   ipconfig
   ```

2. **Update server to bind to all interfaces:**
   In your `main_claude.py`, change:
   ```python
   uvicorn.run(app, host="127.0.0.1", port=8080)
   ```
   To:
   ```python
   uvicorn.run(app, host="0.0.0.0", port=8080)
   ```

3. **Share the URL with coworkers:**
   ```
   https://bhashyem.github.io/dpia-ai-chatbot/context_upload.html?api=http://YOUR_IP:8080
   ```

### Deploy to Cloud (Permanent Solution)

**Recommended platforms:**
- **Railway**: Easy deployment, free tier
- **Render**: Simple setup, good for FastAPI
- **Heroku**: Popular choice, free tier available
- **DigitalOcean App Platform**: Reliable, affordable

**Steps:**
1. Deploy your DPIA server to chosen platform
2. Get the deployment URL (e.g., `https://your-app.railway.app`)
3. Update the GitHub Pages site to use the production URL
4. Coworkers can access directly without URL parameters

## 🛠️ Troubleshooting

### "Failed to load context status" Error
- **Cause**: Can't connect to the API server
- **Solution**: Check the API endpoint URL and server status

### CORS Errors
- **Cause**: Browser blocking cross-origin requests
- **Solution**: Server needs CORS configuration (already included in the DPIA server)

### Network Connection Issues
- **Cause**: Firewall or network restrictions
- **Solution**: Check firewall settings, use VPN if needed

## 📞 Getting Help

1. **Check the browser console** (F12 → Console) for error messages
2. **Verify the API endpoint** is shown correctly on the page
3. **Test the server directly** by visiting the API URL in browser
4. **Contact the server administrator** if connection issues persist

## 🔒 Security Notes

- The context upload functionality requires an active DPIA server
- Uploaded content is stored temporarily for analysis enhancement
- Use secure connections (HTTPS) when possible
- Don't share sensitive data through public ngrok tunnels

---

**Need immediate access?** Ask the server owner to:
1. Find their IP address
2. Share the custom URL with you
3. Ensure their server accepts external connections 