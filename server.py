from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

# .env laden
load_dotenv()

# Umgebungsvariablen
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_SMTP = os.getenv("EMAIL_SMTP", "smtp-relay.brevo.com")  # Standard für Brevo
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))  # TLS Port
EMAIL_TO   = os.getenv("EMAIL_TO", EMAIL_USER)

app = Flask(__name__)
CORS(app)

@app.route("/send", methods=["POST"])
def send_mail():
    data = request.json

    cart = data.get("cart", {})
    message = data.get("message", "")
    email = data.get("email", "")

    # Einfache E-Mail-Validierung
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"status": "error", "message": "Ungültige oder fehlende E-Mail-Adresse"}), 400

    bestellung = "\n".join([f"{item}: {menge}" for item, menge in cart.items()])
    text = f"""Neue Anfrage von {email}

Nachricht:
{message}

Bestellung:
{bestellung}
"""

    msg = EmailMessage()
    msg.set_content(text)
    msg["Subject"] = "Neue Anfrage über das Bestellformular"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    try:
        with smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT) as smtp:
    smtp.starttls()
    smtp.login(EMAIL_USER, EMAIL_PASS)
    smtp.send_message(msg)

        return jsonify({"status": "ok"})
    except Exception as e:
        print("Fehler beim Versand:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
