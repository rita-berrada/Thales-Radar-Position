# RF Coverage Analysis Tool (CAT) - User's Manual

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Data Input](#data-input)
4. [Usage Guide](#usage-guide)
5. [Output Formats](#output-formats)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)
8. [Technical Specifications](#technical-specifications)

---

## Introduction

### Purpose

The RF Coverage Analysis Tool (CAT) is a comprehensive software solution for performing optical/line-of-sight (LOS) coverage analysis for radar systems. The tool is designed to support:

- **PSR (Primary Surveillance Radar)** systems
- **MSSR (Monopulse Secondary Surveillance Radar)** systems
- **ADS-B (Automatic Dependent Surveillance-Broadcast)** sensors

The tool provides accurate assessments of radar coverage during design phases of new projects, including the evaluation of obstacles and their impact on system performance.

### Capabilities

- **Optical Coverage Analysis**: Line-of-sight visibility calculations for given radar positions
- **Obstacle Evaluation**: Assessment of terrain and obstacles affecting signal propagation
- **Multi-Flight Level Analysis**: Coverage maps for 8 standard flight levels (FL5, FL10, FL20, FL50, FL100, FL200, FL300, FL400)
- **DTED 1 Format Support**: Direct processing of Digital Terrain Elevation Data files
- **Google Earth Integration**: Export coverage maps to KML/KMZ format for visualization
- **Interactive Visualization**: 2D maps with flight level selection

### Compliance

This tool complies with DRAC tender requirements for RF coverage analysis software, providing:
- RF analysis software
- Python source code
- Comprehensive documentation

---

## Installation

### Requirements

- **Python**: Version 3.7 or higher
- **Operating System**: Windows, Linux, or macOS

### Dependencies

The tool requires the following Python packages:

```
numpy >= 1.19.0
matplotlib >= 3.3.0
```

Optional (for progress bars):
```
tqdm >= 4.60.0
```

### Installation Steps

1. **Install Python** (if not already installed):
   - Download from [python.org](https://www.python.org/downloads/)
   - Ensure Python is added to your system PATH

2. **Install required packages**:
   ```bash
   pip install numpy matplotlib
   ```

3. **Install optional packages** (recommended):
   ```bash
   pip install tqdm
   ```

4. **Verify installation**:
   ```bash
   python -c "import numpy; import matplotlib; print('Installation successful')"
   ```

### File Structure

Ensure your project directory contains:
```
Thales-Radar-Position/
├── LOS.py                    # Line-of-sight calculation functions
├── visualize_terrain.py     # Terrain loading utilities
├── coverage_analysis.py     # Coverage map computation
├── visualize_coverage.py    # Visualization functions
├── export_kml.py            # KML/KMZ export functions
├── main_coverage.py         # Main execution script
├── terrain_mat.npz          # Terrain data file (DTED 1 format)
└── docs/
    └── USER_MANUAL.md       # This document
```

---

## Data Input

### Terrain Data Format

The tool requires terrain data in **DTED 1 format**, which must be converted to a NumPy `.npz` file containing:

- **Latitude array** (`lat`): 1D array of latitude values in degrees
- **Longitude array** (`lon`): 1D array of longitude values in degrees
- **Terrain elevation** (`ter`): 2D array of elevation values in meters above sea level

**DTED 1 Specifications:**
- Grid spacing: 3-arc-second (~90 meters)
- Elevation values: Meters above sea level (MSL)
- Coordinate system: WGS84 (latitude/longitude)

### Terrain File Structure

The `.npz` file should be created with:
```python
import numpy as np
np.savez('terrain_mat.npz', lat=lats, lon=lons, ter=Z)
```

Where:
- `lats`: 1D array of shape `(n_lats,)`
- `lons`: 1D array of shape `(n_lons,)`
- `Z`: 2D array of shape `(n_lats, n_lons)`

### Radar Position

The radar position is specified by:
- **Latitude** (`radar_lat`): Decimal degrees (e.g., 43.6584)
- **Longitude** (`radar_lon`): Decimal degrees (e.g., 7.2159)
- **Height AGL** (`radar_height_agl_m`): Height above ground level in meters

---

## Usage Guide

### Quick Start

1. **Prepare terrain data**: Ensure `terrain_mat.npz` is in the project directory

2. **Run the main script**:
   ```bash
   python main_coverage.py
   ```

3. **Follow the prompts**:
   - The script will load terrain data
   - Compute coverage maps for all flight levels
   - Display interactive visualization
   - Optionally export to KMZ

### Programmatic Usage

#### Basic Example

```python
from visualize_terrain import load_terrain_npz
from coverage_analysis import compute_all_coverage_maps
from visualize_coverage import interactive_coverage_viewer
from export_kml import export_all_coverage_to_kmz

# Load terrain
lats, lons, Z = load_terrain_npz('terrain_mat.npz')

# Define radar position
radar_lat = 43.6584
radar_lon = 7.2159
radar_height_agl_m = 50.0

# Flight levels
flight_levels = [5, 10, 20, 50, 100, 200, 300, 400]

# Compute coverage maps
coverage_maps = compute_all_coverage_maps(
    radar_lat, radar_lon, radar_height_agl_m,
    flight_levels, lats, lons, Z
)

# Visualize
interactive_coverage_viewer(coverage_maps, lats, lons, radar_lat, radar_lon)

# Export to KMZ
export_all_coverage_to_kmz(
    coverage_maps, lats, lons, radar_lat, radar_lon,
    output_path='radar_coverage.kmz'
)
```

#### Single Flight Level

```python
from coverage_analysis import compute_coverage_map

# Compute coverage for single flight level
coverage_map = compute_coverage_map(
    radar_lat=43.6584,
    radar_lon=7.2159,
    radar_height_agl_m=50.0,
    flight_level=100,
    lats=lats,
    lons=lons,
    Z=Z
)
```

#### Custom LOS Parameters

```python
coverage_maps = compute_all_coverage_maps(
    radar_lat, radar_lon, radar_height_agl_m,
    flight_levels, lats, lons, Z,
    n_samples=800,      # More samples for higher accuracy
    margin_m=10.0       # 10m safety margin
)
```

### Interactive Viewer Controls

When using `interactive_coverage_viewer()`:

- **Right Arrow** or **'n'**: Next flight level
- **Left Arrow** or **'p'**: Previous flight level
- **'q'**: Quit viewer

The viewer displays:
- Coverage map with color coding (green=visible, red=blocked)
- Radar position marker
- Coverage percentage statistics

---

## Output Formats

### Coverage Maps (NumPy Arrays)

Coverage maps are returned as dictionaries:
```python
{
    5.0: <2D boolean array>,   # FL5 coverage
    10.0: <2D boolean array>,  # FL10 coverage
    ...
    400.0: <2D boolean array>   # FL400 coverage
}
```

Each array:
- **Shape**: `(len(lats), len(lons))` - matches terrain grid
- **Data type**: `bool`
- **Values**: `True` = visible, `False` = blocked

### KML/KMZ Export

The tool exports coverage maps to **KMZ format** (ZIP-compressed KML) for Google Earth visualization.

**Features:**
- Separate folders for each flight level
- Color-coded polygons (green=visible, red=blocked)
- Radar position marker
- Proper coordinate system (WGS84)

**Usage in Google Earth:**
1. Open the `.kmz` file in Google Earth
2. Navigate to the flight level folders in the sidebar
3. Toggle visibility of different flight levels
4. Zoom and pan to explore coverage areas

### Visualization Outputs

**Interactive Viewer:**
- Real-time flight level switching
- Coverage statistics display
- Zoom and pan capabilities

**Grid View:**
- All 8 flight levels displayed simultaneously
- Useful for comparison and overview
- Can be saved as image file

---

## Examples

### Example 1: Basic Coverage Analysis

```python
from visualize_terrain import load_terrain_npz
from coverage_analysis import compute_all_coverage_maps
from visualize_coverage import plot_all_coverage_maps
import matplotlib.pyplot as plt

# Load terrain
lats, lons, Z = load_terrain_npz('terrain_mat.npz')

# Radar at Nice Airport
radar_lat = 43.6584
radar_lon = 7.2159
radar_height_agl_m = 50.0

# Compute all coverage maps
coverage_maps = compute_all_coverage_maps(
    radar_lat, radar_lon, radar_height_agl_m,
    [5, 10, 20, 50, 100, 200, 300, 400],
    lats, lons, Z
)

# Display grid view
fig = plot_all_coverage_maps(coverage_maps, lats, lons, radar_lat, radar_lon)
plt.savefig('coverage_overview.png', dpi=300)
plt.show()
```

### Example 2: Export Single Flight Level

```python
from coverage_analysis import compute_coverage_map
from export_kml import export_coverage_to_kml

# Compute FL100 coverage
coverage_map = compute_coverage_map(
    43.6584, 7.2159, 50.0, 100, lats, lons, Z
)

# Export to KML
export_coverage_to_kml(
    coverage_map, lats, lons, 100,
    'coverage_fl100.kml',
    radar_lat=43.6584, radar_lon=7.2159
)
```

### Example 3: Coverage Statistics

```python
import numpy as np

coverage_maps = compute_all_coverage_maps(...)

print("Coverage Statistics:")
print("-" * 40)
for fl, coverage in coverage_maps.items():
    visible_pct = np.sum(coverage) / coverage.size * 100
    blocked_pct = 100 - visible_pct
    print(f"FL{fl:3.0f}: {visible_pct:6.2f}% visible, {blocked_pct:6.2f}% blocked")
```

---

## Troubleshooting

### Common Issues

#### 1. Terrain File Not Found

**Error**: `FileNotFoundError: terrain_mat.npz not found`

**Solution**: 
- Ensure `terrain_mat.npz` is in the same directory as the scripts
- Check file path is correct
- Verify file permissions

#### 2. Memory Issues with Large Grids

**Error**: Out of memory errors during computation

**Solution**:
- Reduce grid resolution if possible
- Process flight levels individually
- Use a machine with more RAM
- Consider downsampling terrain data

#### 3. KML Export Too Large

**Error**: KMZ file is very large or Google Earth is slow

**Solution**:
- The export function automatically samples large grids
- For very large datasets, consider:
  - Reducing grid resolution
  - Exporting individual flight levels
  - Using GroundOverlay instead of polygons

#### 4. Visualization Not Displaying

**Error**: Plot window doesn't appear

**Solution**:
- Ensure matplotlib backend is properly configured
- Try: `matplotlib.use('TkAgg')` before importing pyplot
- On Linux, may need: `sudo apt-get install python3-tk`

#### 5. Import Errors

**Error**: `ModuleNotFoundError`

**Solution**:
- Install missing packages: `pip install <package_name>`
- Verify Python environment
- Check PYTHONPATH settings

### Performance Tips

1. **Large Grids**: For grids > 1000x1000, computation can take hours. Consider:
   - Using a subset of the grid for testing
   - Reducing `n_samples` parameter (trades accuracy for speed)
   - Implementing parallel processing (future enhancement)

2. **Progress Monitoring**: Install `tqdm` for progress bars:
   ```bash
   pip install tqdm
   ```

3. **Testing**: Always test with a small grid subset first (e.g., 100x100)

---

## Technical Specifications

### Algorithm Details

**Line-of-Sight Calculation:**
- Samples the path between radar and target at regular intervals
- Default: 400 samples per path
- Checks terrain elevation at each sample point
- Returns `True` if all points are clear (terrain below line)

**Coverage Map Generation:**
- Iterates over all grid points in terrain data
- For each point, computes LOS at specified flight level altitude
- Stores boolean result (visible/blocked)

**Flight Level to Altitude Conversion:**
- Formula: `altitude_m = FL × 100 × 0.3048`
- FL5 = 1,524 m, FL10 = 3,048 m, ..., FL400 = 12,192 m

### Coordinate Systems

- **Input**: WGS84 (latitude/longitude in decimal degrees)
- **Elevation**: Meters above sea level (MSL)
- **Output**: Same coordinate system maintained in KML export

### Units

- **Distances**: Meters
- **Angles**: Degrees (decimal)
- **Elevations**: Meters above sea level (MSL)
- **Heights**: Meters above ground level (AGL)

### Performance Characteristics

**Computation Time** (approximate):
- Small grid (100×100): ~1-2 minutes per flight level
- Medium grid (500×500): ~10-20 minutes per flight level
- Large grid (1000×1000): ~1-2 hours per flight level
- Very large grid (2000×2000): ~4-8 hours per flight level

**Memory Usage**:
- Coverage maps: ~2 bytes per grid point (boolean)
- For 2000×2000 grid: ~8 MB per flight level
- All 8 flight levels: ~64 MB total

### Limitations

1. **Optical LOS Only**: Current implementation considers only geometric line-of-sight. RF propagation effects (refraction, diffraction) are not included.

2. **Binary Coverage**: Coverage is binary (visible/blocked). Signal strength or quality metrics are not computed.

3. **Single Radar**: Analysis is for a single radar position. Multi-radar fusion is not supported.

4. **Static Terrain**: Terrain is assumed static. Dynamic obstacles or future construction are not considered.

### Future Enhancements

Potential future additions:
- RF propagation models (beyond optical LOS)
- Signal strength calculations
- Multi-radar fusion
- 3D visualization
- Parallel processing support
- Advanced obstacle modeling

---

## Contact and Support

For questions, issues, or feature requests related to this tool, please refer to the project documentation or contact the development team.

---

**Version**: 1.0  
**Last Updated**: 2024  
**Compliance**: DRAC Tender Requirements for RF Coverage Analysis Tool
