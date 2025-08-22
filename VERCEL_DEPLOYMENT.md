# AutoCrate Web - Vercel Deployment Guide

## Quick Start

### 1. One-Click Deploy
Run the deployment script:
```bash
deploy_to_vercel.bat
```

### 2. Manual Deploy
```bash
npm i -g vercel
vercel --prod
```

## What Vercel Deployment Does

### Automatic Setup
When you run `vercel` for the first time:

1. **Authentication**
   - Browser opens automatically
   - Login with GitHub, GitLab, or email
   - No credit card required

2. **Project Creation**
   - Asks: "Set up and deploy?"
   - Choose: Yes
   - Project name: `autocrate-web` (or accept default)
   - Select directory: `.` (current)

3. **Deployment**
   - Uploads your code
   - Builds Python functions
   - Deploys globally to edge network
   - Provides instant HTTPS URL

### What Gets Deployed

**Serverless Functions** (`/api`):
- Flask app runs as serverless Python functions
- Auto-scales from 0 to thousands of requests
- No server management needed

**Static Files**:
- HTML templates
- Documentation
- CSS/JavaScript assets

**Features**:
- Automatic HTTPS/SSL
- Global CDN (faster than Firebase)
- Zero-config deployment
- Preview deployments for each push

## File Structure for Vercel

```
AutoCrate/
├── api/
│   ├── index.py          # Main Flask app (serverless)
│   └── requirements.txt  # Python dependencies
├── web/
│   ├── templates/        # HTML templates
│   └── static/          # Static assets
├── docs/                 # Documentation
├── vercel.json          # Vercel configuration
└── deploy_to_vercel.bat # Deployment script
```

## Setting Environment Variables

### Via Vercel Dashboard (Recommended)

1. Go to [https://vercel.com/dashboard](https://vercel.com/dashboard)
2. Click on your `autocrate-web` project
3. Go to "Settings" → "Environment Variables"
4. Add:
   - `AUTH_PASSWORD_HASH`: Your password hash
   - `SECRET_KEY`: Random string for sessions

### Via CLI
```bash
vercel env add AUTH_PASSWORD_HASH
vercel env add SECRET_KEY
```

### Generate Password Hash
```python
import hashlib
password = "your-secure-password"
hash = hashlib.sha256(password.encode()).hexdigest()
print(hash)
```

## Deployment Commands

### Production Deploy
```bash
vercel --prod
```

### Preview Deploy (for testing)
```bash
vercel
```

### View Logs
```bash
vercel logs
```

### List Deployments
```bash
vercel ls
```

## URLs After Deployment

Your app will be available at:
- **Production**: `https://autocrate-web.vercel.app`
- **Preview**: `https://autocrate-web-xyz123.vercel.app` (unique per deploy)

## Advantages Over Firebase

1. **Simpler Setup**: No Google account or billing required
2. **Faster Deployment**: ~30 seconds vs 2-5 minutes
3. **Better DX**: Automatic preview URLs for each commit
4. **No Cold Starts**: Faster function execution
5. **Edge Network**: Global deployment by default
6. **Free Tier**: Generous limits for hobby projects

## Free Tier Limits

- **Serverless Functions**: 100GB-hours/month
- **Bandwidth**: 100GB/month
- **Requests**: Unlimited
- **Deployments**: Unlimited
- **Custom Domains**: Supported
- **Team Members**: Unlimited

## Troubleshooting

### "Command not found: vercel"
```bash
npm install -g vercel
```

### "No default project found"
```bash
vercel link
```

### "Build failed"
Check `api/requirements.txt` has only:
```
Flask==3.0.0
flask-cors==4.0.0
```

### "404 Not Found"
Ensure `vercel.json` routes are correct

### "Authentication not working"
1. Set environment variables in Vercel dashboard
2. Redeploy: `vercel --prod --force`

## Local Development

### Run locally with Vercel CLI
```bash
vercel dev
```
Access at: http://localhost:3000

### Run Flask directly
```bash
cd api
python index.py
```

## Custom Domain

1. In Vercel Dashboard → Settings → Domains
2. Add your domain: `autocrate.yourdomain.com`
3. Follow DNS instructions
4. Automatic SSL certificate

## Security Best Practices

1. **Change Default Password**: Never use "autocrate2024" in production
2. **Use Environment Variables**: Don't hardcode secrets
3. **Enable 2FA**: On your Vercel account
4. **Monitor Usage**: Check dashboard for unusual activity
5. **Set CORS Policy**: Configure allowed origins in production

## CI/CD Integration

### GitHub Auto-Deploy
1. Import project from GitHub in Vercel
2. Every push auto-deploys
3. PRs get preview URLs

### Manual Git Integration
```bash
git remote add vercel https://vercel.com/your-name/autocrate-web
git push vercel main
```

## Monitoring

- **Dashboard**: https://vercel.com/dashboard
- **Analytics**: Built-in, no setup needed
- **Logs**: Real-time function logs
- **Alerts**: Set up in dashboard

## Support

- Vercel Docs: https://vercel.com/docs
- Status: https://vercel-status.com
- Community: https://github.com/vercel/vercel