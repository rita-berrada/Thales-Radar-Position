import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load data (skip header line)
lats = np.loadtxt('latitudes.txt', skiprows=1)
lons = np.loadtxt('longitudes.txt', skiprows=1)

# Load terrain data handling variable row lengths
expected_rows = len(lats)  # Match number of latitudes
expected_cols = len(lons)  # Match number of longitudes

with open('terrain.txt', 'r') as f:
    lines = f.readlines()
    terrain_rows = []
    for line in lines:
        values = line.strip().split()
        if values:  # Skip empty lines
            row = [float(v) if v != '-1' else np.nan for v in values]
            # Pad or truncate to expected width
            if len(row) < expected_cols:
                row.extend([np.nan] * (expected_cols - len(row)))
            elif len(row) > expected_cols:
                row = row[:expected_cols]
            terrain_rows.append(row)
    
    terrain = np.array(terrain_rows)
    
    # Trim or pad to match expected number of rows (latitudes)
    if terrain.shape[0] > expected_rows:
        terrain = terrain[:expected_rows, :]  # Trim extra rows
    elif terrain.shape[0] < expected_rows:
        # Pad with NaN rows if needed
        padding = np.full((expected_rows - terrain.shape[0], expected_cols), np.nan)
        terrain = np.vstack([terrain, padding])

# Create meshgrid
lon_grid, lat_grid = np.meshgrid(lons, lats)

# Nice Airport coordinates
nice_lat = 43.6584
nice_lon = 7.2159

# 3D surface plot
fig = plt.figure(figsize=(12, 5))
ax1 = fig.add_subplot(121, projection='3d')
ax1.plot_surface(lon_grid, lat_grid, terrain, cmap='terrain', alpha=0.8)
ax1.set_xlabel('Longitude')
ax1.set_ylabel('Latitude')
ax1.set_zlabel('Elevation (m)')
ax1.set_title('3D Terrain Surface')

# 2D map with airport
ax2 = fig.add_subplot(122)
im = ax2.contourf(lon_grid, lat_grid, terrain, levels=20, cmap='terrain')
ax2.plot(nice_lon, nice_lat, 'ro', markersize=10, label='Nice Airport')
ax2.text(nice_lon, nice_lat, 'Nice Airport', fontsize=9, ha='left', va='bottom')
ax2.set_xlabel('Longitude')
ax2.set_ylabel('Latitude')
ax2.set_title('2D Terrain Map')
plt.colorbar(im, ax=ax2, label='Elevation (m)')
ax2.legend()

plt.tight_layout()
plt.show()
