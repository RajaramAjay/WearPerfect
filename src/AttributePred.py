import numpy as np
import cv2
import tensorflow as tf
import joblib
import matplotlib.pyplot as plt
import os
from tensorflow.keras.models import load_model
import toml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.toml"
config = toml.load(CONFIG_PATH)

# Base path for top_wear_models and top_wear_encoders
base_path = config["attribute_models"]["model_path"]

# Model and encoder filenames
top_wear_model_files = [
    "best_sleeve_model.keras",
    "outer_cardigan_best_model_densenet.keras",
    "navel_covering_model_densenet.keras",
    "neckline_best_model_densenet.keras",
]

top_wear_encoder_files = [
    "sleeve_length_encoder.pkl",
    "outer_cardigan_encoder.pkl",
    "navel_encoder.pkl",
    "neckline_encoder.pkl",
]

# Model and encoder filenames
bottom_wear_model_files = ["best_bottomwear_model.keras"]

bottom_wear_encoder_files = ["bottom_length_encoder.pkl"]


# Attribute names corresponding to each model
top_wear_attribute_names = [
    "sleeve_length",
    "outer_cardigan",
    "navel_covering",
    "neckline",
]

bottom_wear_attribute_names = ["lower_clothing_length"]


# Load top_wear_models and top_wear_encoders
top_wear_models = []
top_wear_encoders = []
bottom_wear_models = []
bottom_wear_encoders = []

# Top Wear models loading
for model_file, encoder_file in zip(top_wear_model_files, top_wear_encoder_files):
    model_path = os.path.join(base_path, model_file)
    encoder_path = os.path.join(base_path, encoder_file)

    try:
        model = load_model(model_path)
        encoder = joblib.load(encoder_path)
        top_wear_models.append(model)
        top_wear_encoders.append(encoder)
        print(f"Successfully loaded {model_file} and {encoder_file}")
    except Exception as e:
        print(f"Error loading {model_file} or {encoder_file}: {str(e)}")
        top_wear_models.append(None)
        top_wear_encoders.append(None)

# bottom Wear models loading
for model_file, encoder_file in zip(bottom_wear_model_files, bottom_wear_encoder_files):
    model_path = os.path.join(base_path, model_file)
    encoder_path = os.path.join(base_path, encoder_file)

    try:
        model = load_model(model_path)
        encoder = joblib.load(encoder_path)
        bottom_wear_models.append(model)
        bottom_wear_encoders.append(encoder)
        print(f"Successfully loaded {model_file} and {encoder_file}")
    except Exception as e:
        print(f"Error loading {model_file} or {encoder_file}: {str(e)}")
        bottom_wear_models.append(None)
        bottom_wear_encoders.append(None)

IMG_SIZE = (128, 128)


# Preprocess Function
def preprocess_image(path):
    img = cv2.imread(path)
    if img is None:
        print(f"⚠ Warning: Image not found {path}")
        return None
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB
    img = cv2.resize(img, IMG_SIZE)  # Resize to match model input
    img = img / 255.0  # Normalize pixel values
    return img


# Function to get image predictions for all attributes and return as dictionary
def get_all_attribute_predictions(image_path, clothing_type):
    # Get image name from path
    image_name = os.path.basename(image_path)

    # Initialize result dictionary with image ID
    result = {"imageid": image_name}

    # Preprocess image
    processed_img = preprocess_image(image_path)

    if processed_img is None:
        # If image not found, set all attributes to "Image not found"
        for attr_name in top_wear_attribute_names:
            result[attr_name] = "Image not found"
        return result

    # Expand dimensions to create batch of size 1
    img_batch = np.expand_dims(processed_img, axis=0)

    if clothing_type.lower() == "top":
        # Make predictions for each top wear model/attribute
        for i, (model, encoder, attr_name) in enumerate(
            zip(top_wear_models, top_wear_encoders, top_wear_attribute_names)
        ):
            if model is None or encoder is None:
                result[attr_name] = "Top Wear Model or encoder not available"
                continue

            try:
                # Make prediction
                pred_probs = model.predict(
                    img_batch, verbose=0
                )  # Set verbose=0 to suppress progress bar
                pred_class_idx = np.argmax(pred_probs, axis=1)[0]
                pred_label = encoder.inverse_transform([pred_class_idx])[0]

                # Add prediction to result dictionary
                result[attr_name] = pred_label

            except Exception as e:
                result[attr_name] = f"Error in prediction: {str(e)}"

    elif clothing_type.lower() == "bottom":
        # Make predictions for each bottom wear model/attribute
        for i, (model, encoder, attr_name) in enumerate(
            zip(bottom_wear_models, bottom_wear_encoders, bottom_wear_attribute_names)
        ):
            if model is None or encoder is None:
                result[attr_name] = "Bottom Wear Model or encoder not available"
                continue
            try:
                # Make prediction
                pred_probs = model.predict(
                    img_batch, verbose=0
                )  # Set verbose=0 to suppress progress bar
                pred_class_idx = np.argmax(pred_probs, axis=1)[0]
                pred_label = encoder.inverse_transform([pred_class_idx])[0]

                # Add prediction to result dictionary
                result[attr_name] = pred_label

            except Exception as e:
                result[attr_name] = f"Error in prediction: {str(e)}"

    return result

