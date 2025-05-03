# Deploying Jan-Rakshak to Render

This guide will help you deploy your Jan-Rakshak Flask application to Render.com.

## Prerequisites

1. Your code is pushed to GitHub
2. You have a Render.com account (sign up at https://render.com/)

## Step 1: Create a Procfile

Create a file named `Procfile` (no extension) in your project root:

```
web: gunicorn main:app
```

## Step 2: Add gunicorn to requirements.txt

Add gunicorn to your requirements.txt file:

```
gunicorn==20.1.0
```

## Step 3: Deploy to Render

1. Log in to your Render dashboard
2. Click "New" and select "Web Service"
3. Connect your GitHub account if you haven't already
4. Select your Jan-Rakshak repository
5. Configure your web service:
   - Name: jan-rakshak
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app`
   - Select the free plan
6. Click "Create Web Service"

Render will automatically deploy your application. Once the deployment is complete, you'll get a URL like `https://jan-rakshak.onrender.com` where your application is hosted.

## Step 4: Configure Environment Variables (if needed)

If your application uses environment variables:

1. Go to your web service dashboard
2. Click on "Environment" in the left sidebar
3. Add your environment variables
4. Click "Save Changes"

## Step 5: Set Up a Custom Domain (Optional)

To use your own domain (like jan-rakshak.com):

1. Purchase a domain from a domain registrar (like Namecheap, GoDaddy, etc.)
2. In your Render dashboard, go to your web service
3. Click on "Settings" and then "Custom Domain"
4. Follow the instructions to add your domain

## Troubleshooting

If you encounter any issues:

1. Check the logs in your Render dashboard
2. Make sure all dependencies are in your requirements.txt file
3. Ensure your application works locally before deploying
