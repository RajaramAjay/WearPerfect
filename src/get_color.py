import os
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.cluster import KMeans
from rembg import remove
from matplotlib import colors as mcolors
import cv2

# Load XKCD colors once
xkcd_colors = {
    name.replace("xkcd:", ""): np.array(mcolors.to_rgb(hex_code)) * 255
    for name, hex_code in mcolors.XKCD_COLORS.items()
}


def closest_xkcd_color_name(rgb):
    rgb = np.array(rgb)
    closest = min(xkcd_colors.items(), key=lambda item: np.linalg.norm(rgb - item[1]))
    return closest[0]


def extract_clothing_pixels(image_path, alpha_thresh=100, min_area=1000):
    image = Image.open(image_path).convert("RGBA")
    image = image.resize((256, 256))  # Resize for speed
    image_no_bg = remove(image)
    image_np = np.array(image_no_bg)
    alpha_channel = image_np[:, :, 3]
    mask = (alpha_channel > alpha_thresh).astype(np.uint8) * 255

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cleaned_mask = np.zeros_like(mask)
    for contour in contours:
        if cv2.contourArea(contour) >= min_area:
            cv2.drawContours(cleaned_mask, [contour], -1, 255, thickness=cv2.FILLED)

    clothing_pixels = image_np[:, :, :3][cleaned_mask > 0]
    return clothing_pixels


def get_top_two_colors(pixels, num_colors=5):
    kmeans = KMeans(n_clusters=num_colors, random_state=42)
    labels = kmeans.fit_predict(pixels)
    _, counts = np.unique(labels, return_counts=True)
    sorted_indices = np.argsort(counts)[::-1]
    top_colors = [
        kmeans.cluster_centers_[idx].astype(int) for idx in sorted_indices[:2]
    ]
    return [tuple(c) for c in top_colors]


# ✅ This is the function you can use in your FastAPI or Flask route
def get_image_colors(image_path):
    try:
        pixels = extract_clothing_pixels(image_path)
        rgb1, rgb2 = get_top_two_colors(pixels)
        hex1 = "#{:02x}{:02x}{:02x}".format(*rgb1)
        hex2 = "#{:02x}{:02x}{:02x}".format(*rgb2)
        name1 = closest_xkcd_color_name(rgb1)
        name2 = closest_xkcd_color_name(rgb2)

        return {
            # "primary_color_rgb": str(rgb1),
            # "primary_color_hex": hex1,
            "primary_color_name": name1,
            # "secondary_color_rgb": str(rgb2),
            # "secondary_color_hex": hex2,
            "secondary_color_name": name2,
        }
    except Exception as e:
        return {
            # "primary_color_rgb": "error",
            # "primary_color_hex": "#808080",
            "primary_color_name": f"Error: {e}",
            # "secondary_color_rgb": "",
            # "secondary_color_hex": "",
            "secondary_color_name": "",
        }


# Sample usage after receiving image from API upload
# result = get_image_colors(r"C:\Users\arajaram\OneDrive - Maryland Department of Transportation(MDOT)\Desktop\Capstone project\chatbot for Project\test_images\taras-chernus-iIjResyhhW0-unsplash.jpg")
# print(result)
