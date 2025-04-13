from flask import session, request, jsonify, render_template_string
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from Services.reservation_services import send_message, create_message, get_gmail_service, generate_email_content
from googleapiclient.discovery import build
import json
import tempfile
import os

class BookReservationHandler:
    def __init__(self):
        pass

    def book_reservation(self, data):
        
        try:
            creds = Credentials(
                token=session['token']['token'],
                refresh_token=session['token']['refresh_token'],
                token_uri=session['token']['token_uri'],
                client_id=session['token']['client_id'],
                client_secret=session['token']['client_secret'],
                scopes=session['token']['scopes']
            )

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

            send_message(service, "me", message)
            
            return jsonify({'message': '✅ Reservation email sent successfully!'})

        except Exception as e:
           return jsonify({'message': f'❌ Failed to send email: {str(e)}'}), 500

