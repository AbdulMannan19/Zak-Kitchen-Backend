from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from flask import session, render_template_string
import json
import os

class OAuth2CallbackHandler:
    def __init__(self):
        
        self.credentials_path = os.environ.get('CREDENTIALS_PATH', './credentials.json')
        self.config_path = os.environ.get('CONFIG_PATH', './config.json')
            
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.scopes = config['SCOPES']
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found at {self.config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in config file at {self.config_path}")
        except KeyError:
            raise KeyError("'SCOPES' key not found in config file")
        
        self.redirect_uri = os.environ.get('OAUTH2CALLBACK_URI', 'http://localhost:5000/oauth2callback')

    def handle_callback(self, code, state):
        try:
            reservation_data = json.loads(state)
        
            flow = Flow.from_client_secrets_file(
                self.credentials_path,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            flow.fetch_token(code=code)
            creds = flow.credentials

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
            fetch('/book-reservation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({{ reservation_data|tojson|safe }})
            }).then(res => res.json())
            .then(data => {
                document.body.innerHTML = '<h2>' + data.message + '</h2>';
                setTimeout(() => {
                    window.location.href = 'http://localhost:3000';
                }, 2000);
            }).catch(err => {
                document.body.innerHTML = '<h2>Error: ' + err.message + '</h2>';
                setTimeout(() => {
                    window.location.href = 'http://localhost:3000';
                }, 2000);
            });
            </script>
            """, reservation_data=reservation_data)

        except json.JSONDecodeError:
            return {'error': 'Invalid state parameter format'}, 400
        except Exception as e:
            return {'error': str(e)}, 500 
