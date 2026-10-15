import base64
import io
import os
import requests
from flask import Flask, send_file, request, make_response, redirect

app = Flask(__name__)

# --- BOT FILTER CONSTANTS & UTILITIES ---
BOT_USER_AGENTS = ["bot", "safelinks", "security", "scan", "datadog", "microsoft", "cloud"]

def is_automated_bot(user_agent_string):
    ua_lower = user_agent_string.lower()
    return any(bot_keyword in ua_lower for bot_keyword in BOT_USER_AGENTS)

def get_dynamic_slack_url(encoded_shk):
    if not encoded_shk:
        return None
    try:
        decoded_bytes = base64.urlsafe_b64decode(encoded_shk + '=' * (-len(encoded_shk) % 4))
        return decoded_bytes.decode('utf-8')
    except Exception:
        return None

def send_slack_notification(slack_url, message_text):
    try:
        payload = {"text": message_text}
        requests.post(slack_url, json=payload, timeout=2)
    except Exception as e:
        print(f"❌ Direct Slack Notification Error: {e}", flush=True)


# --- 🎨 DYNAMIC HTML LOADER ROUTE ---
@app.route('/dashboard')
def dashboard():
    try:
        # Python reads the clean file directly from the directory
        with open('dashboard.html', 'r', encoding='utf-8') as file:
            html_content = file.read()
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        return response
    except Exception as e:
        return f"Dashboard missing file error: {e}", 500


# --- 1. TRACKING PIXEL ROUTE ---
@app.route('/track/pixel.png')
def track_pixel():
    user_agent = request.headers.get('User-Agent', '')
    lead_id = request.args.get('lead', 'unknown_lead')
    encoded_shk = request.args.get('shk', '')
    
    if is_automated_bot(user_agent):
        print(f"🤖 BOT FILTERED: Ignored open on lead '{lead_id}'", flush=True)
    else:
        print(f"🔥 HUMAN OPEN: Email opened by lead: '{lead_id}'", flush=True)
        slack_url = get_dynamic_slack_url(encoded_shk)
        if slack_url:
            message = f"📧 *Email Opened!* Lead *{lead_id}* has opened your outreach email template."
            send_slack_notification(slack_url, message)

    pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    pixel_data = base64.b64decode(pixel_b64)
    response = make_response(send_file(io.BytesIO(pixel_data), mimetype='image/png'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    return response


# --- 2. TRACKING LINK ROUTE ---
@app.route('/track/click')
def track_click():
    user_agent = request.headers.get('User-Agent', '')
    lead_id = request.args.get('lead', 'unknown_lead')
    destination = request.args.get('url', 'https://google.com')
    encoded_shk = request.args.get('shk', '')
    
    if is_automated_bot(user_agent):
        print(f"🤖 BOT FILTERED: Ignored click on lead '{lead_id}'", flush=True)
    else:
        print(f"🎯 HUMAN CLICK: Engagement captured for lead '{lead_id}'!", flush=True)
        slack_url = get_dynamic_slack_url(encoded_shk)
        if slack_url:
            message = f"🎯 *Link Clicked!* Lead *{lead_id}* clicked your campaign tracking link and landed on: {destination}"
            send_slack_notification(slack_url, message)
            
    return redirect(destination)


@app.route('/')
def home():
    return "Global SaaS Tracking Server is live! Go to /dashboard to generate links. 🚀"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
