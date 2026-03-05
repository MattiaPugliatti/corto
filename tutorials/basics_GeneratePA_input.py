"""
This script generates a simple geometry file with fixed camera and body positions and orietnations, and varying sun positions producing different, regular, phase angles.

"""

import numpy as np
import json

# ==============================
# USER INPUT
# ==============================

N = 60  # number of poses
min_phase_deg = 0
max_phase_deg = 180

camera_position = np.array([100.0, 0.0, 0.0]) # in [BU]
camera_quat = np.array([0.5, 0.5, 0.5, 0.5]) # W, X, Y, Z

body_position = np.array([0.0, 0.0, 0.0]) # W, X, Y, Z
body_quat = np.array([1.0, 0.0, 0.0, 0.0]) # in [BU]

json_name = "geometry_generated.json" # name of the geometry output file

# ==============================
# SUN SAMPLING
# ==============================

sun_distance = np.linalg.norm(camera_position) * 1e3

def generate_sun_positions(N, cam_pos, body_pos):
    """
    Generate sun positions producing varying phase angles.
    Phase angle defined between camera-body vector
    and sun-body vector.
    """
    view_vec = cam_pos - body_pos
    view_vec = view_vec / np.linalg.norm(view_vec)
    # Build orthonormal basis around view vector
    tmp = np.array([0, 0, 1])
    if abs(np.dot(tmp, view_vec)) > 0.9:
        tmp = np.array([0, 1, 0])
    u = np.cross(view_vec, tmp)
    u /= np.linalg.norm(u)
    v = np.cross(view_vec, u)
    phases = np.linspace(
        np.deg2rad(min_phase_deg),
        np.deg2rad(max_phase_deg),
        N
    )
    sun_positions = []
    for ang in phases:
        direction = (
            np.cos(ang) * view_vec +
            np.sin(ang) * u
        )
        sun_pos = body_pos + direction * sun_distance
        sun_positions.append(sun_pos)
    return np.array(sun_positions)


# ==============================
# BUILD ARRAYS
# ==============================

sun_pos_all = generate_sun_positions(N, camera_position, body_position)

cam_pos_all = np.tile(camera_position, (N, 1))
cam_orientation_all = np.tile(camera_quat, (N, 1))

body_pos_all = np.tile(body_position, (N, 1))
body_orientation_all = np.tile(body_quat, (N, 1))


# ==============================
# GEOM DICTIONARY
# ==============================

GEOM = {
    "sun": {
        "position": sun_pos_all.tolist()
    },
    "camera": {
        "position": cam_pos_all.tolist(),
        "orientation": cam_orientation_all.tolist(),
    },
    "body": {
        "position": body_pos_all.tolist(),
        "orientation": body_orientation_all.tolist(),
    },
}


# ==============================
# JSON save
# ==============================

with open(json_name, "w") as f:
    json.dump(GEOM, f, indent=2)

print("Generated", N, "poses.")