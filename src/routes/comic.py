import os
from flask import Blueprint, request, jsonify
from src.google_drive_service import GoogleDriveService

comic_bp = Blueprint("comic", __name__)

# Initialize GoogleDriveService
# For Vercel, credentials will be loaded from SERVICE_ACCOUNT_JSON env var
# For local, it will try to load from service-account.json file
if os.environ.get("VERCEL"):
    drive_service = GoogleDriveService(service_account_file=None)
else:
    service_account_path = os.path.join(os.path.dirname(__file__), "service-account.json")
    drive_service = GoogleDriveService(service_account_path)

@comic_bp.route("/api/drive-status", methods=["GET"])
def drive_status():
    try:
        # Attempt to list files in root to check authentication
        drive_service.service.files().list(pageSize=1).execute()
        return jsonify({"success": True, "message": "Google Drive API is connected."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@comic_bp.route("/api/upload-comic-cover", methods=["POST"])
def upload_comic_cover():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file"}), 400
    
    comic_id = request.form.get("comic_id")
    comic_title = request.form.get("comic_title")

    if not comic_id or not comic_title:
        return jsonify({"success": False, "error": "Comic ID and title are required"}), 400

    # Ensure comic-covers folder exists
    covers_folder_id = drive_service.setup_comic_folders()["covers_folder_id"]
    if not covers_folder_id:
        return jsonify({"success": False, "error": "Could not find or create comic covers folder"}), 500

    file_data = file.read()
    filename = f"{comic_id}_cover.jpg"
    upload_result = drive_service.upload_file(file_data, filename, covers_folder_id, mime_type="image/jpeg")

    if upload_result:
        return jsonify({"success": True, "data": upload_result, "message": "Cover uploaded successfully"})
    else:
        return jsonify({"success": False, "error": "Failed to upload cover"}), 500

@comic_bp.route("/api/upload-comic-page", methods=["POST"])
def upload_comic_page():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file"}), 400
    
    comic_id = request.form.get("comic_id")
    page_number = request.form.get("page_number")

    if not comic_id or not page_number:
        return jsonify({"success": False, "error": "Comic ID and page number are required"}), 400

    # Ensure comic-pages folder exists
    pages_folder_id = drive_service.setup_comic_folders()["pages_folder_id"]
    if not pages_folder_id:
        return jsonify({"success": False, "error": "Could not find or create comic pages folder"}), 500

    file_data = file.read()
    filename = f"{comic_id}_page_{page_number}.jpg"
    upload_result = drive_service.upload_file(file_data, filename, pages_folder_id, mime_type="image/jpeg")

    if upload_result:
        return jsonify({"success": True, "data": upload_result, "message": "Page uploaded successfully"})
    else:
        return jsonify({"success": False, "error": "Failed to upload page"}), 500

@comic_bp.route("/api/comic-images/<comic_id>", methods=["GET"])
def get_comic_images(comic_id):
    try:
        pages_folder_id = drive_service.setup_comic_folders()["pages_folder_id"]
        if not pages_folder_id:
            return jsonify({"success": False, "error": "Comic pages folder not found"}), 500

        files = drive_service.list_files_in_folder(pages_folder_id)
        comic_files = [f for f in files if f["name"].startswith(f"{comic_id}_page_")]
        
        # Sort by page number
        comic_files.sort(key=lambda x: int(x["name"].split("_")[-1].split(".")[0]))

        return jsonify({"success": True, "data": comic_files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@comic_bp.route("/api/delete-comic-image/<file_id>", methods=["DELETE"])
def delete_comic_image(file_id):
    try:
        result = drive_service.delete_file(file_id)
        if result:
            return jsonify({"success": True, "message": "File deleted successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to delete file"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


