from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from src.google_drive_service import GoogleDriveService

# Initialize Google Drive service
service_account_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'service-account.json')
drive_service = GoogleDriveService(service_account_path)

# Setup comic folders on startup
folder_structure = drive_service.setup_comic_folders()

comic_bp = Blueprint('comic', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_mime_type(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }
    return mime_types.get(ext, 'image/jpeg')

@comic_bp.route('/api/upload-comic-cover', methods=['POST'])
def upload_comic_cover():
    """Upload comic cover image"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        comic_id = request.form.get('comic_id')
        comic_title = request.form.get('comic_title', 'Untitled')
        
        if not comic_id:
            return jsonify({'error': 'Comic ID is required'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File size too large (max 10MB)'}), 400
        
        # Generate secure filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"cover_{comic_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        # Read file data
        file_data = file.read()
        mime_type = get_file_mime_type(file.filename)
        
        # Upload to Google Drive
        if not folder_structure or not folder_structure.get('covers_folder_id'):
            return jsonify({'error': 'Google Drive folders not initialized'}), 500
        
        result = drive_service.upload_file(
            file_data=file_data,
            filename=filename,
            folder_id=folder_structure['covers_folder_id'],
            mime_type=mime_type
        )
        
        if not result:
            return jsonify({'error': 'Failed to upload file to Google Drive'}), 500
        
        return jsonify({
            'success': True,
            'file_id': result['id'],
            'filename': filename,
            'direct_link': result['direct_link'],
            'web_view_link': result['web_view_link'],
            'comic_id': comic_id
        })
        
    except Exception as e:
        print(f"Error uploading comic cover: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@comic_bp.route('/api/upload-comic-page', methods=['POST'])
def upload_comic_page():
    """Upload comic page image"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        comic_id = request.form.get('comic_id')
        page_number = request.form.get('page_number', '1')
        
        if not comic_id:
            return jsonify({'error': 'Comic ID is required'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File size too large (max 10MB)'}), 400
        
        # Generate secure filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"page_{comic_id}_p{page_number}_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        # Read file data
        file_data = file.read()
        mime_type = get_file_mime_type(file.filename)
        
        # Upload to Google Drive
        if not folder_structure or not folder_structure.get('pages_folder_id'):
            return jsonify({'error': 'Google Drive folders not initialized'}), 500
        
        result = drive_service.upload_file(
            file_data=file_data,
            filename=filename,
            folder_id=folder_structure['pages_folder_id'],
            mime_type=mime_type
        )
        
        if not result:
            return jsonify({'error': 'Failed to upload file to Google Drive'}), 500
        
        return jsonify({
            'success': True,
            'file_id': result['id'],
            'filename': filename,
            'direct_link': result['direct_link'],
            'web_view_link': result['web_view_link'],
            'comic_id': comic_id,
            'page_number': page_number
        })
        
    except Exception as e:
        print(f"Error uploading comic page: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@comic_bp.route('/api/comic-images/<comic_id>', methods=['GET'])
def get_comic_images(comic_id):
    """Get all images for a specific comic"""
    try:
        if not folder_structure:
            return jsonify({'error': 'Google Drive folders not initialized'}), 500
        
        # Get cover images
        covers = drive_service.list_files_in_folder(folder_structure['covers_folder_id'])
        comic_covers = [f for f in covers if f['name'].startswith(f'cover_{comic_id}_')]
        
        # Get page images
        pages = drive_service.list_files_in_folder(folder_structure['pages_folder_id'])
        comic_pages = [f for f in pages if f['name'].startswith(f'page_{comic_id}_')]
        
        # Sort pages by page number
        comic_pages.sort(key=lambda x: int(x['name'].split('_p')[1].split('_')[0]) if '_p' in x['name'] else 0)
        
        return jsonify({
            'success': True,
            'comic_id': comic_id,
            'covers': comic_covers,
            'pages': comic_pages,
            'total_covers': len(comic_covers),
            'total_pages': len(comic_pages)
        })
        
    except Exception as e:
        print(f"Error getting comic images: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@comic_bp.route('/api/delete-comic-image/<file_id>', methods=['DELETE'])
def delete_comic_image(file_id):
    """Delete a comic image from Google Drive"""
    try:
        success = drive_service.delete_file(file_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Image deleted successfully'})
        else:
            return jsonify({'error': 'Failed to delete image'}), 500
            
    except Exception as e:
        print(f"Error deleting comic image: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@comic_bp.route('/api/drive-status', methods=['GET'])
def drive_status():
    """Check Google Drive API status"""
    try:
        if drive_service.service and folder_structure:
            return jsonify({
                'success': True,
                'status': 'connected',
                'folders': folder_structure
            })
        else:
            return jsonify({
                'success': False,
                'status': 'disconnected',
                'error': 'Google Drive service not initialized'
            }), 500
            
    except Exception as e:
        print(f"Error checking drive status: {e}")
        return jsonify({'error': 'Internal server error'}), 500

