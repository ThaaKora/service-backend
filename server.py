from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()


EMAIL_TO = os.getenv("EMAIL_TO")  
BREVO_API_KEY = os.getenv("BREVO_API_KEY")  

app = Flask(__name__)
CORS(app)

@app.route("/send", methods=["POST"])
def send_mail():
    data = request.json
    cart = data.get("cart", {})
    message = data.get("message", "")
    email = data.get("email", "")

    
    if not email or "@" not in email:
        return jsonify({"status": "error", "message": "Ungültige E-Mail"}), 400

    
    bestellung = "\n".join([f"{item}: {menge}" for item, menge in cart.items()])
    text = f"""
Neue Bestellung von: {email}

Nachricht:
{message}

Warenkorb:
{bestellung}
"""

    
    payload = {
        "sender": {
            "name": "Partyservice Alexa",
            "email": "noreply@brevo.email"
        },
        "to": [
            {"email": EMAIL_TO}
        ],
        "subject": "Neue Bestellung über das Formular",
        "textContent": text
    }

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    try:
        response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        response.raise_for_status()
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Fehler beim Senden:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
