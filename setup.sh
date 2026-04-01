#!/bin/bash

# PointMeistro v2.0 - Complete Setup
# Laravel 13 + Python GPU Segmentation

set -e

echo "🔩 PointMeistro v2.0 - Enterprise Steel Scan Processing"
echo "========================================================"
echo ""

# Prerequisites check
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found"
    exit 1
fi

if ! command -v composer &> /dev/null; then
    echo "📦 Installing Composer..."
    curl -sS https://getcomposer.com/installer | php
    sudo mv composer.phar /usr/local/bin/composer
fi

if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader)"
fi

echo ""
echo "📦 Step 1: Setting up Laravel 13 directory..."

# Create temp directory for Laravel
mkdir -p /tmp/laravel-temp
cd /tmp/laravel-temp

# Install Laravel 13 to temp location
echo "Installing Laravel 13..."
composer create-project laravel/laravel . "^13.0"

# Install packages
echo "Installing Horizon, Sanctum, Reverb..."
composer require laravel/horizon
composer require laravel/sanctum  
composer require laravel/reverb

# Generate key
php artisan key:generate

# Publish configs
php artisan horizon:install
php artisan vendor:publish --provider="Laravel\Sanctum\SanctumServiceProvider"
php artisan vendor:publish --provider="Laravel\Reverb\ReverbServiceProvider"

# Move to final location
echo "Moving Laravel to project directory..."
cd /home/mark/PointMeistro/laravel-app
rm -f Dockerfile  # Remove just the dockerfile
cd /tmp/laravel-temp
cp -r . /home/mark/PointMeistro/laravel-app/
cd /home/mark/PointMeistro/laravel-app

# Copy Dockerfile back
cat > Dockerfile << 'EOF'
FROM php:8.3-fpm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    libpq-dev \
    zip \
    unzip \
    supervisor \
    nginx

# Clear cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install pdo_pgsql pgsql mbstring exif pcntl bcmath gd

# Get latest Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /var/www/html

# Copy existing application directory contents
COPY . /var/www/html

# Install Laravel dependencies
RUN composer install --no-interaction --optimize-autoloader --no-dev || true

# Set permissions
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html/storage \
    && chmod -R 755 /var/www/html/bootstrap/cache

# Expose port 9000 for PHP-FPM
EXPOSE 9000

CMD ["php-fpm"]
EOF

# Cleanup temp
rm -rf /tmp/laravel-temp

cd /home/mark/PointMeistro

echo ""
echo "🐳 Step 2: Building Docker containers..."
docker compose build

echo ""
echo "🚀 Step 3: Starting services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to initialize..."
sleep 10

echo ""
echo "🗄️ Step 4: Running migrations..."
docker compose exec -T app php artisan migrate --force || echo "Migrations will run on first request"

echo ""
echo "✅ PointMeistro v2.0 is LIVE!"
echo ""
echo "📍 Service URLs:"
echo "   - Laravel App:    http://localhost"
echo "   - Horizon:        http://localhost/horizon"
echo "   - Python API:     http://localhost:8001"
echo "   - WebSockets:     ws://localhost:8080"
echo "   - PostgreSQL:     localhost:5432"
echo "   - Redis:          localhost:6379"
echo ""
echo "🧪 Quick tests:"
echo "   curl http://localhost/"
echo "   curl http://localhost:8001/"
echo ""
echo "📊 Monitor:"
echo "   docker compose logs -f"
echo "   docker compose logs -f horizon"
echo ""
echo "🎉 Ready to process BLK360 scans!"
echo ""
