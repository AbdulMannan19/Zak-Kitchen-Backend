import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import json

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)
    SCOPES = config['SCOPES']

def generate_email_content(name, email, phone, date, time, guests):
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <table width="100%" cellspacing="0" cellpadding="10" style="max-width: 600px; margin: auto; background-color: white; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);">
            <tr>
                <td style="background-color: #0073e6; color: white; text-align: center; font-size: 24px; padding: 15px; border-top-left-radius: 8px; border-top-right-radius: 8px;">
                    Reservation 
                </td>
            </tr>
            <tr>
                <td style="padding: 20px; text-align: center; font-size: 16px; color: #333;">
                    <p>Here is your reservation information:</p>
                    <table width="100%" cellspacing="0" cellpadding="8" style="border-collapse: collapse; text-align: left;">
                        <tr>
                            <th style="background-color: #0073e6; color: white; padding: 10px; border: 1px solid #ddd;">Field</th>
                            <th style="background-color: #0073e6; color: white; padding: 10px; border: 1px solid #ddd;">Details</th>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Name</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{name}</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Email</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{email}</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Phone</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{phone}</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Date</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{date}</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Time</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{time}</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Guests</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{guests}</td>
                        </tr>
                    </table>
                    <p style="margin-top: 20px; font-size: 14px; color: #555;">Thank you for choosing us! We look forward to serving you.</p>
                </td>
            </tr>
            <tr>
                <td style="background-color: #0073e6; color: white; text-align: center; padding: 15px; font-size: 14px; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;">
                    &copy; 2025 Your Company. All Rights Reserved.
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html_content

def get_gmail_service():
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'Backend\credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
            
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, message_text):
    # Create a multipart message
    message = MIMEMultipart('alternative')
    
    # Create both plain-text and HTML versions of the message
    text_part = MIMEText(message_text.replace('<html>', '').replace('</html>', '').replace('<br>', '\n'), 'plain')
    html_part = MIMEText(message_text, 'html')
    
    # Attach both parts
    message.attach(text_part)
    message.attach(html_part)
    
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f'Message Id: {message["id"]}')
        return message
    except Exception as e:
        print(f'An error occurred: {e}')
        return None
