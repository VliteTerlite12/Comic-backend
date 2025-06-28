# Vercel Deployment Instructions

## Environment Variables yang perlu diset di Vercel:

1. **SERVICE_ACCOUNT_JSON**: 
   Copy seluruh isi file service-account.json sebagai string JSON

2. **FLASK_ENV**: 
   production

## Cara Deploy ke Vercel:

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login ke Vercel:
   ```bash
   vercel login
   ```

3. Deploy dari direktori comic-backend:
   ```bash
   vercel
   ```

4. Set environment variables di Vercel dashboard:
   - Pergi ke project settings
   - Tambahkan environment variables
   - Redeploy project

## Struktur File untuk Vercel:
```
comic-backend/
├── api/
│   └── index.py          # Entry point untuk Vercel
├── src/                  # Source code aplikasi
├── vercel.json          # Konfigurasi Vercel
├── requirements.txt     # Python dependencies
└── README.md           # Dokumentasi
```

## Testing Deployment:
Setelah deploy, test endpoints:
- GET /api/drive-status
- POST /api/upload-comic-cover
- POST /api/upload-comic-page

