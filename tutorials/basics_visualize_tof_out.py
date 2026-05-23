"""
visualize_tof.py  –  cortopy / standalone script
==================================================
Standalone visualisation function for ToF depth + intensity images
produced by corto.ToF.process_one().

Can be used as:
    - an imported function:
          from visualize_tof import visualize_tof
    - a command-line script:
          python visualize_tof.py path/to/000000_depth.npy
          python visualize_tof.py path/to/000000_depth.npy path/to/000000_intensity.npy

Output layout
-------------
A 2x2 figure:
    Top-left    : depth image (colourmap, NaN = black)
    Top-right   : intensity image (grayscale, NaN = black)
    Bottom-left : depth histogram (valid pixels only)
    Bottom-right: depth image with intensity as alpha overlay

Dependencies: numpy, matplotlib
"""

from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def visualize_tof(
    depth_path:     np.ndarray | str,
    intensity_path: np.ndarray | str | None = None,
    depth_cmap:     str   = "plasma",
    title:          str   = "ToF Camera Output",
    max_range:      float | None = None,
    save_path:      str | None   = None,
    show:           bool  = True,
) -> plt.Figure:
    """Visualise a corto ToF depth + intensity image pair.

    Args:
        depth_path (np.ndarray | str): float32 (H, W) depth array (m),
            NaN = invalid pixel, or path to a .npy file.
        intensity_path (np.ndarray | str | None): float32 (H, W) intensity
            array [0,1], NaN = invalid pixel, or path to a .npy file.
            If None, only depth panels are shown.
        depth_cmap (str): matplotlib colourmap for the depth image.
            Good choices: "plasma", "viridis", "turbo", "jet".
        title (str): overall figure title.
        max_range (float | None): clip depth display at this value (m).
            If None, uses the data maximum.
        save_path (str | None): if given, save the figure here.
        show (bool): call plt.show() at the end.

    Returns:
        matplotlib Figure object.
    """
    # ── Load arrays ───────────────────────────────────────────────────
    if isinstance(depth_path, str):
        depth = np.load(depth_path)
    else:
        depth = np.asarray(depth_path, dtype=np.float32)

    has_intensity = intensity_path is not None
    if has_intensity:
        if isinstance(intensity_path, str):
            intensity = np.load(intensity_path)
        else:
            intensity = np.asarray(intensity_path, dtype=np.float32)
    else:
        intensity = None

    H, W = depth.shape
    valid = ~np.isnan(depth)
    n_valid = valid.sum()

    vmax = max_range if max_range is not None else (
        float(depth[valid].max()) if n_valid > 0 else 1.0
    )
    vmin = float(depth[valid].min()) if n_valid > 0 else 0.0

    # ── Colour-mapped depth (NaN -> black) ────────────────────────────
    cmap_d = plt.colormaps[depth_cmap].copy()
    cmap_d.set_bad(color="black")

    # ── Figure layout ─────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(13, 9),
                             gridspec_kw={"hspace": 0.35, "wspace": 0.3})
    fig.suptitle(
        f"{title}  –  {H}x{W} px  |  {n_valid:,}/{H*W:,} valid pixels",
        fontsize=13, fontweight="bold", y=0.98
    )

    ax_depth, ax_inten, ax_hist, ax_overlay = axes.flat

    # ── Panel 1: depth image ─────────────────────────────────────────
    im_d = ax_depth.imshow(
        depth, cmap=cmap_d, vmin=vmin, vmax=vmax,
        interpolation="nearest", aspect="equal"
    )
    fig.colorbar(im_d, ax=ax_depth, fraction=0.046, pad=0.04,
                 label="Range (m)")
    ax_depth.set_title("Depth image", fontsize=11)
    ax_depth.axis("off")

    # ── Panel 2: intensity image ──────────────────────────────────────
    if has_intensity:
        cmap_i = plt.colormaps["gray"].copy()
        cmap_i.set_bad(color="black")
        im_i = ax_inten.imshow(
            intensity, cmap=cmap_i, vmin=0.0, vmax=1.0,
            interpolation="nearest", aspect="equal"
        )
        fig.colorbar(im_i, ax=ax_inten, fraction=0.046, pad=0.04,
                     label="Intensity [0-1]")
        ax_inten.set_title("Intensity image", fontsize=11)
        ax_inten.axis("off")
    else:
        ax_inten.set_visible(False)

    # ── Panel 3: depth histogram ──────────────────────────────────────
    if n_valid > 0:
        ax_hist.hist(
            depth[valid].ravel(), bins=80,
            color=plt.colormaps[depth_cmap](0.6), edgecolor="none", alpha=0.85
        )
        ax_hist.set_xlabel("Range (m)", fontsize=10)
        ax_hist.set_ylabel("Pixel count", fontsize=10)
        ax_hist.set_title("Depth histogram (valid pixels)", fontsize=11)
        ax_hist.axvline(float(depth[valid].mean()), color="white",
                        linestyle="--", linewidth=1.2, label="mean")
        ax_hist.legend(fontsize=9)
        ax_hist.set_facecolor("#1a1a2e")
        fig.patch.set_facecolor("white")
    else:
        ax_hist.text(0.5, 0.5, "No valid pixels", ha="center", va="center",
                     transform=ax_hist.transAxes, fontsize=12, color="gray")
        ax_hist.set_title("Depth histogram", fontsize=11)

    # ── Panel 4: depth image with intensity alpha overlay ─────────────
    if has_intensity and n_valid > 0:
        # Normalise depth to [0,1] for colour mapping
        norm_d  = mcolors.Normalize(vmin=vmin, vmax=vmax)
        rgb_d   = plt.colormaps[depth_cmap](norm_d(depth))[:, :, :3]   # (H,W,3)

        # Use intensity as alpha; NaN pixels -> fully transparent
        inten_clean = np.where(np.isnan(intensity), 0.0, intensity)
        alpha       = np.where(valid, inten_clean, 0.0)

        rgba = np.dstack([rgb_d, alpha]).astype(np.float32)

        # Black background
        bg = np.zeros((H, W, 3), dtype=np.float32)
        ax_overlay.imshow(bg, aspect="equal")
        ax_overlay.imshow(rgba, interpolation="nearest", aspect="equal")
        ax_overlay.set_title("Depth coloured by intensity (alpha)", fontsize=11)
    else:
        ax_overlay.set_visible(False)

    ax_overlay.axis("off")

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"[visualize_tof] Saved -> {save_path}")

    if show:
        plt.show()

    return fig

## MAIN 

depth_p   = "output/S10_Spacecraft/tof/images/000000_depth.npy"
inten_p   = "output/S10_Spacecraft/tof/images/000000_intensity.npy"
visualize_tof(depth_p, inten_p)
