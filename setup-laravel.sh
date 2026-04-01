#!/bin/bash

# PointMeistro - Laravel 13 Setup
# Complete enterprise-grade steel scan processing

set -e

echo "🔩 PointMeistro v2.0 - Laravel 13 Full Stack"
echo "=============================================="
echo ""

cd /home/mark/PointMeistro/laravel-app

# Check if Laravel is already installed
if [ ! -f "composer.json" ]; then
    echo "📦 Installing Laravel 13..."
    composer create-project laravel/laravel . "^13.0"
    
    echo ""
    echo "📚 Installing additional packages..."
    
    # Horizon for queue management
    composer require laravel/horizon
    
    # Sanctum for API authentication  
    composer require laravel/sanctum
    
    # Reverb for WebSockets
    composer require laravel/reverb
    
    echo "✅ Laravel 13 installed!"
else
    echo "✅ Laravel already installed"
fi

echo ""
echo "🔧 Configuring Laravel..."

# Generate app key if not exists
if ! grep -q "APP_KEY=base64:" .env 2>/dev/null; then
    php artisan key:generate
fi

# Publish Horizon assets
php artisan horizon:install

# Publish Sanctum config
php artisan vendor:publish --provider="Laravel\Sanctum\SanctumServiceProvider"

# Publish Reverb config
php artisan vendor:publish --provider="Laravel\Reverb\ReverbServiceProvider"

echo ""
echo "✅ Laravel configuration complete!"
echo ""
echo "Next steps:"
echo "  1. Run migrations: php artisan migrate"
echo "  2. Start Horizon: php artisan horizon"
echo "  3. Start Reverb: php artisan reverb:start"
echo ""
