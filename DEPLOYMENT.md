# AutoCrate V12 Web Deployment Guide

## Overview
AutoCrate V12 Web consists of two components:
1. **Frontend**: Next.js application (deployed on Vercel)
2. **Backend API**: FastAPI Python application (deployed on Render/Railway/Fly.io)

## Option 1: Deploy Frontend on Vercel + Backend on Render (Recommended)

### Step 1: Deploy Backend API on Render

1. Create account at [render.com](https://render.com)

2. Create `render.yaml` in the api directory:
```yaml
services:
  - type: web
    name: autocrate-api
    runtime: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.18
```

3. Push code to GitHub

4. Connect GitHub repo to Render and deploy

5. Note your API URL (e.g., `https://autocrate-api.onrender.com`)

### Step 2: Deploy Frontend on Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Navigate to web directory:
```bash
cd web
```

3. Set environment variable for API:
```bash
# Create .env.production.local
echo "NEXT_PUBLIC_API_URL=https://autocrate-api.onrender.com/api" > .env.production.local
```

4. Deploy to Vercel:
```bash
vercel
```

5. Follow prompts:
   - Setup and deploy? **Y**
   - Which scope? Select your account
   - Link to existing project? **N**
   - Project name? **autocrate-v12-web**
   - Directory? **./** (current directory)
   - Override settings? **N**

6. For production deployment:
```bash
vercel --prod
```

## Option 2: Deploy Both on Railway

### Step 1: Setup Railway

1. Create account at [railway.app](https://railway.app)

2. Create new project

3. Add Python service for API:
   - Connect GitHub repo
   - Set root directory to `/api`
   - Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variable: `PYTHON_VERSION=3.9`

4. Add Node service for Frontend:
   - Connect same GitHub repo
   - Set root directory to `/web`
   - Add environment variable: `NEXT_PUBLIC_API_URL=https://[your-api-service].railway.app/api`

## Option 3: Deploy on Fly.io

### Step 1: Install Fly CLI
```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

### Step 2: Create fly.toml for API
```toml
# api/fly.toml
app = "autocrate-api"
primary_region = "iad"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[[services]]
  http_checks = []
  internal_port = 8080
  protocol = "tcp"
  script_checks = []

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

### Step 3: Deploy
```bash
cd api
fly launch
fly deploy

cd ../web
fly launch
fly deploy
```

## Option 4: Simple Vercel Deployment (Frontend Only)

If you want to deploy only the frontend and use a local API:

1. Navigate to web directory:
```bash
cd web
```

2. Deploy to Vercel:
```bash
vercel --prod
```

3. Users will need to run the API locally:
```bash
cd api
python -m uvicorn main:app --reload --port 8001
```

## Environment Variables

### Frontend (.env.production)
```
NEXT_PUBLIC_API_URL=https://your-api-url.com/api
NEXT_PUBLIC_APP_NAME=AutoCrate V12 Web
NEXT_PUBLIC_VERSION=12.0.0
```

### Backend (Environment Variables)
```
CORS_ORIGINS=https://your-frontend.vercel.app
PORT=8000
```

## Post-Deployment Steps

1. **Test the deployment**:
   - Visit your frontend URL
   - Try calculating a crate
   - Download NX expression file
   - Check 3D visualization

2. **Configure CORS**:
   Update `api/main.py` with your frontend URL:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-app.vercel.app"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Monitor logs**:
   - Vercel: `vercel logs`
   - Render: Check dashboard
   - Railway: Check dashboard
   - Fly.io: `fly logs`

## Troubleshooting

### API Connection Issues
- Check CORS configuration
- Verify API URL in environment variables
- Check API logs for errors

### Build Failures
- Ensure Python version is 3.9+
- Check requirements.txt is complete
- Verify Node.js version is 18+

### Performance Issues
- Consider upgrading to paid plans for better performance
- Implement caching for calculations
- Use CDN for static assets

## Cost Considerations

- **Vercel**: Free tier includes 100GB bandwidth/month
- **Render**: Free tier includes 750 hours/month (sleeps after 15 min inactivity)
- **Railway**: $5/month credit, then usage-based
- **Fly.io**: Free tier includes 3 shared VMs

## Recommended Setup for Production

1. **Frontend**: Vercel (excellent Next.js support)
2. **Backend**: Railway or Render (better Python support)
3. **Database**: If needed, PostgreSQL on same platform as backend
4. **File Storage**: Cloudinary or AWS S3 for generated files

## Support

For deployment issues:
- Check logs on your deployment platform
- Verify all environment variables are set
- Ensure GitHub repo is properly connected
- Test API endpoints independently

## Next Steps

After successful deployment:
1. Set up monitoring (Sentry, LogRocket)
2. Configure analytics (Google Analytics, Plausible)
3. Set up CI/CD pipeline
4. Implement rate limiting
5. Add authentication if needed