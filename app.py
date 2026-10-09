import base64
import io
import os
import requests  # <-- NEW: Essential for sending data to your CRM
from flask import Flask, send_file, request, make_response, redirect

app = Flask(__name__)

# 🔄 DYNAMIC WEBHOOK: Looks for Render's environment variable first.
# If it doesn't find one, it falls back to your original client URL.
CRM_WEBHOOK_URL = os.environ.get(
    "CRM_WEBHOOK_URL", 
    "https://hook.us2.make.com/s8vgkb42877ntaonrf609ktri6f5uzog"
)

@app.route('/')
def home():
    return "Tracking server is up and running! 🚀"

# --- 1. TRACKING PIXEL (OPENS) ---
@app.route('/track/pixel.png')
def track_pixel():
    lead_id = request.args.get('lead', 'unknown_lead')
    print(f"🔥 ALERT: Lead '{lead_id}' just opened the email!", flush=True)
    
    # NEW: Send "Open" notification to the CRM
    payload = {"event": "Email Opened", "lead": lead_id}
    try:
        requests.post(CRM_WEBHOOK_URL, json=payload, timeout=2)
    except Exception as e:
        print(f"CRM Sync Error (Open): {e}", flush=True)

    # Return the invisible pixel
    pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    pixel_data = base64.b64decode(pixel_b64)
    response = make_response(send_file(io.BytesIO(pixel_data), mimetype='image/png'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# --- 2. TRACKING LINK (CLICKS) ---
@app.route('/track/click')
def track_click():
    lead_id = request.args.get('lead', 'unknown_lead')
    destination = request.args.get('url', 'https://pgenaijajobs.com.ng')
    print(f"🎯 CLICK ALERT: Lead '{lead_id}' clicked! Sending to: {destination}", flush=True)
    
    # NEW: Send "Click" notification to the CRM
    payload = {"event": "Link Clicked", "lead": lead_id, "destination": destination}
    try:
        requests.post(CRM_WEBHOOK_URL, json=payload, timeout=2)
    except Exception as e:
        print(f"CRM Sync Error (Click): {e}", flush=True)
        
    return redirect(destination)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# --- 3. BOT FILTER UTILITIES ---
BOT_USER_AGENTS = ["bot", "safelinks", "security", "scan", "datadog", "microsoft", "cloud"]

def is_automated_bot(user_agent_string):
    ua_lower = user_agent_string.lower()
    return any(bot_keyword in ua_lower for bot_keyword in BOT_USER_AGENTS)
