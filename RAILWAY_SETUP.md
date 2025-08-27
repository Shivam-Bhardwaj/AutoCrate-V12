# 🚂 Railway Setup - Step by Step

## The Issue
Railway CLI can't create new projects directly. You need to create the project on Railway's website first.

## ✅ Correct Steps:

### 1. Create Project on Railway Website
1. **Go to**: https://railway.app/new
2. **Click**: "Deploy from GitHub repo"
3. **Select**: Your AutoCrate repository (or "Deploy from CLI" if repo isn't on GitHub)
4. **Name it**: `autocrate-api`

### 2. Link Your Local Project
```bash
cd api
railway link
```
Now when prompted, you'll see your `autocrate-api` project to select.

### 3. Deploy
```bash
railway up
```

---

## Alternative: Quick CLI Method

If you don't have a GitHub repo:

```bash
# In api directory
railway login

# Initialize new project (different command)
railway init

# This will create a project and return a project ID
# Then deploy:
railway up
```

---

## Get Your API URL

After deployment:
```bash
railway open
```

Your URL will be shown in the browser, something like:
`https://autocrate-api-production-XXXX.up.railway.app`

---

## Continue with Vercel

Once you have your Railway URL, continue with the Vercel deployment in the `web` directory.