import base64
import io
import os
import requests
from flask import Flask, send_file, request, make_response, redirect, render_template_string

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


# --- 🎨 CLIENT FACING BULK MARKETING DASHBOARD ---
@app.route('/dashboard')
def dashboard():
    html_dashboard = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PGETrack.io Dashboard</title>
        <script src="https://jsdelivr.net"></script>
    </head>
    <body class="bg-slate-900 text-slate-100 min-h-screen flex items-center justify-center p-6">
        <div class="max-w-2xl w-full bg-slate-800 p-8 rounded-2xl shadow-xl border border-slate-700">
            <h1 class="text-3xl font-extrabold text-indigo-400 mb-2">🚀 PGETrack.io Master Tracker</h1>
            <p class="text-slate-400 mb-6 text-sm">Generate single campaign codes to track thousands of automated cold emails.</p>
            
            <div class="space-y-4">
                <div>
                    <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Your Slack Incoming Webhook URL</label>
                    <input type="text" id="slackUrl" placeholder="https://slack.com" 
                           class="w-full bg-slate-900 border border-slate-700 p-3 rounded-lg text-sm text-indigo-300 focus:outline-none focus:border-indigo-500">
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Your Cold Email Platform</label>
                        <select id="emailTool" class="w-full bg-slate-900 border border-slate-700 p-3 rounded-lg text-sm text-slate-300 focus:outline-none focus:border-indigo-500 cursor-pointer">
                            <option value="{{email}}">Instantly / Smartlead ( {{email}} )</option>
                            <option value="{{emailAddress}}">Lemlist ( {{emailAddress}} )</option>
                            <option value="{{contact.email}}">HubSpot ( {{contact.email}} )</option>
                            <option value="{Email}">Apollo / Woodpecker ( {Email} )</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Target Destination Link</label>
                        <input type="text" id="destUrl" placeholder="https://yourcompany.com" 
                               class="w-full bg-slate-900 border border-slate-700 p-3 rounded-lg text-sm focus:outline-none focus:border-indigo-500">
                    </div>
                </div>

                <button onclick="generateTrackingAssets()" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold p-3 rounded-lg mt-2 transition cursor-pointer">
                    Generate Master Campaign Tracking Assets
                </button>

                <div id="outputArea" class="hidden pt-6 border-t border-slate-700 space-y-4">
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-wider text-emerald-400 mb-1">📧 Campaign Master Email Opener Pixel (HTML Tag)</label>
                        <div class="flex gap-2">
                            <input type="text" id="pixelOutput" readonly class="w-full bg-slate-950 p-3 rounded-lg text-xs text-slate-300 font-mono border border-slate-800">
                            <button onclick="copyToClipboard('pixelOutput')" class="bg-slate-700 hover:bg-slate-600 px-4 rounded-lg text-xs font-bold cursor-pointer">Copy</button>
                        </div>
                    </div>
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-wider text-amber-400 mb-1">🎯 Campaign Master Smart Redirect URL Link</label>
                        <div class="flex gap-2">
                            <input type="text" id="linkOutput" readonly class="w-full bg-slate-950 p-3 rounded-lg text-xs text-slate-300 font-mono border border-slate-800">
                            <button onclick="copyToClipboard('linkOutput')" class="bg-slate-700 hover:bg-slate-600 px-4 rounded-lg text-xs font-bold cursor-pointer">Copy</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function generateTrackingAssets() {
                const slackUrl = document.getElementById('slackUrl').value.trim();
                const placeholderTag = document.getElementById('emailTool').value;
                const destUrl = encodeURIComponent(document.getElementById('destUrl').value.trim() || 'https://pgenaijajobs.com.ng');
                
                if(!slackUrl) {
                    alert('Please enter your Slack Webhook URL to configure alerts.');
                    return;
                }

                const encodedShk = btoa(slackUrl).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+\$/, '');
                const baseUrl = window.location.origin;

                const pixelTag = `<img src="${baseUrl}/track/pixel.png?lead=${encodeURIComponent(placeholderTag)}&shk=${encodedShk}" width="1" height="1" style="display:none !important;" alt="" />`;
                const redirectLink = `${baseUrl}/track/click?lead=${encodeURIComponent(placeholderTag)}&url=${destUrl}&shk=${encodedShk}`;

                document.getElementById('pixelOutput').value = pixelTag;
                document.getElementById('linkOutput').value = redirectLink;
                document.getElementById('outputArea').classList.remove('hidden');
            }

            function copyToClipboard(id) {
                const copyText = document.getElementById(id);
                copyText.select();
                navigator.clipboard.writeText(copyText.value);
                alert("Copied directly to clipboard!");
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_dashboard)


# --- 1. TRACKING PIXEL ROUTE ---
@app.route('/track/pixel.png')
def track_pixel():
    user_agent = request.headers.get('User-Agent', '')
    lead_id = request.args.get('lead', 'unknown_lead')
    encoded_shk = request.args.get('shk', '')
    
    if is_automated_bot(user_agent):
        print(f"🤖 BOT FILTERED: Ignored security scan for open on lead '{lead_id}'", flush=True)
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
    destination = request.args.get('url', 'https://pgenaijajobs.com.ng')
    encoded_shk = request.args.get('shk', '')
    
    if is_automated_bot(user_agent):
        print(f"🤖 BOT FILTERED: Ignored security scan for click on lead '{lead_id}'", flush=True)
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
