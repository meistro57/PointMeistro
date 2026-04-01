# Contributing to PointMeistro

This is a private internal tool for Adams Steel Service. External contributions are not currently accepted.

## For Internal Team Members

### Development Workflow

1. **Clone the Repository**
   ```bash
   git clone https://github.com/meistro57/PointMeistro.git
   cd PointMeistro
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow Laravel 13 best practices
   - Use PSR-12 coding standards
   - Write tests for new features
   - Update documentation

4. **Test Your Changes**
   ```bash
   # Run Laravel tests
   docker compose exec app php artisan test
   
   # Run Python tests
   docker compose exec segmenter pytest
   
   # Check code style
   docker compose exec app ./vendor/bin/pint
   ```

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Open PR on GitHub
   - Request review from Mark Hubrich
   - Address any feedback

### Code Style

**PHP/Laravel:**
- PSR-12 coding standard
- Laravel conventions (Eloquent, Resources, Jobs)
- Type hints on all methods
- Descriptive variable names

**Python:**
- PEP 8 style guide
- Type hints (Python 3.10+ syntax)
- Docstrings for all functions
- FastAPI best practices

### Testing

**Laravel Tests:**
```bash
# Feature tests
docker compose exec app php artisan test --filter=ScanTest

# Unit tests
docker compose exec app php artisan test --testsuite=Unit
```

**Python Tests:**
```bash
# All tests
docker compose exec segmenter pytest

# With coverage
docker compose exec segmenter pytest --cov=.
```

### Database Migrations

```bash
# Create migration
docker compose exec app php artisan make:migration create_scans_table

# Run migrations
docker compose exec app php artisan migrate

# Rollback
docker compose exec app php artisan migrate:rollback
```

### Queue Jobs

```bash
# Create job
docker compose exec app php artisan make:job ProcessScanJob

# Test job manually
docker compose exec app php artisan tinker
>>> ProcessScanJob::dispatch($scanId);
```

### Broadcasting Events

```bash
# Create event
docker compose exec app php artisan make:event ScanProcessed

# Test WebSocket
wscat -c ws://localhost:8080
```

## Architecture Decisions

### Why Microservices?

**Laravel**: Handles orchestration, API, database, auth, queues  
**Python**: Handles GPU-intensive point cloud segmentation

This separation allows:
- Independent scaling
- Language-specific optimizations
- GPU isolation
- Clear boundaries

### Why PostgreSQL?

- Better full-text search than MySQL
- Native JSONB support
- Point cloud metadata storage
- Spatial extensions (PostGIS future)

### Why Redis?

- Queue backend for Horizon
- Session storage
- Cache layer
- Pub/sub for broadcasting

### Why Docker?

- Consistent environments (dev/prod)
- Easy GPU passthrough (NVIDIA runtime)
- Service isolation
- Simplified deployment

## Common Tasks

### Adding a New Material Class

1. Update Python segmentation model
2. Add migration for new material type
3. Update `ScanMaterial` model
4. Update API responses
5. Update documentation

### Training a New Model

1. Export Tekla models to IFC
2. Generate training data:
   ```bash
   python scripts/generate_training_data.py --tekla_library /path/to/models
   ```
3. Train PointNet++:
   ```bash
   cd python-segmenter/training
   python train.py --dataset_path /training_data
   ```
4. Deploy model:
   ```bash
   cp trained_model.pth models/concrete_steel_segmentation.pth
   docker compose restart segmenter
   ```

### Debugging

**Laravel Logs:**
```bash
docker compose logs -f app
tail -f laravel-app/storage/logs/laravel.log
```

**Python Logs:**
```bash
docker compose logs -f segmenter
```

**Database Queries:**
```bash
docker compose exec postgres psql -U meistro -d pointmeistro
```

**Redis Inspection:**
```bash
docker compose exec redis redis-cli
KEYS *
GET some_key
```

## Security

- Never commit `.env` files
- Never commit API keys or secrets
- Never commit user scan data
- Never commit trained models (large files)
- Always use Sanctum tokens for API auth
- Validate all user inputs
- Sanitize file uploads

## Performance

- Use queue jobs for long-running tasks
- Cache expensive queries
- Optimize database indexes
- Use eager loading to avoid N+1 queries
- Chunk large point clouds
- Monitor Horizon dashboard

## Documentation

- Update README for user-facing changes
- Update REQUIREMENTS for dependency changes
- Add inline comments for complex logic
- Update API documentation
- Add examples for new features

## Questions?

Contact Mark Hubrich (Meistro) via:
- GitHub issues
- Chat Bridge integration
- QMU Discourse forum

---

**Built by Mark Hubrich + Claude at Adams Steel Service** 🔩
