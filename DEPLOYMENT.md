# PointMeistro Deployment Guide

Production deployment guide for WSL2 with NVIDIA GPU support.

---

## Prerequisites

### Hardware
- NVIDIA GPU (RTX 5000 Ada or similar)
- 16GB+ RAM
- 100GB+ SSD storage
- Windows 11 with WSL2

### Software
- WSL2 (Ubuntu 22.04+)
- Docker Desktop for Windows
- NVIDIA GPU drivers (Windows)
- NVIDIA Container Toolkit (WSL2)

---

## Initial Setup

### 1. Install WSL2

```powershell
# In PowerShell (Admin)
wsl --install
wsl --set-default-version 2
wsl --install -d Ubuntu-22.04
```

### 2. Install Docker Desktop

1. Download from https://www.docker.com/products/docker-desktop
2. Enable WSL2 backend in settings
3. Enable integration with Ubuntu distro

### 3. Install NVIDIA Drivers

1. Download latest drivers from NVIDIA website
2. Install on Windows host
3. Verify: Open PowerShell, run `nvidia-smi`

### 4. Install NVIDIA Container Toolkit (in WSL2)

```bash
cd /home/mark/PointMeistro
chmod +x install-nvidia-toolkit.sh
./install-nvidia-toolkit.sh
```

Verify GPU access:
```bash
./check-nvidia.sh
```

Should show:
```
✅ GPU is accessible in Docker containers!
```

---

## Deployment

### Option 1: Quick Start (Recommended)

```bash
cd /home/mark/PointMeistro
chmod +x setup.sh
./setup.sh
```

This script will:
1. Install Laravel 13 + packages
2. Build Docker containers
3. Start all services
4. Run migrations
5. Verify deployment

### Option 2: Manual Step-by-Step

```bash
cd /home/mark/PointMeistro

# 1. Install Laravel
cd laravel-app
composer create-project laravel/laravel . "^13.0"
composer require laravel/horizon laravel/sanctum laravel/reverb
php artisan key:generate
cd ..

# 2. Build containers
docker compose build --no-cache

# 3. Start services
docker compose up -d

# 4. Run migrations
docker compose exec app php artisan migrate --force

# 5. Start Horizon
docker compose exec app php artisan horizon &
```

---

## Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Laravel App | http://localhost | Main application |
| Horizon Dashboard | http://localhost/horizon | Queue monitoring |
| Python API | http://localhost:8001 | Segmentation service |
| WebSocket Server | ws://localhost:8080 | Real-time updates |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache & Queues |

---

## Configuration

### Environment Variables

Edit `laravel-app/.env`:

```env
APP_NAME=PointMeistro
APP_ENV=production
APP_DEBUG=false
APP_URL=http://localhost

DB_CONNECTION=pgsql
DB_HOST=postgres
DB_PORT=5432
DB_DATABASE=pointmeistro
DB_USERNAME=meistro
DB_PASSWORD=steel_scans_2026

REDIS_HOST=redis
QUEUE_CONNECTION=redis
BROADCAST_DRIVER=reverb

PYTHON_SEGMENTER_URL=http://segmenter:8001
```

### Docker Compose Overrides

For production-specific settings:

```bash
# Create docker-compose.override.yml
cat > docker-compose.override.yml << 'EOF'
version: '3.8'
services:
  app:
    environment:
      - APP_ENV=production
      - APP_DEBUG=false
EOF
```

---

## Security Hardening

### 1. Change Default Passwords

Edit `docker-compose.yml`:
```yaml
environment:
  - DB_PASSWORD=YOUR_STRONG_PASSWORD_HERE
```

### 2. Enable HTTPS (Production)

```bash
# Generate SSL certificate
docker compose exec nginx openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/nginx.key \
  -out /etc/nginx/ssl/nginx.crt
```

