import ctypes
import os
import requests
from datetime import datetime

# -----------------------------
# Paths (relative to script)
# -----------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

PICTURES_DIR = os.path.join(SCRIPT_DIR, "Pictures")
LOG_PATH = os.path.join(SCRIPT_DIR, "apod.log")

os.makedirs(PICTURES_DIR, exist_ok=True)

# -----------------------------
# Logging helper
# -----------------------------
def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# -----------------------------
# Configuration
# -----------------------------
# TODO: ENTER YOUR OWN API KEY GENERATED FROM https://api.nasa.gov/
NASA_API_KEY = "YOUR_API_KEY_HERE"
APOD_API_URL = "https://api.nasa.gov/planetary/apod"

today = datetime.now().strftime("%Y-%m-%d")
IMAGE_PATH = os.path.join(PICTURES_DIR, f"apod_{today}.jpg")

# -----------------------------
# Call NASA APOD API
# -----------------------------
log("Calling NASA APOD API...")

try:
    response = requests.get(
        APOD_API_URL,
        params={"api_key": NASA_API_KEY},
        timeout=15
    )
    response.raise_for_status()
    data = response.json()
except Exception as e:
    log(f"ERROR: Failed to fetch APOD data: {e}")
    exit(1)

# -----------------------------
# Skip videos
# -----------------------------
if data.get("media_type") != "image":
    log("APOD is not an image today (video or other media). Skipping update.")
    exit(0)

image_url = data.get("hdurl") or data.get("url")
log(f"Downloading image from: {image_url}")

# -----------------------------
# Download image
# -----------------------------
try:
    img = requests.get(image_url, timeout=10)
    img.raise_for_status()
    with open(IMAGE_PATH, "wb") as f:
        f.write(img.content)
except Exception as e:
    log(f"ERROR: Failed to download image: {e}")
    exit(1)

log(f"Image saved to: {IMAGE_PATH}")

# -----------------------------
# Set wallpaper (Windows)
# -----------------------------
SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

result = ctypes.windll.user32.SystemParametersInfoW(
    SPI_SETDESKWALLPAPER,
    0,
    IMAGE_PATH,
    SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
)

if result:
    log("Wallpaper updated successfully.")
else:
    log("ERROR: Failed to set wallpaper.")

log("Script finished.")
exit(0)
