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


# --- 🎨 STANDALONE DESIGN ENGINE (FIXED STYLING ESCAPES) ---
@app.route('/dashboard')
def dashboard():
    html_dashboard = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard | PGETrack.io</title>
    <style>
        body {
            background-color: #0b0f19;
            color: #f1f5f9;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            margin: 0;
            box-sizing: border-box;
        }
        .container {
            background-color: #1e293b;
            width: 100%;
            max-width: 550px;
            padding: 30px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        .header {
            text-align: center;
            margin-bottom: 25px;
        }
        .badge {
            display: inline-block;
            background-color: rgba(99, 102, 241, 0.15);
            color: #818cf8;
            font-size: 11px;
            font-weight: 700;
            padding: 6px 12px;
            border-radius: 50px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
        }
        h1 {
            font-size: 28px;
            font-weight: 900;
            margin: 0 0 8px 0;
        }
        .logo-accent {
            color: #6366f1;
        }
        .subtitle {
            color: #94a3b8;
            font-size: 13px;
            margin: 0;
            line-height: 1.5;
        }
        .card {
            background-color: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 16px;
            border-radius: 14px;
            margin-bottom: 16px;
            box-sizing: border-box;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
        }
        @media (min-width: 480px) {
            .grid { grid-template-columns: 1fr 1fr; }
        }
        label {
            display: block;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            color: #cbd5e1;
            margin-bottom: 6px;
        }
        input, select {
            width: 100%;
            background-color: #020617;
            border: 1px solid #334155;
            padding: 12px;
            border-radius: 10px;
            color: #f8fafc;
            font-size: 13px;
            box-sizing: border-box;
        }
        input:focus, select:focus {
            border-color: #6366f1;
            outline: none;
        }
        .btn-submit {
            width: 100%;
            background: linear-gradient(to right, #4f46e5, #7c3aed);
            color: white;
            border: none;
            padding: 14px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        }
        .hidden {
            display: none;
        }
        .output-group {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        .output-title-pixel { color: #34d399; font-size: 12px; font-weight: 600; margin-bottom: 6px; display: block;}
        .output-title-link { color: #fbbf24; font-size: 12px; font-weight: 600; margin-bottom: 6px; display: block;}
        .flex-box {
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
        }
        .flex-box input {
            font-family: monospace;
            font-size: 11px;
            background-color: #020617;
            color: #94a3b8;
        }
        .btn-copy {
            background-color: #334155;
            color: #f1f5f9;
            border: none;
            padding: 0 16px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
        }
    </style>
</head>
<body>

    <div class="container">
        <div class="header">
            <div class="badge">⚡ Production Node</div>
            <h1>PGETrack<span class="logo-accent">.io</span></h1>
            <p class="subtitle">Generate dynamic tracking configurations for bulk outbound pipelines instantly.</p>
        </div>

        <div class="card">
            <label>1. Slack Webhook Destination Endpoint</label>
            <input type="text" id="slackUrl" placeholder="https://slack.com...">
        </div>

        <div class="card grid">
            <div>
                <label>2. Sending Platform</label>
                <select id="emailTool">
                    <option value="{{email}}">Instantly / Smartlead ( {{email}} )</option>
                    <option value="{{emailAddress}}">Lemlist ( {{emailAddress}} )</option>
                    <option value="{{contact.email}}">HubSpot ( {{contact.email}} )</option>
                    <option value="{Email}">Apollo / Woodpecker ( {Email} )</option>
                </select>
            </div>
            <div>
                <label>3. Destination Link Target</label>
                <input type="text" id="destUrl" placeholder="https://yourcompany.com">
            </div>
        </div>

        <button onclick="generateTrackingAssets()" class="btn-submit">Compile Campaign Assets</button>

        <div id="outputArea" class="hidden output-group">
            <label style="color:#a78bfa; margin-bottom:12px;">✓ Compiled Assets Infrastructure</label>
            
            <div>
                <span class="output-title-pixel">📧 Stealth Email Opener HTML Code</span>
                <div class="flex-box">
                    <input type="text" id="pixelOutput" readonly>
                    <button id="btn-pixelOutput" onclick="copyToClipboard('pixelOutput')" class="btn-copy">Copy Tag</button>
                </div>
            </div>

            <div>
                <span class="output-title-link">🎯 Campaign Outreach Click Redirect URL Link</span>
                <div class="flex-box">
                    <input type="text" id="linkOutput" readonly>
                    <button id="btn-linkOutput" onclick="copyToClipboard('linkOutput')" class="btn-copy">Copy Link</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        function generateTrackingAssets() {
            const slackUrl = document.getElementById('slackUrl').value.trim();
            const placeholderTag = document.getElementById('emailTool').value;
            const destUrl = encodeURIComponent(document.getElementById('destUrl').value.trim() || 'https://pgenaijajobs.com.ng');
            
            if(!slackUrl) { alert('Please enter a valid Slack endpoint.'); return; }
            
            const encodedShk = btoa(slackUrl).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+\$/, '');
            const baseUrl = window.location.origin;
            
            // Fixed escaping: Added backslashes so Python handles strings safely
            document.getElementById('pixelOutput').value = '<img src="' + baseUrl + '/track/pixel.png?lead=' + encodeURIComponent(placeholderTag) + '&shk=' + encodedShk + '" width="1" height="1" style="display:none !important;" />';
            document.getElementById('linkOutput').value = baseUrl + '/track/click?lead=' + encodeURIComponent(placeholderTag) + '&url=' + destUrl + '&shk=' + encodedShk;
            document.getElementById('outputArea').classList.remove('hidden');
        }

        function copyToClipboard(id) {
            const copyText = document.getElementById(id);
            copyText.select();
            navigator.clipboard.writeText(copyText.value);
            
            const btn = document.getElementById('btn-' + id);
            const oldText = btn.innerText;
            btn.innerText = "✓ Copied";
            
            setTimeout(() => {
                btn.innerText = oldText;
            }, 2000);
        }
    </script>
</body>
</html>"""
    response = make_response(html_dashboard)
    response.headers['Content-Type'] = 'text/html'
    return response


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
message = f"📧 Email Opened! Lead {lead_id} has opened your outreach email template."
send_slack_notification(slack_url, message)
pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
pixel_data = base64.b64decode(pixel_b64)
response = make_response(send_file(io.BytesIO(pixel_data), mimetype='image/png'))
response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
return response

--- 2. TRACKING LINK ROUTE ---

@app.route('/track/click')
def track_click():
user_agent = request.headers.get('User-Agent', '')
lead_id = request.args.get('lead', 'unknown_lead')
destination = request.args.get('url', 'https://pgenaijajobs.com.ng')
encoded_shk = request.args.get('shk', '')
if is_automated_bot(user_agent):
print(f"🤖 BOT FILTERED: Ignored click on lead '{lead_id}'", flush=True)
else:
print(f"🎯 HUMAN CLICK: Engagement captured for lead '{lead_id}'!", flush=True)
slack_url = get_dynamic_slack_url(encoded_shk)
if slack_url:
message = f"🎯 Link Clicked! Lead {lead_id} clicked your campaign tracking link and landed on: {destination}"
send_slack_notification(slack_url, message)
return redirect(destination)
@app.route('/')
def home():
return "Global SaaS Tracking Server is live! Go to /dashboard to generate links. 🚀"
if name == 'main':
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