Update `nginx/nginx.conf`:
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/nginx.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx.key;
    # ... rest of config
}
```

### 3. Sanctum API Tokens

```bash
# Generate API token for client
docker compose exec app php artisan tinker
>>> $user = User::find(1);
>>> $token = $user->createToken('BLK360 Scanner')->plainTextToken;
>>> echo $token;
```

---

## Monitoring

### Horizon Dashboard

Access: http://localhost/horizon

Monitor:
- Job throughput
- Failed jobs
- Queue wait times
- Memory usage

### Docker Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f app
docker compose logs -f horizon
docker compose logs -f segmenter

# Last 100 lines
docker compose logs --tail=100 app
```

### Laravel Logs

```bash
tail -f laravel-app/storage/logs/laravel.log
```

### System Resources

```bash
# GPU usage
nvidia-smi -l 1

# Docker stats
docker stats

# Disk usage
df -h
```

---

## Backup

### Database Backup

```bash
# Backup
docker compose exec postgres pg_dump -U meistro pointmeistro > backup.sql

# Restore
docker compose exec -T postgres psql -U meistro pointmeistro < backup.sql
```

### Application Code

```bash
# Backup entire app
tar -czf pointmeistro-backup-$(date +%Y%m%d).tar.gz \
  laravel-app/ \
  python-segmenter/ \
  nginx/ \
  docker-compose.yml
```

### User Data (Scans)

```bash
# Backup storage
tar -czf storage-backup-$(date +%Y%m%d).tar.gz storage/
```

---

## Maintenance

### Update Dependencies

```bash
# Laravel packages
docker compose exec app composer update

# Python packages
docker compose build --no-cache segmenter
docker compose up -d segmenter
```

### Clear Caches

```bash
# Laravel caches
docker compose exec app php artisan cache:clear
docker compose exec app php artisan config:clear
docker compose exec app php artisan view:clear

# Redis cache
docker compose exec redis redis-cli FLUSHALL
```

### Restart Services

```bash
# All services
docker compose restart

# Specific service
docker compose restart app
docker compose restart segmenter
```

---

## Scaling

### Horizontal Scaling

Add more Horizon workers:

```yaml
# docker-compose.yml
horizon-worker-2:
  build:
    context: ./laravel-app
  command: php artisan horizon
  # ... same config as horizon
```

### Vertical Scaling

Increase container resources:

```yaml
services:
  segmenter:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 16G
```

---

## Troubleshooting

### GPU Not Detected

```bash
# Check NVIDIA driver
nvidia-smi

# Check Docker runtime
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# Reinstall toolkit
./install-nvidia-toolkit.sh
```

### Service Won't Start

```bash
# Check logs
docker compose logs segmenter

# Check ports
netstat -tulpn | grep -E '80|8001|8080|5432|6379'

# Rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Database Connection Error

```bash
# Check PostgreSQL
docker compose exec postgres psql -U meistro -d pointmeistro -c "SELECT 1"

# Reset database
docker compose down -v
docker compose up -d postgres
docker compose exec app php artisan migrate --force
```

### Out of Disk Space

```bash
# Clean Docker
docker system prune -af --volumes

# Clean old scans
find storage/scans -type f -mtime +30 -delete

# Clean Laravel logs
truncate -s 0 laravel-app/storage/logs/laravel.log
```

---

## Performance Tuning

### PHP Opcache

Add to Dockerfile:
```dockerfile
RUN docker-php-ext-install opcache
COPY opcache.ini /usr/local/etc/php/conf.d/opcache.ini
```

### PostgreSQL Tuning

```bash
docker compose exec postgres psql -U meistro -d pointmeistro

ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET work_mem = '64MB';
```

### Redis Memory

```yaml
redis:
  command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
```

---

## Production Checklist

- [ ] Change all default passwords
- [ ] Enable HTTPS
- [ ] Set `APP_DEBUG=false`
- [ ] Configure backups (database + storage)
- [ ] Set up monitoring (Horizon + logs)
- [ ] Document API endpoints
- [ ] Train production PointNet++ model
- [ ] Test failure scenarios
- [ ] Set up automated restarts
- [ ] Configure log rotation
- [ ] Test GPU failover (CPU fallback)
- [ ] Document recovery procedures

---

**Deployed and maintained by Mark Hubrich @ Adams Steel Service** 🔩
