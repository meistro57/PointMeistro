# Laravel 13 Requirements

## PHP Version
- **Minimum**: PHP 8.4.0 (REQUIRED)
- **Recommended**: PHP 8.4.0+ (what we're using)
- Laravel 13 does NOT work with PHP 8.3 or earlier

## Required PHP Extensions
- BCMath
- Ctype
- cURL
- DOM
- Fileinfo
- JSON
- Mbstring
- OpenSSL
- PCRE
- PDO
- Tokenizer
- XML
- PostgreSQL (pdo_pgsql)
- Redis (via phpredis or predis)
- GD (for image manipulation)

## Composer Version
- **Minimum**: 2.7+

## Our Dockerfile Configuration

```dockerfile
FROM php:8.4-fpm

# Extensions installed:
RUN docker-php-ext-install \
    pdo_pgsql \    # PostgreSQL driver
    pgsql \        # PostgreSQL native
    mbstring \     # Multibyte string support
    exif \         # Image metadata
    pcntl \        # Process control
    bcmath \       # Arbitrary precision math
    gd             # Image processing
```

## Verification

Once containers are built, verify PHP version:

```bash
docker compose exec app php -v
# Should show: PHP 8.4.x

docker compose exec app php -m
# Should list all required extensions
```

## Laravel 13 New Features We're Using

1. **Improved Queue Performance** - Horizon dashboard
2. **Native WebSocket Support** - Reverb (no Pusher needed)
3. **Enhanced API Resources** - Cleaner response formatting
4. **Better PostgreSQL Support** - Native full-text search
5. **Improved Broadcasting** - Real-time scan processing updates
6. **PHP 8.4 Features** - Property hooks, asymmetric visibility

## Compatibility Matrix

| Package | Version | PHP Requirement |
|---------|---------|-----------------|
| Laravel Framework | 13.x | PHP 8.4+ |
| Laravel Horizon | 6.x | PHP 8.4+ |
| Laravel Sanctum | 4.x | PHP 8.4+ |
| Laravel Reverb | 1.x | PHP 8.4+ |

✅ **All packages require PHP 8.4**

## IMPORTANT: Version Jump

Laravel 13 is a major breaking change requiring PHP 8.4. This is NOT backward compatible with PHP 8.3 or earlier.
