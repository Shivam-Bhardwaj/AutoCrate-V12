# AutoCrate Web Application

## Overview
This is the web version of AutoCrate, providing browser-based access to the crate design automation system with password authentication.

## Features
- Web-based GUI replacing the desktop tkinter interface
- Password-protected access
- Real-time crate dimension calculations
- NX expression file generation and download
- Integrated documentation viewer
- Firebase hosting and serverless functions

## Project Structure
```
web/
├── app.py              # Flask application with API endpoints
├── main.py             # Firebase Functions entry point
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── index.html     # Main application interface
│   └── login.html     # Authentication page
├── static/            # Static assets
│   └── docs/          # Documentation (copied during deployment)
└── temp/              # Temporary files for downloads
```

## Setup Instructions

### 1. Install Dependencies
```bash
cd web
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and update values:
```bash
cp .env.example .env
```

### 3. Local Development
Run the Flask development server:
```bash
python app.py
```
Access at: http://localhost:5000

### 4. Firebase Setup
1. Install Firebase CLI:
   ```bash
   npm install -g firebase-tools
   ```

2. Login to Firebase:
   ```bash
   firebase login
   ```

3. Create a Firebase project:
   ```bash
   firebase projects:create autocrate-web
   ```

4. Initialize Firebase in the project:
   ```bash
   firebase init
   ```
   - Select: Hosting and Functions
   - Choose Python for Functions
   - Use existing configuration files

## Deployment

### Quick Deploy
Run the deployment script:
```bash
deploy_to_firebase.bat
```

### Manual Deploy
```bash
# Copy documentation
xcopy /E /Y docs\* web\static\docs\

# Deploy to Firebase
firebase deploy --only hosting,functions
```

## Authentication

### Default Password
- Default: `autocrate2024`
- **IMPORTANT**: Change this in production!

### Changing Password
1. Generate new password hash:
   ```python
   import hashlib
   password = "your-new-password"
   hash = hashlib.sha256(password.encode()).hexdigest()
   print(hash)
   ```

2. Update in `app.py`:
   ```python
   PASSWORD_HASH = "your-new-hash"
   ```

### Firebase Authentication (Optional)
For production, integrate Firebase Authentication:
1. Enable Authentication in Firebase Console
2. Update `app.py` to use Firebase Auth SDK
3. Implement user management features

## API Endpoints

### Authentication
- `POST /api/login` - Authenticate with password
- `POST /api/logout` - Clear session

### Calculations
- `POST /api/calculate` - Calculate crate dimensions
  ```json
  {
    "product_weight": 1000,
    "product_length": 48,
    "product_width": 36,
    "product_height": 24,
    "clearance_length": 4,
    "clearance_width": 4,
    "clearance_height": 4,
    "panel_thickness": 0.5,
    "cleat_thickness": 1.5,
    "cleat_width": 3.5,
    "intermediate_cleat_width": 1.5
  }
  ```

### File Generation
- `POST /api/generate_expressions` - Generate NX expression file
- `GET /api/download/<filename>` - Download generated file

### Documentation
- `GET /docs` - Access integrated documentation

## Security Considerations

1. **Password Storage**: Never store plain text passwords
2. **HTTPS**: Always use HTTPS in production
3. **Session Security**: Configure secure session cookies
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **Input Validation**: Validate all user inputs
6. **File Access**: Restrict file system access

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session secret | Random |
| `AUTH_PASSWORD_HASH` | SHA256 hash of password | - |
| `SESSION_LIFETIME_HOURS` | Session duration | 24 |
| `MAX_UPLOAD_SIZE` | Max file size | 10MB |

## Troubleshooting

### Firebase Deployment Issues
1. Ensure Firebase CLI is installed
2. Check Firebase project exists
3. Verify billing is enabled for Functions
4. Review function logs in Firebase Console

### Authentication Problems
1. Clear browser cookies
2. Check password hash is correct
3. Verify session configuration

### Calculation Errors
1. Check input validation
2. Review server logs
3. Ensure core AutoCrate modules are accessible

## Development Tips

### Testing Locally
```bash
# Run with debug mode
export FLASK_ENV=development
python app.py
```

### Monitoring
- Firebase Console: View function logs
- Browser DevTools: Debug client-side issues
- Flask logs: Server-side debugging

## Production Checklist

- [ ] Change default password
- [ ] Configure custom domain
- [ ] Set up SSL certificate
- [ ] Enable Firebase Authentication
- [ ] Configure backup strategy
- [ ] Set up monitoring/alerts
- [ ] Implement rate limiting
- [ ] Add Google Analytics
- [ ] Configure CDN for static assets
- [ ] Test on multiple browsers

## Support

For issues or questions:
1. Check documentation at `/docs`
2. Review Firebase logs
3. Contact AutoCrate support team