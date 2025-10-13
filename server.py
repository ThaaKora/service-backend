from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

# .env
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS = os.getenv("SENDER_PASS") 
EMAIL_TO = os.getenv("EMAIL_TO")

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

    try:
        msg = MIMEText(text)
        msg["Subject"] = "Neue Bestellung über das Formular"
        msg["From"] = f"Partyservice Alexa <{SENDER_EMAIL}>"
        msg["To"] = EMAIL_TO

        # Gmail SMTP-Verbindung (SSL)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASS)
            server.send_message(msg)

        return jsonify({"status": "ok"})
    except Exception as e:
        print("Fehler beim Senden:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
