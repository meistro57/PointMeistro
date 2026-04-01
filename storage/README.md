# Storage Directory

This directory holds user uploads and processing outputs.

**DO NOT COMMIT USER DATA TO GIT**

## Structure

```
storage/
├── scans/
│   └── raw/              # Original E57/PLY/LAS uploads
└── segmented/            # Processed output files
    ├── concrete/         # Concrete-only point clouds
    ├── steel/           # Steel-only point clouds
    └── composite/       # Multi-material outputs
```

## Volume Mount

This directory is mounted as a Docker volume and shared between:
- Laravel app (file uploads)
- Python segmenter (read/write processing)
- Nginx (static file serving for downloads)

## Cleanup

Run periodic cleanup to avoid filling disk:

```bash
# Delete processed files older than 30 days
find storage/segmented -type f -mtime +30 -delete

# Delete abandoned uploads (no associated database record)
docker compose exec app php artisan scans:cleanup
```

## File Formats

- **Input**: E57 (BLK360 native), PLY, LAS/LAZ
- **Output**: PLY (ASCII or binary), LAS
