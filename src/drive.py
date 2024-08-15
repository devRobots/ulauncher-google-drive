import os.path

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

ROOT = "/home/devrobot/.local/share/ulauncher/extensions/ulauncher-google-drive"
SCOPES = [
  "https://www.googleapis.com/auth/drive.readonly",
  "https://www.googleapis.com/auth/drive.metadata.readonly"
]

class Drive:
  def __init__(self):
    self._oauth()

  def _oauth(self):
    creds = None
    if os.path.exists(f'{ROOT}/token.json'):
      creds = Credentials.from_authorized_user_file(f'{ROOT}/token.json')
    
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
          f'{ROOT}/credentials.json', SCOPES
        )
        creds = flow.run_local_server(port=0)
      
      with open(f'{ROOT}/token.json', 'w') as token:
        token.write(creds.to_json())
    
    self.creds = creds

  def search_files(self, query="CV"):
    if not self.creds:
      raise Exception("Credentials not found")

    service = build("drive", "v3", credentials=self.creds)
    files = []
    page_token = None

    while True:
      response = (
        service.files()
        .list(
          q=f"name contains '{query}'",
          spaces="drive",
          fields="nextPageToken, files(name, webViewLink, mimeType, size, owners, createdTime)",
          pageToken=page_token,
        )
        .execute()
      )
      
      files.extend(response.get("files", []))
      
      page_token = response.get("nextPageToken", None)
      if page_token is None:
        break

    return files
