from flask import Flask, render_template, request, jsonify, session
from google.oauth2.credentials import Credentials

from flask import request, render_template_string
from google_auth_oauthlib.flow import Flow
from Backend.mail import get_gmail_service, send_message, create_message
from Backend.email_template import generate_email_content
import os
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/gmail.send']

app = Flask(__name__)
app.secret_key = os.urandom(24)

reservations_data = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/reservations', methods=['GET', 'POST'])
def make_reservation():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            # Handle form data
            data = {
                'name': request.form.get('name', ''),
                'email': request.form.get('email', ''),
                'phone': request.form.get('phone', ''),
                'date': request.form.get('date', ''),
                'time': request.form.get('time', ''),
                'guests': request.form.get('guests', '')
            }
        
        try:
            service = get_gmail_service()
            sender = data['email']
            to = "isfarmohi.im@gmail.com"
            subject = f"New Reservation from {data['name']}"
            
            # Generate HTML content with the data
            message_text = generate_email_content(
                name=data['name'],
                email=data['email'],
                phone=data['phone'],
                date=data['date'],
                time=data['time'],
                guests=data['guests']
            )
            
            message = create_message(sender, to, subject, message_text)
            email_result = send_message(service, "me", message)
            
            return jsonify({
                'message': 'Request received and email sent',
                'data': data,
                'content_type': request.headers.get('Content-Type'),
                'method': request.method,
                'email_status': 'sent' if email_result else 'failed'
            })
            
        except Exception as e:
            return jsonify({
                'message': 'Request received but email failed',
                'data': data,
                'content_type': request.headers.get('Content-Type'),
                'method': request.method,
                'email_error': str(e)
            }), 500
    
    return render_template('reservations.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        print(f"New Message from {name} ({email}): {message}")
    return render_template('contact.html')

@app.route('/oauth2callback')
def oauth2callback():
    print("oauth2callback")
    code = request.args.get('code')

    flow = Flow.from_client_secrets_file(
        'Backend/credentials.json',
        scopes=SCOPES,
        redirect_uri='https://mib3825.pythonanywhere.com/oauth2callback'
    )
    flow.fetch_token(code=code)
    creds = flow.credentials

    # Save credential info into the session
    session['token'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    return render_template_string("""
    <script>
    const formData = JSON.parse(sessionStorage.getItem('reservationFormData'));
    fetch('/send-email-from-user', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formData)
    }).then(res => res.json()).then(data => {
        document.body.innerHTML = '<h2>' + data.message + '</h2>';
    }).catch(err => {
        document.body.innerHTML = '<h2>Something went wrong: ' + err + '</h2>';
    });
    </script>
    """)

@app.route('/send-email-from-user', methods=['POST'])
def send_email_from_user():
    print("send_email_from_user")
    data = request.get_json()

    if 'token' not in session:
        return jsonify({'message': 'Session expired or missing. Please try again.'}), 401

    creds = Credentials(
        token=session['token']['token'],
        refresh_token=session['token']['refresh_token'],
        token_uri=session['token']['token_uri'],
        client_id=session['token']['client_id'],
        client_secret=session['token']['client_secret'],
        scopes=session['token']['scopes']
    )

    try:
        service = build('gmail', 'v1', credentials=creds)

        subject = f"New Reservation from {data['name']}"
        message_text = generate_email_content(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            date=data['date'],
            time=data['time'],
            guests=data['guests']
        )

        message = create_message(
            sender=data['email'],
            to='zakkitchen@gmail.com',
            subject=subject,
            message_text=message_text
        )

        send_result = send_message(service, "me", message)

        return jsonify({'message': '✅ Reservation email sent from your Gmail!'})

    except Exception as e:
        return jsonify({'message': f'❌ Failed to send email: {str(e)}'}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
