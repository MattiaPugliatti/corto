"""
Visualize a depth map saved as an .exr file.

Requirements:
    pip install openexr numpy matplotlib
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import OpenEXR
import Imath

def visualize_exr(path: str, sentinel: float = 1e9, cmap: str = "inferno"):
    exr = OpenEXR.InputFile(path)
    header = exr.header()

    dw = header["dataWindow"]
    h = dw.max.y - dw.min.y + 1
    w = dw.max.x - dw.min.x + 1

    channels = list(header["channels"].keys())
    print(f"Channels found: {channels}")

    pt = Imath.PixelType(Imath.PixelType.FLOAT)

    # --- 3-channel: slope map ---
    if len(channels) == 3:
        rgb = np.stack([
            np.frombuffer(exr.channel(c, pt), dtype=np.float32).reshape(h, w)
            for c in channels
        ], axis=-1)

        # Normalize to [0, 1] for display
        rgb_display = np.clip(rgb / (rgb.max() + 1e-8), 0, 1)

        fig, ax = plt.subplots(figsize=(7, 7))
        ax.imshow(rgb_display, origin="upper")  # no cmap — matplotlib infers RGB from shape (H, W, 3)
        # ax.set_title(f"RGB Image [{sys.path}]")
        ax.axis("off")

    # --- 1-channel: depth map ---
    else:
        channel_name = "Z" if "Z" in channels else channels[0]
        print(f"Reading depth channel: '{channel_name}'")
        depth = np.frombuffer(exr.channel(channel_name, pt), dtype=np.float32).reshape(h, w)

        invalid_mask = (depth == 0) | np.isinf(depth) | np.isnan(depth) | (depth >= sentinel)
        masked_depth = np.ma.masked_where(invalid_mask, depth)

        dmin, dmax = float(masked_depth.min()), float(masked_depth.max())
        
        print(f"Depth range: {dmin:.4f} — {dmax:.4f}")

        fig, ax = plt.subplots(figsize=(7, 7))
        im = ax.imshow(masked_depth, vmin=dmin, vmax=dmax, cmap=cmap, origin="upper")
        # fig.colorbar(im, ax=ax, label="Depth [m]")
        # ax.set_title(f"Depth Map  [{path}]")
        ax.axis("off")

    plt.tight_layout()
    plt.show()
    return fig

# visualize_exr("output/S10_Spacecraft/slopes_exr/000000.exr")
# visualize_exr("output/S10_Spacecraft/depth_exr/000000.exr", cmap = 'inferno')
# visualize_exr("_IMAGES_PROPOSAL/obj_ID.exr", cmap = 'inferno')
visualize_exr("output/S10_Spacecraft/obj_ID/000000.exr", cmap = 'plasma')
