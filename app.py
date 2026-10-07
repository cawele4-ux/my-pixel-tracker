import base64
import io
from flask import Flask, send_file, request, make_response

app = Flask(__name__)

@app.route('/track/pixel.png')
def track_pixel():
    # 1. Grab the tracking ID from the email URL (e.g., ?lead=john)
    lead_id = request.args.get('lead', 'unknown_lead')
    
    # 2. Print the open event to your server logs
    print(f"🔥 ALERT: Lead '{lead_id}' just opened the email!", flush=True)
    
    # 3. Standard base64 representation of a 1x1 transparent PNG pixel
    pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    pixel_data = base64.b64decode(pixel_b64)
    
    # 4. Turn it into a response and explicitly tell Gmail NOT to cache it
    response = make_response(send_file(io.BytesIO(pixel_data), mimetype='image/png'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  
@app.route('/')
def home():
    return "Tracking server is up and running! 🚀"
    
from flask import redirect # Ensure redirect is imported at the top

@app.route('/track/click')
def track_click():
    # 1. Grab the lead ID and the final URL destination from the link parameters
    lead_id = request.args.get('lead', 'unknown_lead')
    destination = request.args.get('url', 'https://google.com') # fallback if url is missing
    
    # 2. Log the click event instantly to your Render terminal
    print(f"🎯 CLICK ALERT: Lead '{lead_id}' clicked a link! Sending to: {destination}", flush=True)
    
    # 3. Redirect the user seamlessly to the actual website
    return redirect(destination)
    
