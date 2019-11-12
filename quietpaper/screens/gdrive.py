from apiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from apiclient import errors
from quietpaper import logger
import numpy as np

class GdriveScreen:

    def __init__(self, auth_file, file_id, file_locally):
        self.auth_file = auth_file
        self.file_id = file_id
        self.file_locally = file_locally

    def get_update_rate(self, cycle):
        return 5
    
    def update(self, display, cycle):
        try:
            scope = ['https://www.googleapis.com/auth/drive']
            credentials = ServiceAccountCredentials.from_json_keyfile_name(self.auth_file, scope)
            service = build('drive', 'v3', credentials=credentials)
            media_body = MediaFileUpload(self.file_locally, resumable=True)
            updated_file = service.files().update(
                fileId=self.file_id, media_body=media_body).execute()
        except Exception as e: 
            logger.warning("Cannot update image on GdriveScreen: " + (e.message if hasattr(e, 'message') else type(e).__name__))

    def clear(self, display):
        pass
        