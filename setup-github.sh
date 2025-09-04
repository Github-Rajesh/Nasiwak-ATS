#!/bin/bash

# Replace 'YOUR-GITHUB-USERNAME' with your actual GitHub username
# Replace 'YOUR-REPO-NAME' with your chosen repository name

echo "Setting up GitHub repository..."

# Add the new remote (update with your details)
git remote add origin https://github.com/YOUR-GITHUB-USERNAME/YOUR-REPO-NAME.git

# Push to GitHub
git branch -M main
git push -u origin main

echo "Repository setup complete!"
echo "Your render.yaml file should now be available on GitHub"
echo "You can proceed with Render deployment"
