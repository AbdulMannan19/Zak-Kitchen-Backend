from flask import session, request, jsonify, render_template, render_template_string
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
                to='mohiisfar@gmail.com',
                subject=subject,
                message_text=message_text
            )

            send_message(service, "me", message)
            print("Message sent successfully")
            
            return render_template_string("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                <title>Reservation Request Received - Zak's Kitchen</title>
                <link href="https://fonts.googleapis.com/css2?family=Cardo:ital@0;1&family=Great+Vibes&display=swap" rel="stylesheet">
                <style>
                    body {
                        margin: 0;
                        padding: 0;
                        font-family: 'Cardo', serif;
                        background-color: #d1830f;
                        color: #1a1a1a;
                        text-align: center;
                        min-height: 100vh;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    }
                    .container {
                        padding: 40px 20px;
                        max-width: 800px;
                        margin: 0 auto;
                        position: relative;
                    }
                    .stars {
                        font-size: 1.5em;
                        color: black;
                        margin: 20px 0;
                        letter-spacing: 5px;
                    }
                    .header {
                        font-family: 'Great Vibes', cursive;
                        font-size: 2.8em;
                        color: black;
                        margin-bottom: 20px;
                    }
                    .title {
                        font-weight: bold;
                        font-size: 1.2em;
                        margin: 20px 0;
                    }
                    .content {
                        margin: 30px 0;
                    }
                    .content p {
                        margin: 15px 0;
                        font-size: 1.1em;
                        line-height: 1.6;
                    }
                    .contact-info {
                        margin-top: 30px;
                        font-size: 1.1em;
                    }
                    .contact-info p {
                        margin: 10px 0;
                    }
                    .footer {
                        margin-top: 30px;
                        font-weight: bold;
                    }
                    a {
                        color: black;
                        text-decoration: none;
                    }
                    a:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="stars">✦✦✦✦✦</div>
                    
                    <div class="header">With Gratitude...</div>

                    <div class="title">
                        We've Received Your Reservation Request!
                    </div>

                    <div class="content">
                        <p>Thank you for reaching out to Zak's Kitchen.</p>
                        <p>We have received your email for reservation. We will contact you shortly regarding available slots.</p>
                        <p>Please check your inbox for confirmation and further details. We're excited at the possibility of welcoming you soon!</p>
                        
                        <h3>Warm Regards</h3>
                    </div>

                    <div class="contact-info">
                        <p>Web: <a href="https://www.ZaksKitchenAu.com">www.ZaksKitchenAu.com</a></p>
                        <p>Email: <a href="mailto:info@zakskitchenau.com">info@zakskitchenau.com</a></p>
                        <p>Contact: 041-102-0566</p>
                    </div>

                    <div class="footer">
                        Zak's Kitchen Team
                    </div>

                    <div class="stars">✦✦✦✦✦</div>
                </div>

                <script>
                    setTimeout(() => {
                        window.location.href = 'https://www.ZaksKitchenAu.com';
                    }, 3000);
                </script>
            </body>
            </html>
            """)

        except Exception as e:
            return render_template_string("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                <title>Oops! Something Went Wrong - Zak's Kitchen</title>
                <link href="https://fonts.googleapis.com/css2?family=Cardo:ital@0;1&family=Great+Vibes&display=swap" rel="stylesheet">
                <style>
                    body {
                        margin: 0;
                        padding: 0;
                        font-family: 'Cardo', serif;
                        background-color: #d1830f;
                        color: #1a1a1a;
                        text-align: center;
                        min-height: 100vh;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    }
                    .container {
                        padding: 40px 20px;
                        max-width: 800px;
                        margin: 0 auto;
                        position: relative;
                    }
                    .stars {
                        font-size: 1.5em;
                        color: black;
                        margin: 20px 0;
                        letter-spacing: 5px;
                    }
                    .header {
                        font-family: 'Great Vibes', cursive;
                        font-size: 2.8em;
                        color: black;
                        margin-bottom: 20px;
                    }
                    .title {
                        font-weight: bold;
                        font-size: 1.2em;
                        margin: 20px 0;
                    }
                    .content {
                        margin: 30px 0;
                    }
                    .content p {
                        margin: 15px 0;
                        font-size: 1.1em;
                        line-height: 1.6;
                    }
                    .contact-info {
                        margin-top: 30px;
                        font-size: 1.1em;
                    }
                    .contact-info p {
                        margin: 10px 0;
                    }
                    .footer {
                        margin-top: 30px;
                        font-weight: bold;
                    }
                    a {
                        color: black;
                        text-decoration: none;
                    }
                    a:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="stars">✦✦✦✦✦</div>
                    
                    <div class="header">Our Apologies...</div>

                    <div class="title">
                        Your Request Could Not Be Processed
                    </div>

                    <div class="content">
                        <p>It seems our servers are currently down or experiencing high traffic.</p>
                        <p>Please rest assured—your reservation request has not been lost.</p>
                        <p>We kindly ask that you try again after a few moments, or feel free to reach out to us directly for assistance.</p>
                        <p>We're grateful for your patience and understanding. 🙏</p>
                    </div>

                    <div class="contact-info">
                        <p>Web: <a href="https://www.ZaksKitchenAu.com">www.ZaksKitchenAu.com</a></p>
                        <p>Email: <a href="mailto:info@zakskitchenau.com">info@zakskitchenau.com</a></p>
                        <p>Contact: 041-102-0566</p>
                    </div>

                    <div class="footer">
                        Zak's Kitchen Team
                    </div>

                    <div class="stars">✦✦✦✦✦</div>
                </div>

                <script>
                    setTimeout(() => {
                        window.location.href = 'https://www.ZaksKitchenAu.com';
                    }, 3000);
                </script>
            </body>
            </html>
            """, error=str(e))        

