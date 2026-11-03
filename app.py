import os
import requests
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)

# Configured with your Gemini API Key
GEMINI_API_KEY = "AQ.Ab8RN6JJEuLRzKUXa4NeQBrSEAGdfOyk3f2u2xONkJUNeQSlQw"
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Configured with your Meta / Instagram / Facebook Token & Updated Verify Token
VERIFY_TOKEN = "imran123"
ACCESS_TOKEN = "EAAQmsTG8qQ4BS9kbcnPTGPxBSSHaktnQKTOdyWFwqtHd82qkHZCFBZAZCevyZAREFaUUwKpE3f1ZApA0gu04Cz7cShLSh3lYAtMfg8ZCTfXxNYo7B40CGsaItfv3T0szDIyQjZCjOvEiucF5trllyaHmH0GUBoNSe3jmFpOu83e5YfXokg1Bc8D5nlIApGZA9ZANwGflpLzXlf7quOZBXoDDR7N1Em48mj0G8I5FVgXMFnmu4FYE0f2fJzygZDZD"
GRAPH_API_VERSION = "v21.0"

def generate_gemini_response(user_message):
    """Passes customer query to Gemini with system instructions for your e-commerce business."""
    try:
        system_instruction = (
            "You are an automated e-commerce customer support assistant for a tech and electronics importer. "
            "Keep answers helpful, polite, concise, and professional."
        )
        
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
            config={
                "system_instruction": system_instruction,
                "max_output_tokens": 300,
            }
        )
        return response.text
    except Exception as e:
        print(f"Error generating Gemini response: {e}")
        return "Thanks for reaching out! A representative will get back to you shortly."

@app.route("/", methods=["GET"])
def home_test_page():
    """Browser testing dashboard to check how Gemini responds to customer queries."""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gemini Multi-Platform Bot Simulator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; background: #f9f9f9; }
            .chat-box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            textarea { width: 100%; height: 100px; padding: 10px; margin-top: 10px; border-radius: 4px; border: 1px solid #ccc; }
            button { background: #0095f6; color: white; border: none; padding: 10px 20px; margin-top: 10px; border-radius: 4px; cursor: pointer; font-weight: bold; }
            button:hover { background: #0077c2; }
            .response { margin-top: 20px; padding: 15px; background: #eef6fc; border-left: 4px solid #0095f6; border-radius: 4px; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <div class="chat-box">
            <h2>🤖 Gemini Multi-Platform Bot Simulator</h2>
            <p>Your API keys are configured! Test how your AI assistant replies right here.</p>
            <form method="POST" action="/test-chat">
                <label>Simulated Customer Message:</label>
                <textarea name="message" placeholder="e.g., Do you have Android TV boxes in stock?">Do you have Android TV boxes in stock?</textarea>
                <br>
                <button type="submit">Generate AI Reply</button>
            </form>
            {% if reply %}
                <div class="response"><strong>Gemini's Auto-Reply:</strong><br>{{ reply }}</div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, reply=None)

@app.route("/test-chat", methods=["POST"])
def test_chat():
    user_message = request.form.get("message", "")
    ai_reply = generate_gemini_response(user_message)
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gemini Multi-Platform Bot Simulator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; background: #f9f9f9; }
            .chat-box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            textarea { width: 100%; height: 100px; padding: 10px; margin-top: 10px; border-radius: 4px; border: 1px solid #ccc; }
            button { background: #0095f6; color: white; border: none; padding: 10px 20px; margin-top: 10px; border-radius: 4px; cursor: pointer; font-weight: bold; }
            button:hover { background: #0077c2; }
            .response { margin-top: 20px; padding: 15px; background: #eef6fc; border-left: 4px solid #0095f6; border-radius: 4px; white-space: pre-wrap; }
            a { display: inline-block; margin-top: 15px; color: #0095f6; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="chat-box">
            <h2>🤖 Gemini Multi-Platform Bot Simulator</h2>
            <p><strong>You asked:</strong> {{ user_message }}</p>
            <form method="POST" action="/test-chat">
                <label>Simulated Customer Message:</label>
                <textarea name="message">{{ user_message }}</textarea>
                <br>
                <button type="submit">Generate AI Reply</button>
            </form>
            <div class="response"><strong>Gemini's Auto-Reply:</strong><br>{{ reply }}</div>
            <br><a href="/">← Reset</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, user_message=user_message, reply=ai_reply)

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Handles initial webhook verification handshake from Meta (Instagram & Facebook)."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Verification failed", 403
    return "Invalid request", 400

@app.route("/webhook", methods=["POST"])
def handle_incoming_message():
    """Live production webhook endpoint that handles incoming Instagram and Facebook messages."""
    body = request.get_json()
    print("Incoming webhook payload:", body)

    # 1. Handle Instagram Messaging Events
    if body.get("object") == "instagram":
        for entry in body.get("entry", []):
            for event in entry.get("messaging", []):
                if "message" in event and "text" in event["message"]:
                    sender_id = event["sender"]["id"]
                    message_text = event["message"]["text"]
                    ai_reply = generate_gemini_response(message_text)
                    send_meta_message(sender_id, ai_reply)

    # 2. Handle Facebook Messenger Events
    elif body.get("object") == "page":
        for entry in body.get("entry", []):
            for event in entry.get("messaging", []):
                if "message" in event and "text" in event["message"]:
                    sender_id = event["sender"]["id"]
                    message_text = event["message"]["text"]
                    ai_reply = generate_gemini_response(message_text)
                    send_meta_message(sender_id, ai_reply)

    return jsonify({"status": "EVENT_RECEIVED"}), 200

def send_meta_message(recipient_id, message_text):
    """Sends responses back via Meta Graph API (works for both Instagram and Facebook Page messaging)."""
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "access_token": ACCESS_TOKEN
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Failed to send Meta message: {response.text}")

@app.route("/check-youtube-comments", methods=["GET"])
def check_youtube_comments():
    """Fetches recent comments on your YouTube channel and replies using Gemini."""
    channel_id = "UC6Rtwzh0YOeo9526B2xU_gg"  # Replace with your YouTube Channel ID
    api_key = GEMINI_API_KEY              # Or your YouTube Data API Key

    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&channelId={channel_id}&key={api_key}"
    res = requests.get(url)

    if res.status_code == 200:
        comments_data = res.json()
        for item in comments_data.get("items", []):
            comment_snippet = item["snippet"]["topLevelComment"]["snippet"]
            comment_text = comment_snippet["textDisplay"]
            comment_id = item["id"]

            # Generate Gemini reply tailored for your brand
            ai_reply = generate_gemini_response(f"Reply to this YouTube comment professionally: {comment_text}")
            
            # (Optional) You can add comments.insert logic here using YouTube API to post `ai_reply` back to `comment_id`

        return jsonify({"status": "YouTube comments processed successfully"}), 200
    return jsonify({"error": "Failed to fetch YouTube comments"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
