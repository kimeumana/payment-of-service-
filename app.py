from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# PayPal API credentials
CLIENT_ID = 'your_client_id_here'  # Replace with your actual client ID
CLIENT_SECRET = 'your_client_secret_here'  # Replace with your actual client secret
PAYPAL_API_URL = 'https://api-m.sandbox.paypal.com'  # Use sandbox for testing

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-payment', methods=['POST'])
def create_payment():
    payment_data = {
        "intent": "sale",
        "redirect_urls": {
            "return_url": "http://localhost:5000/success",
            "cancel_url": "http://localhost:5000/cancel"
        },
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": "20.00",  # Amount to be charged
                "currency": "USD"
            },
            "description": "Payment for services"
        }]
    }

    # Get access token
    auth_response = requests.post(
        f"{PAYPAL_API_URL}/v1/oauth2/token",
        headers={"Accept": "application/json", "Accept-Language": "en_US"},
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={"grant_type": "client_credentials"}
    )
    access_token = auth_response.json().get('access_token')

    # Create payment
    payment_response = requests.post(
        f"{PAYPAL_API_URL}/v1/payments/payment",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
        data=json.dumps(payment_data)
    )

    payment_json = payment_response.json()
    if payment_response.status_code == 201:
        approval_url = next(link['href'] for link in payment_json['links'] if link['rel'] == 'approval_url')
        return jsonify({'approval_url': approval_url})
    else:
        return jsonify(error=payment_json), 403

@app.route('/success')
def success():
    return "Payment was successful!"

@app.route('/cancel')
def cancel():
    return "Payment was canceled."

if __name__ == '__main__':
    app.run(port=5000)
