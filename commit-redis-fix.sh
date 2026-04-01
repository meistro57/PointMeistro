#!/bin/bash
# Commit the Redis extension fix to git

cd ~/PointMeistro

# Check git status
echo "========================================="
echo "Current Git Status:"
echo "========================================="
git status

echo ""
echo "========================================="
echo "Staging Dockerfile changes..."
echo "========================================="
git add laravel-app/Dockerfile

echo ""
echo "========================================="
echo "Committing changes..."
echo "========================================="
git commit -m "Fix: Add PHP Redis extension to Dockerfile

- Added pecl install redis to Dockerfile
- Enables docker-php-ext-enable redis
- Fixes Horizon container crash loop due to missing Redis extension
- All Laravel containers (app, horizon, reverb) now have Redis support"

echo ""
echo "========================================="
echo "Pushing to remote..."
echo "========================================="
git push

echo ""
echo "========================================="
echo "DONE! Changes committed and pushed."
echo "========================================="
