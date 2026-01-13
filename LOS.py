import numpy as np


# =========================
# 1) LOAD TERRAIN (NPZ)
# =========================
def load_terrain_npz(npz_path: str):
    """
    Charge terrain + lat/lon depuis terrain_mat.npz

    Le fichier contient:
    - d["ter"] : matrice terrain (N,M) en mètres (MSL)
    - d["lat"] : latitudes (N,)
    - d["lon"] : longitudes (M,)
    """
    d = np.load(npz_path)
    lats = d["lat"].astype(float)
    lons = d["lon"].astype(float)
    Z = d["ter"].astype(float)

    if Z.shape != (len(lats), len(lons)):
        raise ValueError(f"Incohérence: Z{Z.shape} vs ({len(lats)}, {len(lons)})")

    return lats, lons, Z


# =========================
# 2) TERRAIN INTERPOLATION
# =========================
def z_terrain(lat: float, lon: float,
              lats: np.ndarray, lons: np.ndarray, Z: np.ndarray):
    """
    Altitude terrain (m) au point (lat, lon) via interpolation bilinéaire.
    Retourne None si hors zone ou si no-data (valeurs < 0).
    """

    # axes croissants ou décroissants
    lats_inc = lats[0] < lats[-1]
    lons_inc = lons[0] < lons[-1]

    lat_min, lat_max = (lats[0], lats[-1]) if lats_inc else (lats[-1], lats[0])
    lon_min, lon_max = (lons[0], lons[-1]) if lons_inc else (lons[-1], lons[0])

    if not (lat_min <= lat <= lat_max and lon_min <= lon <= lon_max):
        return None

    # rendre croissant pour searchsorted
    lats_s = lats if lats_inc else lats[::-1]
    lons_s = lons if lons_inc else lons[::-1]

    # réordonner Z
    if lats_inc and lons_inc:
        Z_s = Z
    elif (not lats_inc) and lons_inc:
        Z_s = Z[::-1, :]
    elif lats_inc and (not lons_inc):
        Z_s = Z[:, ::-1]
    else:
        Z_s = Z[::-1, ::-1]

    i1 = int(np.searchsorted(lats_s, lat))
    j1 = int(np.searchsorted(lons_s, lon))
    i1 = int(np.clip(i1, 1, len(lats_s) - 1))
    j1 = int(np.clip(j1, 1, len(lons_s) - 1))
    i0, j0 = i1 - 1, j1 - 1

    lat0, lat1 = lats_s[i0], lats_s[i1]
    lon0, lon1 = lons_s[j0], lons_s[j1]

    z00 = Z_s[i0, j0]
    z01 = Z_s[i0, j1]
    z10 = Z_s[i1, j0]
    z11 = Z_s[i1, j1]

    # no-data: valeurs négatives (dans ton npz, on en a)
    if min(z00, z01, z10, z11) < 0:
        return None

    t = (lat - lat0) / (lat1 - lat0 + 1e-12)
    u = (lon - lon0) / (lon1 - lon0 + 1e-12)

    z0 = (1 - u) * z00 + u * z01
    z1 = (1 - u) * z10 + u * z11
    return float((1 - t) * z0 + t * z1)


# =========================
# 3) LINE ALTITUDE
# =========================
def z_ligne(s: float, z_radar_m: float, z_target_m: float) -> float:
    """Altitude (m) sur la droite radar->cible (s∈[0,1])."""
    return z_radar_m + s * (z_target_m - z_radar_m)


def fl_to_m(FL: float) -> float:
    """FLxxx = xxx*100 ft ; 1 ft = 0.3048 m."""
    return FL * 100.0 * 0.3048


# =========================
# 4) LOS FUNCTION
# =========================
def los_visible(radar_lat: float, radar_lon: float, radar_height_agl_m: float,
                target_lat: float, target_lon: float, target_alt_m_msl: float,
                lats: np.ndarray, lons: np.ndarray, Z: np.ndarray,
                n_samples: int = 400, margin_m: float = 0.0) -> bool:
    """
    True si LOS OK, False sinon.

    - radar_height_agl_m : hauteur tour au-dessus du sol (AGL)
    - target_alt_m_msl   : altitude cible en m (MSL), ex: fl_to_m(50)
    - margin_m           : marge de sécurité (0 ou 10m par ex)
    """

    z_ground_r = z_terrain(radar_lat, radar_lon, lats, lons, Z)
    if z_ground_r is None:
        return False
    z_radar = z_ground_r + radar_height_agl_m

    for k in range(1, n_samples):
        s = k / n_samples

        lat = radar_lat + s * (target_lat - radar_lat)
        lon = radar_lon + s * (target_lon - radar_lon)

        z_ground = z_terrain(lat, lon, lats, lons, Z)
        if z_ground is None:
            return False  # safe: no-data => on considère bloqué

        z_line = z_ligne(s, z_radar, target_alt_m_msl)

        if z_ground + margin_m >= z_line:
            return False

    return True


# =========================
# 5) QUICK TEST (RUN)
# =========================
# 1) charge le npz
lats, lons, Z = load_terrain_npz("terrain_mat.npz")

print("Loaded:", "lats", lats.shape, "lons", lons.shape, "Z", Z.shape)
print("Terrain min/max:", float(np.min(Z)), float(np.max(Z)))

# 2) radar au milieu (pour éviter out-of-bounds)
radar_lat = float(lats[len(lats)//2])
radar_lon = float(lons[len(lons)//2])
radar_alt = 20

# 3) cible un peu plus loin + FL50
target_lat = radar_lat + 0.1
target_lon = radar_lon + 0.05
target_alt = fl_to_m(50)

print("Radar:", radar_lat, radar_lon, "Target:", target_lat, target_lon, "Alt(m):", target_alt)

ok = los_visible(
    radar_lat, radar_lon, radar_alt,
    target_lat, target_lon, target_alt,
    lats, lons, Z,
    n_samples=400, margin_m=0.0
)

print("LOS visible ?", ok)
