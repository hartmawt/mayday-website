from google_auth_oauthlib.flow import InstalledAppFlow
import json

# Use the file you just downloaded
flow = InstalledAppFlow.from_client_secrets_file(
    '../spec/client_secret_916197180463-na0cohjeb7mfmnsspaprdg0d661tjmt8.apps.googleusercontent.com.json',
    scopes=['https://www.googleapis.com/auth/business.manage']
)

# This opens your browser
creds = flow.run_local_server(port=0)

# This is the "Golden Ticket" for your website
print(f"REFRESH_TOKEN: {creds.refresh_token}")
print(f"CLIENT_ID: {creds.client_id}")
print(f"CLIENT_SECRET: {creds.client_secret}")