#!/usr/bin/env python3
"""Generate a test point cloud for PointMeistro testing"""

import numpy as np
import open3d as o3d

# Create a simple test scene: floor slab + steel beam
points_list = []
colors_list = []

# Concrete floor slab (gray)
for x in np.linspace(0, 10, 100):
    for y in np.linspace(0, 10, 100):
        points_list.append([x, y, 0])
        colors_list.append([0.6, 0.6, 0.6])  # Gray

# Steel I-beam (darker)
for x in np.linspace(4, 6, 50):
    for y in np.linspace(0, 10, 100):
        for z in np.linspace(3, 3.5, 10):
            points_list.append([x, y, z])
            colors_list.append([0.3, 0.3, 0.35])  # Dark metallic

# Create point cloud
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(np.array(points_list))
pcd.colors = o3d.utility.Vector3dVector(np.array(colors_list))

# Save as PLY
o3d.io.write_point_cloud("/home/mark/PointMeistro/test_scan.ply", pcd)
print(f"✅ Generated test scan: {len(points_list):,} points")
print("   Upload with: curl -X POST http://localhost:3000/segment -F 'file=@test_scan.ply'")
