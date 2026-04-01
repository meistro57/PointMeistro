"""
PointMeistro - Point Cloud Segmentation Service
Segments concrete, steel, rebar from BLK360 scans for Adams Steel Service
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import open3d as o3d
import numpy as np
import tempfile
import uuid
from pathlib import Path
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PointMeistro Segmenter", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Material class IDs
CLASSES = {
    0: "concrete",
    1: "steel",
    2: "rebar",
    3: "formwork",
    4: "other"
}

# Storage paths
STORAGE_DIR = Path("/storage")
OUTPUT_DIR = STORAGE_DIR / "segmented"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


class PlaceholderSegmenter:
    """Placeholder segmentation until real PointNet++ model is trained"""
    
    def segment(self, points: np.ndarray, colors: np.ndarray = None) -> np.ndarray:
        """
        Segment point cloud by material using heuristics
        
        Args:
            points: Nx3 array of XYZ coordinates
            colors: Nx3 array of RGB colors (optional)
        
        Returns:
            Nx1 array of class predictions
        """
        predictions = np.zeros(len(points), dtype=int)
        
        if colors is not None:
            # Convert RGB to grayscale
            gray = np.mean(colors, axis=1)
            
            # Concrete: gray surfaces (0.35-0.75 gray value)
            concrete_mask = (gray > 0.35) & (gray < 0.75)
            predictions[concrete_mask] = 0
            
            # Steel: metallic/darker or very bright surfaces
            steel_mask = (gray < 0.35) | (gray > 0.75)
            predictions[steel_mask] = 1
        else:
            # Without colors, segment by height (floor/ceiling likely concrete)
            z_values = points[:, 2]
            z_min, z_max = z_values.min(), z_values.max()
            z_range = z_max - z_min
            
            floor_mask = z_values < (z_min + z_range * 0.15)
            ceiling_mask = z_values > (z_max - z_range * 0.15)
            predictions[floor_mask | ceiling_mask] = 0
        
        return predictions


# Initialize segmenter
segmenter = PlaceholderSegmenter()


@app.get("/")
def root():
    return {
        "service": "PointMeistro Segmenter",
        "version": "1.0.0",
        "status": "running",
        "model": "placeholder (train PointNet++ for production)"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/segment")
async def segment_point_cloud(
    file: UploadFile = File(...),
    materials: str = "concrete,steel"
):
    """
    Segment uploaded point cloud by material
    
    Accepts: .e57, .ply, .pcd, .las, .laz
    Returns: URLs to segmented point clouds
    """
    try:
        # Parse requested materials
        material_list = [m.strip() for m in materials.split(',')]
        
        # Generate unique ID for this job
        job_id = str(uuid.uuid4())
        logger.info(f"Processing scan {job_id}: {file.filename}")
        
        # Save uploaded file
        suffix = Path(file.filename).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Load point cloud
        logger.info(f"Loading point cloud from {tmp_path}")
        pcd = load_point_cloud(tmp_path)
        
        if pcd is None:
            raise HTTPException(status_code=400, detail="Failed to load point cloud")
        
        # Extract points and colors
        points = np.asarray(pcd.points)
        colors = np.asarray(pcd.colors) if pcd.has_colors() else None
        
        logger.info(f"Point cloud loaded: {len(points):,} points")
        
        # Run segmentation
        logger.info("Running segmentation...")
        predictions = segmenter.segment(points, colors)
        
        # Filter by requested materials
        results = {}
        material_ids = [k for k, v in CLASSES.items() if v in material_list]
        
        for class_id in material_ids:
            material_name = CLASSES[class_id]
            mask = predictions == class_id
            
            if not mask.any():
                logger.warning(f"No points found for material: {material_name}")
                continue
            
            # Create segmented point cloud
            segmented_pcd = o3d.geometry.PointCloud()
            segmented_pcd.points = o3d.utility.Vector3dVector(points[mask])
            
            if colors is not None:
                segmented_pcd.colors = o3d.utility.Vector3dVector(colors[mask])
            
            # Save to storage
            output_path = OUTPUT_DIR / job_id / f"{material_name}.ply"
            output_path.parent.mkdir(exist_ok=True, parents=True)
            o3d.io.write_point_cloud(str(output_path), segmented_pcd)
            
            logger.info(f"Saved {material_name}: {mask.sum():,} points to {output_path}")
            
            results[material_name] = {
                "path": str(output_path),
                "url": f"/download/{job_id}/{material_name}.ply",
                "point_count": int(mask.sum())
            }
        
        # Cleanup
        Path(tmp_path).unlink()
        
        return JSONResponse({
            "job_id": job_id,
            "status": "completed",
            "total_points": int(len(points)),
            "materials": results
        })
    
    except Exception as e:
        logger.error(f"Segmentation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{job_id}/{filename}")
async def download_segmented(job_id: str, filename: str):
    """Download segmented point cloud"""
    file_path = OUTPUT_DIR / job_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=filename
    )


def load_point_cloud(file_path: str) -> o3d.geometry.PointCloud:
    """Load point cloud from various formats"""
    try:
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == ".e57":
            return load_e57(file_path)
        elif suffix in [".ply", ".pcd"]:
            return o3d.io.read_point_cloud(file_path)
        elif suffix in [".las", ".laz"]:
            return load_las(file_path)
        else:
            logger.error(f"Unsupported file format: {suffix}")
            return None
    
    except Exception as e:
        logger.error(f"Failed to load point cloud: {str(e)}")
        return None


def load_e57(file_path: str) -> o3d.geometry.PointCloud:
    """Load E57 file (BLK360 native format)"""
    try:
        import pye57
        
        e57 = pye57.E57(file_path)
        data = e57.read_scan(0, colors=True)
        
        # Extract XYZ
        points = np.column_stack([
            data["cartesianX"],
            data["cartesianY"],
            data["cartesianZ"]
        ])
        
        # Create point cloud
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        
        # Add colors if available
        if "colorRed" in data:
            colors = np.column_stack([
                data["colorRed"],
                data["colorGreen"],
                data["colorBlue"]
            ]) / 255.0
            pcd.colors = o3d.utility.Vector3dVector(colors)
        
        return pcd
    
    except ImportError:
        logger.error("pye57 not installed - cannot read E57 files")
        return None
    except Exception as e:
        logger.error(f"Failed to read E57: {str(e)}")
        return None


def load_las(file_path: str) -> o3d.geometry.PointCloud:
    """Load LAS/LAZ file"""
    try:
        import laspy
        
        las = laspy.read(file_path)
        
        # Extract XYZ
        points = np.vstack([las.x, las.y, las.z]).T
        
        # Create point cloud
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        
        # Add colors if available
        if hasattr(las, 'red'):
            colors = np.vstack([las.red, las.green, las.blue]).T / 65535.0
            pcd.colors = o3d.utility.Vector3dVector(colors)
        
        return pcd
    
    except ImportError:
        logger.error("laspy not installed - cannot read LAS files")
        return None
    except Exception as e:
        logger.error(f"Failed to read LAS: {str(e)}")
        return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
