# AI Resume Matcher - Render Deployment Guide

This application is ready to be deployed on Render.com. Follow these steps to deploy:

## Prerequisites

1. A Render.com account (free tier available)
2. A GitHub repository with this code
3. (Optional) OpenAI API key for AI matching features

## Deployment Steps

### Option 1: Using render.yaml (Recommended)

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file

3. **Configure Environment Variables**
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: Generate a secure secret key
   - `OPENAI_API_KEY`: Your OpenAI API key (optional)
   - Database URL will be automatically configured

### Option 2: Manual Setup

1. **Create Web Service**
   - Go to Render Dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Build & Deploy Settings**
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 run:app`
   - **Environment**: `Python 3`

3. **Create PostgreSQL Database**
   - Click "New" → "PostgreSQL"
   - Choose free tier
   - Note the connection details

4. **Set Environment Variables**
   - `FLASK_ENV=production`
   - `SECRET_KEY=your-secret-key-here`
   - `DATABASE_URL=postgresql://...` (from step 3)
   - `OPENAI_API_KEY=your-openai-key` (optional)

## Post-Deployment

1. **Initialize Database**
   The database tables will be created automatically on first startup.

2. **Upload Test Data**
   - Access your deployed application
   - Upload some resumes and job descriptions to test functionality

3. **Monitor Logs**
   - Check the Render dashboard for deployment logs
   - Monitor application performance

## Features

- **Resume Upload & Parsing**: Upload PDF, DOC, DOCX, TXT resumes
- **Job Description Matching**: Smart matching algorithm
- **AI-Powered Matching**: Optional OpenAI integration for enhanced matching
- **Ranking & Scoring**: Comprehensive candidate scoring system
- **Web Interface**: Clean, responsive UI for easy interaction

## Environment Variables Reference

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `FLASK_ENV` | Yes | Application environment | `production` |
| `SECRET_KEY` | Yes | Flask secret key for sessions | - |
| `DATABASE_URL` | Yes | PostgreSQL connection string | - |
| `OPENAI_API_KEY` | No | OpenAI API key for AI features | - |
| `OPENAI_MODEL` | No | OpenAI model to use | `gpt-4o-mini` |
| `USE_AI_MATCHING` | No | Enable AI matching features | `True` |
| `PORT` | No | Application port | `5000` |

## Support

For issues or questions:
1. Check the application logs in Render dashboard
2. Review the error handlers in `app/utils/error_handlers.py`
3. Ensure all environment variables are properly set

## Cost Considerations

- **Free Tier**: Includes 750 hours/month (enough for personal use)
- **Database**: Free PostgreSQL with 1GB storage
- **Scaling**: Can upgrade plans for higher traffic

The application is optimized for the free tier but can scale as needed.
