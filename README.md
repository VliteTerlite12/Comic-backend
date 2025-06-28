# MyComicIDN Backend

Backend API untuk aplikasi MyComicIDN - Platform komik digital Indonesia.

## Features

- 🔐 **Authentication System** - Login/signup dengan username sederhana
- 📚 **Comic Management** - CRUD operations untuk komik
- 🖼️ **Image Storage** - Integrasi dengan Google Drive API
- 🔍 **Search & Filter** - Pencarian komik berdasarkan judul dan tag
- 📊 **Reporting System** - Sistem laporan dengan status warna
- 🌙 **Dark/Light Mode** - Support untuk tema gelap dan terang

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: Cloud Firestore
- **File Storage**: Google Drive API
- **Authentication**: Custom JWT-like system
- **Deployment**: Vercel (Serverless)

## Project Structure

```
comic-backend/
├── api/
│   └── index.py              # Vercel entry point
├── src/
│   ├── routes/
│   │   ├── comic.py          # Comic-related endpoints
│   │   └── user.py           # User-related endpoints
│   ├── models/
│   │   └── user.py           # Database models
│   ├── google_drive_service.py # Google Drive integration
│   └── main.py               # Flask app main file
├── vercel.json               # Vercel configuration
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## API Endpoints

### Comic Management
- `POST /api/upload-comic-cover` - Upload comic cover image
- `POST /api/upload-comic-page` - Upload comic page image
- `GET /api/comic-images/<comic_id>` - Get all images for a comic
- `DELETE /api/delete-comic-image/<file_id>` - Delete comic image
- `GET /api/drive-status` - Check Google Drive API status

### User Management
- `POST /api/users` - Create new user
- `GET /api/users/<user_id>` - Get user profile
- `PUT /api/users/<user_id>` - Update user profile

## Environment Variables

For local development, create a `.env` file:

```env
FLASK_ENV=development
GOOGLE_APPLICATION_CREDENTIALS=src/service-account.json
```

For Vercel deployment, set these in Vercel dashboard:

```env
FLASK_ENV=production
SERVICE_ACCOUNT_JSON=<your-service-account-json-content>
```

## Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd comic-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Google Drive API**
   - Create a service account in Google Cloud Console
   - Download the JSON key file
   - Place it as `src/service-account.json`
   - Enable Google Drive API
   - Share your Google Drive folder with the service account email

5. **Run the application**
   ```bash
   python src/main.py
   ```

   The API will be available at `http://localhost:5001`

## Deployment to Vercel

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```

4. **Set Environment Variables**
   - Go to Vercel dashboard
   - Navigate to your project settings
   - Add environment variables:
     - `FLASK_ENV`: `production`
     - `SERVICE_ACCOUNT_JSON`: Copy entire content of service-account.json

5. **Redeploy**
   ```bash
   vercel --prod
   ```

## Google Drive Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Google Drive API**
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"

3. **Create Service Account**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the details and create
   - Download the JSON key file

4. **Setup Folder Permissions**
   - Create a folder in your Google Drive for comic storage
   - Share the folder with the service account email (found in JSON file)
   - Give "Editor" permissions

## File Structure in Google Drive

The application creates this folder structure:

```
MyComicIDN-Storage/
├── comic-covers/     # Comic cover images
└── comic-pages/      # Comic page images
```

## Security Notes

- **Never commit service-account.json** to version control
- Use environment variables for sensitive data
- Implement proper CORS policies
- Validate all user inputs
- Use HTTPS in production

## API Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": {...},
  "message": "Success message"
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error message"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please contact [your-email@example.com] or create an issue in the repository.

