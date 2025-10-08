from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os

load_dotenv()

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
EMAIL_TO = os.getenv("EMAIL_TO")  # Deine Zieladresse z. B. bestellungen@xyz.de
SENDER_NAME = os.getenv("SENDER_NAME", "Partyservice Alexa")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@partyservice.com")

app = Flask(__name__)
CORS(app)

@app.route("/send", methods=["POST"])
def send_mail():
    data = request.json

    cart = data.get("cart", {})
    message = data.get("message", "")
    email = data.get("email", "")

    # E-Mail check
    if not email or "@" not in email:
        return jsonify({"status": "error", "message": "Ungültige E-Mail"}), 400

    bestellung = "\n".join([f"{item}: {qty}" for item, qty in cart.items()])
    inhalt = f"""
Neue Bestellung von: {email}

Nachricht:
{message}

Warenkorb:
{bestellung}
"""

    payload = {
        "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "to": [{"email": EMAIL_TO}],
        "subject": "Neue Bestellung über das Formular",
        "textContent": inhalt
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
