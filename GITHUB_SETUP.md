# GitHub Repository Setup Instructions

## Step 1: Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `ai-resume-matcher` (or your choice)
3. Make it **PUBLIC** (required for Render free tier)
4. Don't check "Add a README file" (we already have one)
5. Click "Create repository"

## Step 2: Connect Local Repository
After creating the repository, GitHub will show you commands. Use these:

```bash
# Replace with your actual GitHub username and repository name
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git branch -M main
git push -u origin main
```

## Step 3: Verify Files on GitHub
Check that these files are present in your GitHub repository:
- ✅ render.yaml
- ✅ Procfile  
- ✅ requirements.txt
- ✅ runtime.txt
- ✅ build.sh
- ✅ README.md
- ✅ DEPLOYMENT.md

## Step 4: Deploy to Render
1. Go to https://dashboard.render.com/
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the render.yaml file
5. Set required environment variables:
   - FLASK_ENV=production
   - SECRET_KEY=your-secret-key
   - OPENAI_API_KEY=your-api-key (optional)

## Alternative: Manual Web Service
If Blueprint doesn't work:
1. Click "New" → "Web Service"
2. Connect repository
3. Build Command: `chmod +x build.sh && ./build.sh`
4. Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 run:app`

Your application will be live at: https://your-app-name.onrender.com
