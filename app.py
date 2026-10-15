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


# --- 🎨 UPGRADED PREMIUM SAAS DASHBOARD ---
@app.route('/dashboard')
def dashboard():
    html_dashboard = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard | PGETrack.io</title>
        <!-- Tailwind CSS & Inter Font Family -->
        <script src="https://jsdelivr.net"></script>
        <link rel="preconnect" href="https://googleapis.com">
        <link rel="preconnect" href="https://gstatic.com" crossorigin>
        <link href="https://googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; }
        </style>
    </head>
    <body class="bg-[#0b0f19] text-slate-100 min-h-screen flex items-center justify-center p-4 selection:bg-indigo-500 selection:text-white">
        
        <!-- Background Decorative Tech Glows -->
        <div class="absolute top-0 left-1/4 w-96 h-96 bg-indigo-600/10 rounded-full filter blur-[100px] pointer-events-none"></div>
        <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-violet-600/10 rounded-full filter blur-[100px] pointer-events-none"></div>

        <div class="max-w-2xl w-full bg-slate-900/60 backdrop-blur-xl p-6 md:p-10 rounded-3xl shadow-2xl border border-slate-800/80 relative z-10 transition-all duration-300">
            
            <!-- Header Group -->
            <div class="text-center mb-8">
                <div class="inline-flex items-center gap-2 bg-indigo-500/10 text-indigo-400 text-xs px-3 py-1.5 rounded-full font-semibold border border-indigo-500/20 mb-3 tracking-wide uppercase">
                    ⚡ Production Ready Node
                </div>
                <h1 class="text-3xl md:text-4xl font-black tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-400 bg-clip-text text-transparent">
                    PGETrack<span class="text-indigo-500">.io</span>
                </h1>
                <p class="text-slate-400 mt-2 text-sm max-w-md mx-auto leading-relaxed">
                    Generate secure, multi-tenant tracking pipelines to monitor automated cold email campaigns instantly.
                </p>
            </div>
            
            <div class="space-y-6">
                <!-- Step 1: Destination Credentials -->
                <div class="bg-slate-950/40 p-5 rounded-2xl border border-slate-800/50">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-500 text-[10px] font-bold text-white">1</span>
                        <label class="block text-xs font-bold uppercase tracking-wider text-slate-300">Alert Destination</label>
                    </div>
                    <input type="text" id="slackUrl" placeholder="Paste your Slack Incoming Webhook URL..." 
                           class="w-full bg-slate-950/80 border border-slate-800 p-3.5 rounded-xl text-sm text-indigo-300 placeholder-slate-600 focus:outline-none focus:border-indigo-500/80 focus:ring-2 focus:ring-indigo-500/10 transition-all font-mono">
                </div>

                <!-- Step 2: Campaign Variables -->
                <div class="bg-slate-950/40 p-5 rounded-2xl border border-slate-800/50">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-500 text-[10px] font-bold text-white">2</span>
                        <label class="block text-xs font-bold uppercase tracking-wider text-slate-300">Campaign Parameters</label>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <span class="block text-[11px] text-slate-500 mb-1 font-medium">Outbound Software</span>
                            <select id="emailTool" class="w-full bg-slate-950/80 border border-slate-800 p-3.5 rounded-xl text-sm text-slate-300 focus:outline-none focus:border-indigo-500/80 focus:ring-2 focus:ring-indigo-500/10 transition-all cursor-pointer">
                                <option value="{{email}}">Instantly / Smartlead ( {{email}} )</option>
                                <option value="{{emailAddress}}">Lemlist ( {{emailAddress}} )</option>
                                <option value="{{contact.email}}">HubSpot ( {{contact.email}} )</option>
                                <option value="{Email}">Apollo / Woodpecker ( {Email} )</option>
                            </select>
                        </div>
                        <div>
                            <span class="block text-[11px] text-slate-500 mb-1 font-medium">Redirect URL Target</span>
                            <input type="text" id="destUrl" placeholder="https://yourcompany.com" 
                                   class="w-full bg-slate-950/80 border border-slate-800 p-3.5 rounded-xl text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/80 focus:ring-2 focus:ring-indigo-500/10 transition-all">
                        </div>
                    </div>
                </div>

                <!-- Action Execution Button -->
                <button onclick="generateTrackingAssets()" class="w-full bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold p-4 rounded-xl shadow-lg shadow-indigo-600/10 hover:shadow-indigo-600/20 active:scale-[0.99] transition-all cursor-pointer text-sm tracking-wide">
                    Compile Tracking Infrastructure
                </button>

                <!-- Step 3: Deployment Outputs (Hidden initially) -->
                <div id="outputArea" class="hidden space-y-5 pt-6 border-t border-slate-800/80 evaluation-animate">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500 text-[10px] font-bold text-slate-950">✓</span>
                        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300">Generated Deployment Assets</h3>
                    </div>

                    <!-- Asset 1: Open Pixel -->
                    <div class="space-y-1.5">
                        <div class="flex justify-between items-center">
                            <span class="text-xs font-medium text-emerald-400 flex items-center gap-1.5">
                                <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                                📧 Stealth Email Opener Code
                            </span>
                        </div>
                        <div class="flex gap-2">
                            <input type="text" id="pixelOutput" readonly class="w-full bg-slate-950/90 border border-slate-800/80 p-3 rounded-xl text-xs text-slate-400 font-mono focus:outline-none">
                            <button id="btn-pixelOutput" onclick="copyToClipboard('pixelOutput')" class="bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 rounded-xl text-xs font-semibold border border-slate-700/60 transition active:scale-95 cursor-pointer whitespace-nowrap">Copy Tag</button>
                        </div>
                    </div>

                    <!-- Asset 2: Tracking Redirect URL -->
                    <div class="space-y-1.5">
                        <div class="flex justify-between items-center">
                            <span class="text-xs font-medium text-amber-400 flex items-center gap-1.5">
                                <span class="h-1.5 w-1.5 rounded-full bg-amber-400 animate-pulse"></span>
                                🎯 Outreach Click Router Link
                            </span>
                        </div>
                        <div class="flex gap-2">
                            <input type="text" id="linkOutput" readonly class="w-full bg-slate-950/90 border border-slate-800/80 p-3 rounded-xl text-xs text-slate-400 font-mono focus:outline-none">
                            <button id="btn-linkOutput" onclick="copyToClipboard('linkOutput')" class="bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 rounded-xl text-xs font-semibold border border-slate-700/60 transition active:scale-95 cursor-pointer whitespace-nowrap">Copy Link</button>
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
alert('Please provide a valid Slack Webhook endpoint destination.');
return;
}
// Encode client configurations into secure base64 blocks
const encodedShk = btoa(slackUrl).replace(/+/g, '-').replace(///g, '_').replace(/=+$/, '');
const baseUrl = window.location.origin;
const pixelTag = <img src="${baseUrl}/track/pixel.png?lead=${encodeURIComponent(placeholderTag)}&shk=${encodedShk}" width="1" height="1" style="display:none !important;" alt="" />;
const redirectLink = ${baseUrl}/track/click?lead=${encodeURIComponent(placeholderTag)}&url=${destUrl}&shk=${encodedShk};
document.getElementById('pixelOutput').value = pixelTag;
document.getElementById('linkOutput').value = redirectLink;
const outputArea = document.getElementById('outputArea');
outputArea.classList.remove('hidden');
outputArea.scrollIntoView({ behavior: 'smooth' });
}
function copyToClipboard(id) {
const copyText = document.getElementById(id);
copyText.select();
navigator.clipboard.writeText(copyText.value);
const btn = document.getElementById('btn-' + id);
const originalText = btn.innerText;
btn.innerText = "✓ Copied";
btn.classList.add('bg-emerald-600/20', 'text-emerald-400', 'border-emerald-500/30');
setTimeout(() => {
btn.innerText = originalText;
btn.classList.remove('bg-emerald-600/20', 'text-emerald-400', 'border-emerald-500/30');
}, 2000);
}



"""response = make_response(html_dashboard)
response.headers['Content-Type'] = 'text/html'
return response

--- 1. TRACKING PIXEL ROUTE ---

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
print(f"🤖 BOT FILTERED: Ignored security scan for click on lead '{lead_id}'", flush=True)
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
