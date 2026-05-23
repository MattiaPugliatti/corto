import os
import numpy as np
import imageio.v3 as iio
import matplotlib.pyplot as plt

# ==============================
# CONFIG
# ==============================
BASE = os.getcwd()

CALIB_DATA = {
    "Lambertian": os.path.join(BASE, "input/SphereCalib/S00_Calibration_Lambertian/img"),
    "McEwen": os.path.join(BASE, "input/SphereCalib/S00_Calibration_McEwen/img"),
    "Akimov": os.path.join(BASE, "input/SphereCalib/S00_Calibration_Akimov/img"),
    "LommelSeeliger": os.path.join(BASE, "input/SphereCalib/S00_Calibration_LommelSeeliger/img"),
    "Minnaert": os.path.join(BASE, "input/SphereCalib/S00_Calibration_Minnaert/img"),
    "ROLO": os.path.join(BASE, "input/SphereCalib/S00_Calibration_ROLO/img"),
    "SimplifiedHapke": os.path.join(BASE, "input/SphereCalib/S00_Calibration_SimplifiedHapke/img"),
    "Hapke": os.path.join(BASE, "input/SphereCalib/S00_Calibration_Hapke/img"),
}

N_EXPECTED = 60
phase_angles = np.linspace(0, 180, N_EXPECTED) # Expected phase angles for the rendered images (check the scenario settings)

# ==============================
# FUN DEFS
# ==============================

def load_images(folder):
    files = sorted([
        f for f in os.listdir(folder)
        if f.endswith(".png")
    ])
    if len(files) == 0:
        raise RuntimeError("No images found")
    images = []
    for f in files:
        img = iio.imread(os.path.join(folder, f)).astype(np.float32)
        # Normalize if 8-bit
        if img.max() > 1.5:
            img /= 255.0
        # Convert to grayscale radiance
        if img.ndim == 3:
            img = 0.2126*img[:,:,0] + 0.7152*img[:,:,1] + 0.0722*img[:,:,2]
        images.append(img)
    images = np.array(images)
    print("Loaded images:", images.shape)
    return images

def radial_profile(img, mask):
    h, w = img.shape
    y, x = np.indices((h, w))
    cx = np.mean(x[mask])
    cy = np.mean(y[mask])
    r = np.sqrt((x-cx)**2 + (y-cy)**2)
    r = r[mask]
    vals = img[mask]
    bins = np.linspace(0, r.max(), 50)
    digit = np.digitize(r, bins)
    profile = [
        vals[digit == i].mean()
        if np.any(digit == i) else 0
        for i in range(1, len(bins))
    ]
    return np.array(profile)

def collect_metrics(images):
    # Generate mask of the sphere based on the first image (assuming the sphere is the brightest object)
    reference = images[0]
    thr = np.percentile(reference, 20)
    mask = reference > thr
    # Collect metrics for each image
    means = []
    peaks = []
    fluxes = []
    bright_means = []
    for img in images:
        sphere_pixels = img[mask]
        means.append(np.mean(sphere_pixels))
        peaks.append(np.max(sphere_pixels))
        fluxes.append(np.sum(sphere_pixels))
        # Bright hemisphere approx
        bright = sphere_pixels[sphere_pixels > np.mean(sphere_pixels)]
        bright_means.append(np.mean(bright))
    means = np.array(means)
    peaks = np.array(peaks)
    fluxes = np.array(fluxes)
    fluxes_ad = fluxes / np.max(fluxes)
    bright_means = np.array(bright_means)
    profile = radial_profile(images[len(images)//2], mask)
    return means, peaks, fluxes_ad, bright_means, profile

# ==============================
# LOOP to collect metrics
# ==============================

RESULTS = {}

for model, folder in CALIB_DATA.items():
    print(f"Processing {model}")
    print("Path:", folder)

    images = load_images(folder)

    means, peaks, fluxes_ad, bright_means, profile = collect_metrics(images)

    RESULTS[model] = {
        "means": means,
        "peaks": peaks,
        "flux": fluxes_ad,
        "bright": bright_means,
        "profile": profile
    }

# ==============================
# PLOTS
# ==============================

plt.figure()
plt.subplot(3,1,1)
for model, data in RESULTS.items():
    plt.plot(phase_angles[0:-1], data["means"][0:-1], label=model)
plt.grid('minor')
plt.legend()
plt.title("Mean Radiance over Phase Angle")
plt.subplot(3,1,2) 
for model, data in RESULTS.items():
    plt.semilogy(phase_angles[0:-1], data["peaks"][0:-1], label=model)
plt.grid('minor')
plt.legend()
plt.title("Peak Radiance over Phase Angle")
plt.subplot(3,1,3)
for model, data in RESULTS.items():
    plt.plot(phase_angles[0:-1], data["flux"][0:-1], label=model)
plt.grid('minor')
plt.legend()
plt.title("Normalized Flux over Phase Angle")
plt.xlabel("Phase Angle [deg]")
plt.tight_layout()


plt.figure()
for model, data in RESULTS.items():
    plt.semilogy(phase_angles[0:-1], data["flux"][0:-1], label=model)
plt.grid('minor')
plt.legend()
plt.title("Normalized Flux over Phase Angle")
plt.xlabel("Phase Angle [deg]")
plt.tight_layout()

plt.show()
