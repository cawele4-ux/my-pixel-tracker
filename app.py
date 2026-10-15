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


# --- 🎨 UPGRADED PREMIUM SAAS DASHBOARD ---
@app.route('/dashboard')
def dashboard():
    html_dashboard = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard | PGETrack.io</title>
    <script src="https://jsdelivr.net"></script>
    <link href="https://googleapis.com" rel="stylesheet">
    <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-[#0b0f19] text-slate-100 min-h-screen flex items-center justify-center p-4">
    <div class="absolute top-0 left-1/4 w-96 h-96 bg-indigo-600/10 rounded-full filter blur-[100px] pointer-events-none"></div>
    <div class="max-w-2xl w-full bg-slate-900/60 backdrop-blur-xl p-6 md:p-10 rounded-3xl shadow-2xl border border-slate-800/80 relative z-10">
        <div class="text-center mb-8">
            <div class="inline-flex items-center bg-indigo-500/10 text-indigo-400 text-xs px-3 py-1.5 rounded-full font-semibold border border-indigo-500/20 mb-3 uppercase tracking-wide">⚡ Production Ready Node</div>
            <h1 class="text-3xl md:text-4xl font-black tracking-tight bg-gradient-to-r from-white to-indigo-400 bg-clip-text text-transparent">PGETrack<span class="text-indigo-500">.io</span></h1>
            <p class="text-slate-400 mt-2 text-sm leading-relaxed">Generate dynamic multi-tenant tracking configurations instantly.</p>
        </div>
        <div class="space-y-6">
            <div class="bg-slate-950/40 p-5 rounded-2xl border border-slate-800/50">
                <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">1. Slack Webhook Destination Endpoint</label>
                <input type="text" id="slackUrl" placeholder="https://slack.com..." class="w-full bg-slate-950/80 border border-slate-800 p-3.5 rounded-xl text-sm text-indigo-300 font-mono focus:outline-none focus:border-indigo-500">
            </div>
            <div class="bg-slate-950/40 p-5 rounded-2xl border border-slate-800/50 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">2. Seding Platform</label>
                    <select id="emailTool" class="w-full bg-slate-950/80 border border-slate-800 p-3.5 rounded-xl text-sm text-slate-300 focus:outline-none">
                        <option value="{{email}}">Instantly / Smartlead ( {{email}} )</option>
                        <option value="{{emailAddress}}">Lemlist ( {{emailAddress}} )</option>
                        <option value="{{contact.email}}">HubSpot ( {{contact.email}} )</option>
                        <option value="{Email}">Apollo / Woodpecker ( {Email} )</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">3. Destination Link Target</label>
                    <input type="text" id="destUrl" placeholder="https://yourcompany.com" class="w-full bg-slate-950/80 border border-slate-800 p-3.5 rounded-xl text-sm">
                </div>
            </div>
            <button onclick="generateTrackingAssets()" class="w-full bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold p-4 rounded-xl shadow-lg active:scale-95 transition-all cursor-pointer text-sm uppercase tracking-wider">Compile Campaign Code</button>
            <div id="outputArea" class="hidden space-y-4 pt-6 border-t border-slate-800/80">
                <div class="space-y-1">
                    <span class="text-xs font-medium text-emerald-400">📧 Stealth Email Opener HTML Code</span>
                    <div class="flex gap-2"><input type="text" id="pixelOutput" readonly class="w-full bg-slate-950/90 border border-slate-800 p-3 rounded-xl text-xs font-mono"><button id="btn-pixelOutput" onclick="copyToClipboard('pixelOutput')" class="bg-slate-800 px-4 rounded-xl text-xs font-semibold cursor-pointer whitespace-nowrap">Copy Tag</button></div>
                </div>
                <div class="space-y-1">
                    <span class="text-xs font-medium text-amber-400">🎯 Campaign Outreach Click Redirect URL Link</span>
                    <div class="flex gap-2"><input type="text" id="linkOutput" readonly class="w-full bg-slate-950/90 border border-slate-800 p-3 rounded-xl text-xs font-mono"><button id="btn-linkOutput" onclick="copyToClipboard('linkOutput')" class="bg-slate-800 px-4 rounded-xl text-xs font-semibold cursor-pointer whitespace-nowrap">Copy Link</button></div>
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
            document.getElementById('pixelOutput').value = `<img src="${baseUrl}/track/pixel.png?lead=\${encodeURIComponent(placeholderTag)}&shk=\${encodedShk}" width="1" height="1" style="display:none !important;" />`;
            document.getElementById('linkOutput').value = `\${baseUrl}/track/click?lead=\${encodeURIComponent(placeholderTag)}&url=\${destUrl}&shk=\${encodedShk}`;
            document.getElementById('outputArea').classList.remove('hidden');
        </div>
        function copyToClipboard(id) {
            const copyText = document.getElementById(id); copyText.select(); navigator.clipboard.writeText(copyText.value);
            const btn = document.getElementById('btn-' + id); const old = btn.innerText; btn.innerText = "✓ Copied";
            setTimeout(() => { btn.innerText = old; }, 2000);
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
