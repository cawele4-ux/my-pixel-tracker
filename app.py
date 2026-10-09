import base64
import io
import os
import requests  # Essential for sending data to Make.com
from flask import Flask, send_file, request, make_response, redirect

app = Flask(__name__)

# 🔄 DYNAMIC WEBHOOK: Looks for Render's environment variable first.
# If it doesn't find one, it falls back to your default Make configuration.
CRM_WEBHOOK_URL = os.environ.get(
    "CRM_WEBHOOK_URL", 
    "https://make.com"
)

# --- BOT FILTER CONSTANTS & UTILITIES ---
BOT_USER_AGENTS = ["bot", "safelinks", "security", "scan", "datadog", "microsoft", "cloud"]

def is_automated_bot(user_agent_string):
    ua_lower = user_agent_string.lower()
    return any(bot_keyword in ua_lower for bot_keyword in BOT_USER_AGENTS)


@app.route('/')
def home():
    return "Tracking server is up and running! 🚀"


# --- 1. TRACKING PIXEL (OPENS WITH BOT FILTER INTEGRATED) ---
@app.route('/track/pixel.png')
def track_pixel():
    # 🕵️ Check if the traffic is coming from a real human or a corporate security scanner
    user_agent = request.headers.get('User-Agent', '')
    lead_id = request.args.get('lead', 'unknown_lead')
    
    # 🛡️ BOT GUARD: If it's a security bot, give it the image silently and stop execution
    if is_automated_bot(user_agent):
        print(f"🤖 BOT FILTERED: Ignored security scan for open on lead '{lead_id}'", flush=True)
    else:
        # 👤 HUMAN ENTRANCE: Only send to Make.com if a real human opened it
        print(f"🔥 ALERT: Lead '{lead_id}' just opened the email!", flush=True)
        payload = {"event": "Email Opened", "lead": lead_id}
        try:
            requests.post(CRM_WEBHOOK_URL, json=payload, timeout=2)
        except Exception as e:
            print(f"CRM Sync Error (Open): {e}", flush=True)

    # Return the invisible tracking pixel seamlessly to either human or bot
    pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    pixel_data = base64.b64decode(pixel_b64)
    response = make_response(send_file(io.BytesIO(pixel_data), mimetype='image/png'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# --- 2. TRACKING LINK (CLICKS WITH BOT FILTER INTEGRATED) ---
@app.route('/track/click')
def track_click():
    # 🕵️ Check if the click is from a human or a link scanner bot checking safety
    user_agent = request.headers.get('User-Agent', '')
    lead_id = request.args.get('lead', 'unknown_lead')
    destination = request.args.get('url', 'https://pgenaijajobs.com.ng')
    
    # 🛡️ BOT GUARD: If a security scanner clicks the link, skip sending to Make.com
    if is_automated_bot(user_agent):
        print(f"🤖 BOT FILTERED: Ignored corporate link scan for lead '{lead_id}'", flush=True)
    else:
        # 👤 HUMAN ENTRANCE: Only notify your client if a real human clicked it
        print(f"🎯 CLICK ALERT: Lead '{lead_id}' clicked! Sending to: {destination}", flush=True)
        
        # Send "Click" notification to the CRM
        payload = {"event": "Link Clicked", "lead": lead_id, "destination": destination}
        try:
            requests.post(CRM_WEBHOOK_URL, json=payload, timeout=2)
        except Exception as e:
            print(f"CRM Sync Error (Click): {e}", flush=True)
        
    # Real human or bot scanner, we still always redirect them to the final destination safely
    return redirect(destination)


# --- 3. EXECUTION BLOCK (MUST REMAIN AT THE ABSOLUTE BOTTOM) ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
