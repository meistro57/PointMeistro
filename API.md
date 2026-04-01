# PointMeistro API Documentation

RESTful API for point cloud segmentation service.

Base URL: `http://localhost/api`

---

## Authentication

Uses Laravel Sanctum token-based authentication.

### Generate Token

```bash
docker compose exec app php artisan tinker
>>> $user = User::find(1);
>>> $token = $user->createToken('API Token')->plainTextToken;
>>> echo $token;
```

### Using Token

```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost/api/scans
```

---

## Endpoints

### Health Check

```
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "services": {
    "database": "connected",
    "redis": "connected",
    "segmenter": "running",
    "queue": "running"
  },
  "version": "2.0.0"
}
```

---

### Upload Scan

```
POST /api/scans/upload
```

**Headers:**
- `Authorization: Bearer {token}`
- `Content-Type: multipart/form-data`

**Body:**
- `file` (required): E57, PLY, or LAS file
- `materials[]` (optional): Array of materials to extract
  - Valid values: `concrete`, `steel`, `rebar`, `formwork`, `other`
  - Default: `["concrete", "steel"]`
- `project_name` (optional): Project identifier
- `location` (optional): Job site location

**Example:**
```bash
curl -X POST http://localhost/api/scans/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@scan.e57" \
  -F "materials[]=concrete" \
  -F "materials[]=steel" \
  -F "project_name=Navy Pier Expansion" \
  -F "location=Chicago, IL"
```

**Response:**
```json
{
  "scan_id": "uuid-here",
  "job_id": "job-uuid-here",
  "status": "queued",
  "filename": "scan.e57",
  "size_bytes": 45678901,
  "materials_requested": ["concrete", "steel"],
  "estimated_processing_time": "2-3 minutes",
  "websocket_channel": "scans.uuid-here"
}
```

**Status Codes:**
- `201` - Created
- `400` - Invalid file format
- `413` - File too large (max 500MB)
- `422` - Validation error
- `401` - Unauthorized

---

### Get Scan Status

```
GET /api/scans/{scan_id}
```

**Headers:**
- `Authorization: Bearer {token}`

**Response:**
```json
{
  "scan_id": "uuid-here",
  "status": "processing",
  "progress": 65,
  "filename": "scan.e57",
  "uploaded_at": "2026-03-31T19:46:34Z",
  "started_processing_at": "2026-03-31T19:47:01Z",
  "materials": [
    {
      "material": "concrete",
      "status": "complete",
      "point_count": 1234567,
      "download_url": "/api/scans/uuid-here/download/concrete"
    },
    {
      "material": "steel",
      "status": "processing",
      "point_count": null,
      "download_url": null
    }
  ]
}
```

**Status Values:**
- `queued` - Waiting in queue
- `processing` - Currently segmenting
- `complete` - Ready to download
- `failed` - Processing error

**Status Codes:**
- `200` - OK
- `404` - Scan not found
- `401` - Unauthorized

---

### Download Segmented Material

```
GET /api/scans/{scan_id}/download/{material}
```

**Headers:**
- `Authorization: Bearer {token}`

**Parameters:**
- `format` (optional): Output format
  - Valid values: `ply` (default), `las`, `e57`

**Example:**
```bash
curl -O -J \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost/api/scans/uuid-here/download/concrete?format=ply
```

**Response:**
- Binary file download (PLY, LAS, or E57)
- Filename in `Content-Disposition` header

**Status Codes:**
- `200` - OK
- `404` - Scan or material not found
- `425` - Processing not complete
- `401` - Unauthorized

---

### List Scans

```
GET /api/scans
```

**Headers:**
- `Authorization: Bearer {token}`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Results per page (default: 20, max: 100)
- `status` (optional): Filter by status
- `project_name` (optional): Filter by project

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/api/scans?page=1&per_page=20&status=complete"
```

**Response:**
```json
{
  "data": [
    {
      "scan_id": "uuid-1",
      "filename": "scan1.e57",
      "status": "complete",
      "uploaded_at": "2026-03-31T10:00:00Z",
      "project_name": "Navy Pier"
    }
  ],
  "meta": {
    "current_page": 1,
    "per_page": 20,
    "total": 42,
    "last_page": 3
  }
}
```

---

### Delete Scan

```
DELETE /api/scans/{scan_id}
```

**Headers:**
- `Authorization: Bearer {token}`

**Response:**
```json
{
  "message": "Scan deleted successfully",
  "scan_id": "uuid-here"
}
```

**Status Codes:**
- `200` - Deleted
- `404` - Scan not found
- `401` - Unauthorized

---

## WebSocket Events

Connect to: `ws://localhost:8080`

### Subscribe to Scan Updates

