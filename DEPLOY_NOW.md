# 🚀 Deploy AutoCrate V12 - Vercel + Railway

## Prerequisites
✅ Railway CLI installed (done!)  
✅ Vercel Pro account  
✅ Git repository ready  

---

## **PART 1: Deploy Backend to Railway** 🚂

### Step 1: Login to Railway
```bash
railway login
```
This will open your browser to authenticate.

### Step 2: Create New Railway Project
```bash
# Navigate to API directory
cd api

# Create new project
railway link

# When prompted, choose:
# > Create New Project
# > Enter project name: autocrate-api
```

### Step 3: Deploy to Railway
```bash
# Deploy the API
railway up

# This will:
# 1. Build your Python app
# 2. Deploy it
# 3. Give you a URL like: https://autocrate-api-production.up.railway.app
```

### Step 4: Get Your API URL
```bash
railway open
```
Copy the URL from your browser (you'll need it for Vercel)

---

## **PART 2: Deploy Frontend to Vercel** 🚀

### Step 1: Set Environment Variable
```bash
# Navigate to web directory
cd ../web

# Add your Railway API URL
echo "NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app/api" > .env.production.local
```

### Step 2: Deploy to Vercel
```bash
# Login to Vercel (if needed)
vercel login

# Deploy to production
vercel --prod

# When prompted:
# - Setup and deploy? Y
# - Which scope? (select your account)
# - Link to existing project? N (first time) or Y (updates)
# - Project name? autocrate-v12
# - Directory? ./ (current)
# - Override settings? N
```

### Step 3: Configure Production Environment
```bash
# Set production environment variable
vercel env add NEXT_PUBLIC_API_URL production

# Enter your Railway URL when prompted:
# https://autocrate-api-production.up.railway.app/api
```

---

## **PART 3: Final Configuration** ⚙️

### Update CORS in Railway
```bash
# Go back to API directory
cd ../api

# Add Vercel domain to CORS
railway variables set CORS_ORIGINS="https://autocrate-v12.vercel.app"

# Redeploy
railway up
```

### Custom Domain (Optional)
**For Vercel:**
```bash
vercel domains add autocrate.com
```

**For Railway:**
```bash
railway domain add api.autocrate.com
```

---

## **Quick Commands Reference** 📝

### Check Status
```bash
# Railway logs
railway logs

# Vercel logs  
vercel logs

# Railway dashboard
railway open

# Vercel dashboard
vercel dashboard
```

### Update Deployments
```bash
# Update API
cd api && railway up

# Update Frontend
cd web && vercel --prod
```

### Environment Variables
```bash
# Railway
railway variables set KEY=value

# Vercel
vercel env add KEY production
```

---

## **Your URLs** 🌐

After deployment, you'll have:

| Service | URL |
|---------|-----|
| **Frontend** | `https://autocrate-v12.vercel.app` |
| **API** | `https://autocrate-api-production.up.railway.app` |
| **API Docs** | `https://autocrate-api-production.up.railway.app/docs` |

---

## **Test Your Deployment** ✅

1. Visit your frontend URL
2. Try creating a crate calculation
3. Download NX expression file
4. Check 3D visualization

---

## **Troubleshooting** 🔧

### API not connecting?
```bash
# Check Railway logs
railway logs

# Verify environment variable
vercel env ls production
```

### CORS errors?
```bash
# Update CORS in Railway
railway variables set CORS_ORIGINS="https://your-vercel-app.vercel.app"
railway up
```

### Build failing?
```bash
# Check Python version
railway variables set NIXPACKS_PYTHON_VERSION=3.9
railway up
```

---

## **Monthly Cost** 💰
- **Vercel Pro**: $20/month (you have this)
- **Railway**: ~$5/month for API
- **Total**: $25/month

---

## **Next Steps** 🎯
1. Set up custom domains
2. Configure analytics
3. Set up monitoring
4. Add error tracking (Sentry)

---

## **Support** 💬
- Railway Discord: https://discord.gg/railway
- Vercel Support: https://vercel.com/support
- GitHub Issues: Your repo issues page