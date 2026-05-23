"""
basics_Visualize_geometry.py
============================
Reads a corto geometry JSON file and visualises all body/camera orientations
in 3-D, showing:
  - Camera and body positions as coloured markers
  - Camera orientation as a triad of axes (X/Y/Z in red/green/blue)
  - Body orientation as a triad of axes
  - The camera boresight ray pointed toward the body
  - Sun direction vectors (normalised, shown from the body)

Quaternion convention: W, X, Y, Z  (same as the generator script)

Usage
-----
Run directly:
    python basics_Visualize_geometry.py

Or point it at any geometry file:
    json_path = "path/to/geometry.json"
    show_every = 5        # draw a triad every N poses to avoid clutter
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D          # noqa: F401

# ==============================
# USER INPUT
# ==============================

json_path  = "geometry_generated.json"   # path to the geometry JSON
show_every = 5                           # draw orientation triads every N poses
triad_scale = 5.0                        # length of axis arrows (in scene units)

# ==============================
# HELPERS
# ==============================

def quat_to_rotation_matrix(q):
    """Return 3x3 rotation matrix from quaternion [W, X, Y, Z]."""
    w, x, y, z = q / np.linalg.norm(q)
    return np.array([
        [1 - 2*(y*y + z*z),     2*(x*y - z*w),     2*(x*z + y*w)],
        [    2*(x*y + z*w), 1 - 2*(x*x + z*z),     2*(y*z - x*w)],
        [    2*(x*z - y*w),     2*(y*z + x*w), 1 - 2*(x*x + y*y)],
    ])


def draw_triad(ax, origin, R, scale, alpha=0.8):
    """Draw X/Y/Z axes of a frame at *origin* rotated by *R*."""
    colors = ("red", "green", "blue")
    for i, color in enumerate(colors):
        direction = R[:, i] * scale
        ax.quiver(
            origin[0], origin[1], origin[2],
            direction[0], direction[1], direction[2],
            color=color, linewidth=1.2, alpha=alpha,
            arrow_length_ratio=0.15,
        )


def draw_ray(ax, start, end, color, label=None, alpha=0.5):
    """Draw a line from *start* to *end*."""
    ax.plot(
        [start[0], end[0]],
        [start[1], end[1]],
        [start[2], end[2]],
        color=color, linewidth=0.8, alpha=alpha,
        label=label,
    )


def set_equal_axes(ax, all_points):
    """Force equal aspect ratio on a 3-D axis."""
    pts = np.array(all_points)
    max_range = np.ptp(pts, axis=0).max() / 2.0
    mid = pts.mean(axis=0)
    for setter, m in zip(
        [ax.set_xlim, ax.set_ylim, ax.set_zlim], mid
    ):
        setter(m - max_range, m + max_range)


# ==============================
# LOAD DATA
# ==============================

with open(json_path) as f:
    geom = json.load(f)

cam_pos   = np.array(geom["camera"]["position"])    # (N, 3)
cam_quat  = np.array(geom["camera"]["orientation"]) # (N, 4)  W X Y Z
body_pos  = np.array(geom["body"]["position"])      # (N, 3)
body_quat = np.array(geom["body"]["orientation"])   # (N, 4)
sun_pos   = np.array(geom["sun"]["position"])       # (N, 3)

N = len(cam_pos)
print(f"Loaded {N} poses from '{json_path}'")

# ==============================
# FIGURE 1 – 3-D scene overview
# ==============================

fig = plt.figure(figsize=(13, 9))
ax  = fig.add_subplot(111, projection="3d")

all_pts = []   # collect every plotted point for axis scaling

# Sun directions: draw a short unit vector from the body toward the sun
for i in range(0, N, show_every):
    sun_dir = sun_pos[i] - body_pos[i]
    sun_dir = sun_dir / np.linalg.norm(sun_dir) * triad_scale * 3
    draw_ray(
        ax,
        body_pos[i],
        body_pos[i] + sun_dir,
        color="gold",
        label="Sun dir" if i == 0 else None,
        alpha=0.4,
    )

# Camera-to-body boresight ray
for i in range(0, N, show_every):
    draw_ray(
        ax,
        cam_pos[i],
        body_pos[i],
        color="cyan",
        label="Boresight" if i == 0 else None,
        alpha=0.3,
    )

# Body orientation triads
for i in range(0, N, show_every):
    R = quat_to_rotation_matrix(body_quat[i])
    draw_triad(ax, body_pos[i], R, scale=triad_scale * 0.6, alpha=0.6)
    all_pts.append(body_pos[i])

# Camera orientation triads + positions
for i in range(0, N, show_every):
    R = quat_to_rotation_matrix(cam_quat[i])
    draw_triad(ax, cam_pos[i], R, scale=triad_scale, alpha=0.9)
    all_pts.append(cam_pos[i])

# Camera trajectory scatter
sc_cam = ax.scatter(
    cam_pos[:, 0], cam_pos[:, 1], cam_pos[:, 2],
    c=np.arange(N), cmap="viridis", s=18, zorder=5, label="Camera",
)
# Body positions
ax.scatter(
    body_pos[:, 0], body_pos[:, 1], body_pos[:, 2],
    c="orange", s=40, marker="*", zorder=6, label="Body",
)

# Colourbar for pose index
cbar = fig.colorbar(sc_cam, ax=ax, pad=0.08, shrink=0.55)
cbar.set_label("Pose index", fontsize=9)

# Axis triad legend patches (manual legend entries)
from matplotlib.lines import Line2D
legend_handles = [
    Line2D([0], [0], color="red",    lw=2, label="X axis"),
    Line2D([0], [0], color="green",  lw=2, label="Y axis"),
    Line2D([0], [0], color="blue",   lw=2, label="Z axis"),
    Line2D([0], [0], color="cyan",   lw=1, alpha=0.6, label="Boresight"),
    Line2D([0], [0], color="gold",   lw=1, alpha=0.6, label="Sun dir"),
    Line2D([0], [0], color="none",   marker="o",  markerfacecolor="cyan",    markersize=6, label="Camera"),
    Line2D([0], [0], color="none",   marker="*",  markerfacecolor="orange",  markersize=9, label="Body"),
]
ax.legend(handles=legend_handles, loc="upper left", fontsize=8, framealpha=0.7)

ax.set_xlabel("X [BU]")
ax.set_ylabel("Y [BU]")
ax.set_zlabel("Z [BU]")
ax.set_title(f"Geometry overview — {N} poses  (triads every {show_every})", pad=12)

set_equal_axes(ax, all_pts if all_pts else np.vstack([cam_pos, body_pos]))

plt.tight_layout()

# ==============================
# FIGURE 2 – per-pose angles
# ==============================

# Phase angle: angle between (sun - body) and (camera - body) vectors
# Boresight angle: angle between camera Z-axis and (body - camera) direction
# (how well the camera is pointing at the body)

phase_angles    = np.zeros(N)
boresight_error = np.zeros(N)

for i in range(N):
    # Phase angle
    v_cam = cam_pos[i] - body_pos[i]
    v_sun = sun_pos[i] - body_pos[i]
    cos_p = np.dot(v_cam, v_sun) / (np.linalg.norm(v_cam) * np.linalg.norm(v_sun))
    phase_angles[i] = np.degrees(np.arccos(np.clip(cos_p, -1, 1)))

    # Boresight error: angle between camera -Z axis and vector toward body
    R = quat_to_rotation_matrix(cam_quat[i])
    cam_z    = R[:, 2]                          # camera Z (boresight) in world frame
    to_body  = body_pos[i] - cam_pos[i]
    to_body /= np.linalg.norm(to_body)
    cos_b    = np.dot(cam_z, to_body)
    boresight_error[i] = np.degrees(np.arccos(np.clip(cos_b, -1, 1)))

fig2, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

axes[0].plot(phase_angles, color="steelblue", linewidth=1.5)
axes[0].set_ylabel("Phase angle [deg]")
axes[0].set_title("Phase angle (sun–body–camera)")
axes[0].grid(True, alpha=0.3)

axes[1].plot(boresight_error, color="darkorange", linewidth=1.5)
axes[1].set_ylabel("Boresight error [deg]")
axes[1].set_xlabel("Pose index")
axes[1].set_title("Camera boresight error (angle between camera +Z and body direction)")
axes[1].grid(True, alpha=0.3)

plt.suptitle(f"Per-pose orientation metrics — {N} poses", fontsize=12)
plt.tight_layout()

# ==============================
# FIGURE 3 – orientation summary table
# ==============================

print("\n--- Orientation summary (first 10 poses) ---")
print(f"{'Pose':>5}  {'Cam quat (W,X,Y,Z)':>35}  {'Body quat (W,X,Y,Z)':>35}  {'Phase [deg]':>11}  {'Boresight err [deg]':>19}")
for i in range(min(10, N)):
    cq = cam_quat[i]
    bq = body_quat[i]
    print(
        f"{i:>5}  "
        f"[{cq[0]:6.3f},{cq[1]:6.3f},{cq[2]:6.3f},{cq[3]:6.3f}]  "
        f"[{bq[0]:6.3f},{bq[1]:6.3f},{bq[2]:6.3f},{bq[3]:6.3f}]  "
        f"{phase_angles[i]:>11.2f}  "
        f"{boresight_error[i]:>19.2f}"
    )

plt.show()
