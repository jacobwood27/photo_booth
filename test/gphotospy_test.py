from gphotospy import authorize
from gphotospy.album import Album
from gphotospy.media import Media

import pyqrcode
import png



# Select secrets file (got through Google's API console)
CLIENT_SECRET_FILE = "/home/jwood/google_api_credentials.json" # Here your secret's file. See below.

# Get authorization and return a service object
service = authorize.init(CLIENT_SECRET_FILE)

# Init the album manager
album_manager = Album(service)
media_manager = Media(service)

# Create a new album
new_album = album_manager.create('test album4')

# Get the album id and share it
id_album = new_album.get("id")
share_results = album_manager.share(id_album)

shareUrl = share_results["shareableUrl"]

media_manager.stage_media("test/raw_dual.mp4")
media_manager.batchCreate(album_id=id_album)

qr = pyqrcode.create(shareUrl)
qr.png('myqr.png', scale = 6)

