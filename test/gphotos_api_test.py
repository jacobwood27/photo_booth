import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.transport.requests import AuthorizedSession, Request
import json

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
          'https://www.googleapis.com/auth/photoslibrary.sharing']

URL = 'https://photoslibrary.googleapis.com/v1'

creds = None

if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('/home/woojac/google_api_credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

session = AuthorizedSession(creds)

create_album_body = json.dumps({"album": {"title": "test_album"}})
resp = session.post(URL + '/albums', create_album_body).json()
alb_id = resp["id"]


request_body = {
    "sharedAlbumOptions": {
        "isCollaborative": True,
        "isCommentable": True
    }
}
result = session.albums().share(
    albumId=alb_id,
    body=request_body).execute()


with open("test_pic.jpg", mode='rb') as fp:
    data = fp.read()

session.headers["Content-type"] = "application/octet-stream"
session.headers["X-Goog-Upload-Protocol"] = "raw"
session.headers["X-Goog-Upload-File-Name"] = "test_pic.jpg"

upload_token = session.post(URL + '/uploads', data)

if upload_token.status_code == 200 and upload_token.content:

    create_body = json.dumps({"albumId": alb_id,
                                "newMediaItems": [
                                    {"description": "",
                                    "simpleMediaItem": {"uploadToken": upload_token.content.decode()}
                                    }
                                ]}, indent=4)

    resp = session.post(URL + '/mediaItems:batchCreate', create_body).json()



### Steps
# Make an album
# Upload media
# Move into album
# Set shareable
# Display QR code
