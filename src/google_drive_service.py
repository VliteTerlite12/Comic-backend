import os
import io
import json
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError

class GoogleDriveService:
    def __init__(self, service_account_file=None):
        self.service_account_file = service_account_file
        self.scopes = ["https://www.googleapis.com/auth/drive"]
        self.service = None
        self.folder_id = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API using service account"""
        try:
            credentials = None
            if os.environ.get("SERVICE_ACCOUNT_JSON"):
                # Load credentials from environment variable (for Vercel)
                info = json.loads(os.environ.get("SERVICE_ACCOUNT_JSON"))
                credentials = service_account.Credentials.from_service_account_info(info, scopes=self.scopes)
            elif self.service_account_file:
                # Load credentials from file (for local development)
                credentials = service_account.Credentials.from_service_account_file(
                    self.service_account_file, scopes=self.scopes)
            else:
                raise ValueError("Service account credentials not provided.")

            self.service = build("drive", "v3", credentials=credentials)
            print("Google Drive API authenticated successfully")
        except Exception as e:
            print(f"Authentication failed: {e}")
            raise
    
    def create_folder(self, folder_name, parent_folder_id="root"):
        """Create a folder in Google Drive"""
        try:
            # Check if folder already exists
            existing_folder = self.find_folder(folder_name, parent_folder_id)
            if existing_folder:
                return existing_folder["id"]
            
            folder_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_folder_id]
            }
            
            folder = self.service.files().create(body=folder_metadata, fields="id").execute()
            folder_id = folder.get("id")
            print(f"Created folder \'{folder_name}\' with ID: {folder_id}")
            return folder_id
        except HttpError as error:
            print(f"An error occurred while creating folder: {error}")
            return None
    
    def find_folder(self, folder_name, parent_folder_id="root"):
        """Find a folder by name in the specified parent folder"""
        try:
            query = f"name=\'{folder_name}\' and mimeType=\'application/vnd.google-apps.folder\' and \'{parent_folder_id}\' in parents and trashed=false"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            folders = results.get("files", [])
            return folders[0] if folders else None
        except HttpError as error:
            print(f"An error occurred while searching for folder: {error}")
            return None
    
    def upload_file(self, file_data, filename, folder_id, mime_type="image/jpeg"):
        """Upload a file to Google Drive"""
        try:
            file_metadata = {
                "name": filename,
                "parents": [folder_id]
            }
            
            media = MediaIoBaseUpload(
                io.BytesIO(file_data),
                mimetype=mime_type,
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id,webViewLink,webContentLink"
            ).execute()
            
            # Make file publicly readable
            self.make_file_public(file.get("id"))
            
            return {
                "id": file.get("id"),
                "web_view_link": file.get("webViewLink"),
                "web_content_link": file.get("webContentLink"),
                "direct_link": f"https://drive.google.com/uc?id={file.get("id")}"
            }
        except HttpError as error:
            print(f"An error occurred while uploading file: {error}")
            return None
    
    def make_file_public(self, file_id):
        """Make a file publicly readable"""
        try:
            permission = {
                "type": "anyone",
                "role": "reader"
            }
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            print(f"File {file_id} made public")
        except HttpError as error:
            print(f"An error occurred while making file public: {error}")
    
    def delete_file(self, file_id):
        """Delete a file from Google Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"File {file_id} deleted successfully")
            return True
        except HttpError as error:
            print(f"An error occurred while deleting file: {error}")
            return False
    
    def list_files_in_folder(self, folder_id):
        """List all files in a folder"""
        try:
            query = f"\'{folder_id}\' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, webViewLink, webContentLink, mimeType, createdTime)"
            ).execute()
            files = results.get("files", [])
            
            # Add direct links
            for file in files:
                file["direct_link"] = f"https://drive.google.com/uc?id={file["id"]}"
            
            return files
        except HttpError as error:
            print(f"An error occurred while listing files: {error}")
            return []
    
    def setup_comic_folders(self):
        """Setup main comic folders structure"""
        try:
            # Create main comics folder
            main_folder_id = self.create_folder("MyComicIDN-Storage")
            
            # Create subfolders
            covers_folder_id = self.create_folder("comic-covers", main_folder_id)
            pages_folder_id = self.create_folder("comic-pages", main_folder_id)
            
            return {
                "main_folder_id": main_folder_id,
                "covers_folder_id": covers_folder_id,
                "pages_folder_id": pages_folder_id
            }
        except Exception as e:
            print(f"Error setting up comic folders: {e}")
            return None