```javascript
import Echo from 'laravel-echo';
import Pusher from 'pusher-js';

window.Pusher = Pusher;

window.Echo = new Echo({
    broadcaster: 'reverb',
    key: 'local-key',
    wsHost: 'localhost',
    wsPort: 8080,
    forceTLS: false,
    enabledTransports: ['ws']
});

// Listen to scan progress
Echo.channel('scans.' + scanId)
    .listen('ScanProcessingStarted', (e) => {
        console.log('Processing started:', e);
    })
    .listen('ScanProcessingProgress', (e) => {
        console.log('Progress:', e.progress + '%');
    })
    .listen('ScanProcessingComplete', (e) => {
        console.log('Complete:', e);
    })
    .listen('ScanProcessingFailed', (e) => {
        console.error('Failed:', e.error);
    });
```

### Events

#### ScanProcessingStarted
```json
{
  "scan_id": "uuid",
  "started_at": "2026-03-31T19:47:01Z"
}
```

#### ScanProcessingProgress
```json
{
  "scan_id": "uuid",
  "progress": 65,
  "current_step": "Segmenting steel",
  "points_processed": 1234567
}
```

#### ScanProcessingComplete
```json
{
  "scan_id": "uuid",
  "completed_at": "2026-03-31T19:50:15Z",
  "materials": [
    {
      "material": "concrete",
      "point_count": 1234567,
      "download_url": "/api/scans/uuid/download/concrete"
    }
  ]
}
```

#### ScanProcessingFailed
```json
{
  "scan_id": "uuid",
  "error": "Invalid file format",
  "failed_at": "2026-03-31T19:47:30Z"
}
```

---

## Rate Limiting

- **Upload**: 10 requests per minute
- **Status Check**: 60 requests per minute
- **Download**: 30 requests per minute

**Headers:**
- `X-RateLimit-Limit`: Total allowed
- `X-RateLimit-Remaining`: Remaining requests
- `Retry-After`: Seconds until reset

**Response (429 Too Many Requests):**
```json
{
  "message": "Too many requests",
  "retry_after": 45
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "message": "Error description",
  "errors": {
    "field_name": ["Validation error details"]
  }
}
```

### Common Status Codes

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `413` - Payload Too Large
- `422` - Unprocessable Entity
- `429` - Too Many Requests
- `500` - Internal Server Error

---

## Python Segmenter API (Direct)

For advanced users who want to bypass Laravel and call the Python service directly.

**Base URL:** `http://localhost:8001`

### Segment Point Cloud

```
POST /segment
```

**Body:**
- `file`: Point cloud file (E57, PLY, LAS)
- `materials`: Comma-separated material list

**Example:**
```bash
curl -X POST http://localhost:8001/segment \
  -F "file=@scan.e57" \
  -F "materials=concrete,steel"
```

**Response:**
```json
{
  "status": "success",
  "materials": {
    "concrete": {
      "point_count": 1234567,
      "output_file": "/storage/segmented/scan_concrete.ply"
    },
    "steel": {
      "point_count": 456789,
      "output_file": "/storage/segmented/scan_steel.ply"
    }
  },
  "processing_time_seconds": 45.2
}
```

---

## SDK Examples

### cURL

```bash
# Upload
curl -X POST http://localhost/api/scans/upload \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@scan.e57"

# Check status
curl -H "Authorization: Bearer TOKEN" \
  http://localhost/api/scans/SCAN_ID

# Download
curl -O -J -H "Authorization: Bearer TOKEN" \
  http://localhost/api/scans/SCAN_ID/download/concrete
```

### Python

```python
import requests

API_URL = "http://localhost/api"
TOKEN = "your-token-here"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Upload
with open("scan.e57", "rb") as f:
    files = {"file": f}
    data = {"materials[]": ["concrete", "steel"]}
    response = requests.post(
        f"{API_URL}/scans/upload",
        headers=headers,
        files=files,
        data=data
    )
    scan = response.json()

# Check status
response = requests.get(
    f"{API_URL}/scans/{scan['scan_id']}",
    headers=headers
)
status = response.json()

# Download
response = requests.get(
    f"{API_URL}/scans/{scan['scan_id']}/download/concrete",
    headers=headers
)
with open("concrete.ply", "wb") as f:
    f.write(response.content)
```

### JavaScript

```javascript
const API_URL = 'http://localhost/api';
const TOKEN = 'your-token-here';

// Upload
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('materials[]', 'concrete');
formData.append('materials[]', 'steel');

const response = await fetch(`${API_URL}/scans/upload`, {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${TOKEN}`
    },
    body: formData
});

const scan = await response.json();

// Check status
const statusResponse = await fetch(`${API_URL}/scans/${scan.scan_id}`, {
    headers: {
        'Authorization': `Bearer ${TOKEN}`
    }
});

// Download
const blob = await fetch(`${API_URL}/scans/${scan.scan_id}/download/concrete`, {
    headers: {
        'Authorization': `Bearer ${TOKEN}`
    }
}).then(r => r.blob());

const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'concrete.ply';
a.click();
```

---

**API Version: 2.0.0**  
**Last Updated: March 31, 2026**
