"""
visualize_lidar.py  –  cortopy / standalone script
====================================================
Standalone visualisation function for LiDAR point clouds produced by
corto.LiDAR.process_one().

Can be used as:
    - an imported function:   from visualize_lidar import visualize_lidar
    - a command-line script:  python visualize_lidar.py path/to/000000.npy

Colouring modes
---------------
    "ring"       : one colour per vertical channel (ring_id)
    "intensity"  : grayscale mapped to return intensity
    "depth"      : colour mapped to slant range (z distance)
    "timestamp"  : colour mapped to horizontal scan angle proxy

Dependencies: numpy, matplotlib
"""

from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D          # noqa: F401  (registers 3D projection)
from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize


def visualize_lidar(
    pc:         np.ndarray | str,
    color_by:   str   = "ring",
    point_size: float = 2.0,
    azimuth:    float = -60.0,
    elevation:  float = 25.0,
    title:      str   = "LiDAR Point Cloud",
    save_path:  str | None = None,
    show:       bool  = True,
) -> plt.Figure:
    """Visualise a corto LiDAR point cloud in 3-D.

    Args:
        pc (np.ndarray | str): structured numpy array with fields
            (x, y, z, intensity, ring_id, timestamp_s), or a path to a
            .npy file containing such an array.
        color_by (str): colouring mode – one of
            "ring", "intensity", "depth", "timestamp".
        point_size (float): scatter point size.
        azimuth (float): initial horizontal view angle (degrees).
        elevation (float): initial vertical view angle (degrees).
        title (str): figure title.
        save_path (str | None): if given, save the figure to this path.
        show (bool): call plt.show() at the end.

    Returns:
        matplotlib Figure object.
    """
    # ── Load if path given ────────────────────────────────────────────
    if isinstance(pc, (str,)):
        pc = np.load(pc)

    if len(pc) == 0:
        print("[visualize_lidar] Point cloud is empty – nothing to display.")
        fig = plt.figure(figsize=(8, 6))
        ax  = fig.add_subplot(111, projection="3d")
        ax.set_title(f"{title}  (empty)")
        if show:
            plt.show()
        return fig

    x = pc["x"].astype(float)
    y = pc["y"].astype(float)
    z = pc["z"].astype(float)

    # ── Colour mapping ────────────────────────────────────────────────
    cmap_name = {
        "ring":      "tab20",
        "intensity": "gray",
        "depth":     "plasma",
        "timestamp": "hsv",
    }.get(color_by, "tab20")

    if color_by == "ring":
        raw    = pc["ring_id"].astype(float)
        label  = "Ring ID"
    elif color_by == "intensity":
        raw    = pc["intensity"].astype(float)
        label  = "Intensity"
    elif color_by == "depth":
        raw    = np.sqrt(x**2 + y**2 + z**2)
        label  = "Range (m)"
    else:  # timestamp
        raw    = pc["timestamp_s"].astype(float)
        label  = "Timestamp (s)"

    norm   = Normalize(vmin=raw.min(), vmax=raw.max())
    cmap   = get_cmap(cmap_name)
    colors = cmap(norm(raw))

    # ── Figure ────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(11, 8))
    ax  = fig.add_subplot(111, projection="3d")

    sc = ax.scatter(x, y, z, c=colors, s=point_size, linewidths=0, alpha=0.85)

    # Colourbar (use a ScalarMappable so colorbar works with scatter colours)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, pad=0.1, shrink=0.6)
    cbar.set_label(label, fontsize=10)

    # ── Axes labels and style ─────────────────────────────────────────
    ax.set_xlabel("X (m)", fontsize=9)
    ax.set_ylabel("Y (m)", fontsize=9)
    ax.set_zlabel("Z (m)", fontsize=9)
    ax.set_title(f"{title}\n{len(pc):,} points  |  colour: {color_by}",
                 fontsize=11, pad=12)
    ax.view_init(elev=elevation, azim=azimuth)

    # Equal-ish aspect ratio
    max_range = max(x.max()-x.min(), y.max()-y.min(), z.max()-z.min()) / 2.0
    mid_x, mid_y, mid_z = x.mean(), y.mean(), z.mean()
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"[visualize_lidar] Saved → {save_path}")

    if show:
        plt.show()

    return fig

## MAIN 

path = "output/S10_Spacecraft/lidar/pointclouds/000000.npy"
visualize_lidar(path, color_by="ring")
