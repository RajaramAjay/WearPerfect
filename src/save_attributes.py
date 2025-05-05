from src.calculate_scores import calculate_scores
from src.weather_suitability_clustering import determine_bottom_wear_weather_suitability, get_weathercluster_list
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os

def top_wear_save_attributes(current_user_id, data, config):          
    image_id = data.get("image_id", "")
    attributes = data.get("attributes", {})
    image_hash = data.get("image_hash", "")
    # Calculate warmth and breathability
    warmth, breathability = calculate_scores(attributes, "clothing_type")
    print(f"Warmth: {warmth}, Breathability: {breathability}")

    # Make a copy for weather clustering
    new_data_row = data.copy() 
    new_data_row["attributes"]["warmth_score"] = warmth
    new_data_row["attributes"]["breathability_score"] = breathability

    # Rename keys for weather clustering model if needed
    attribute_map = {
    "outer_cardigan": "outer_clothing_cardigan",
    "navel_covering": "upper_clothing_covering_navel",
    }
    for old_key, new_key in attribute_map.items():
        if old_key in new_data_row["attributes"]:
            new_data_row["attributes"][new_key] = new_data_row["attributes"].pop(
                old_key
            )

    # Get weather tags
    try:
        weather_tags = get_weathercluster_list(new_data_row)
    except Exception as e:
        print(f"Warning: Failed to generate weather tags - {e}")
        weather_tags = []
   

    # Prepare row for CSV
    row = {
    "user_id": current_user_id,
    "image_id": secure_filename(image_id),
    "clothing_type": "top",
    "image_hash": image_hash,
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    # 'warmth_index': warmth,
    "breathability_score": breathability,
    "weather_tags": ", ".join(weather_tags),
    }

    # Add all attributes
    for key, value in attributes.items():
        row[key] = value

    row["warmth_index"] = row["warmth_score"]
    del row["warmth_score"]
    # Build field order
    base_fields = ["user_id", "image_id", "clothing_type", "image_hash", "timestamp"]
    weather_fields = ["warmth_index", "breathability_score", "weather_tags"]

    desired_order = (
        base_fields
        + [
            "upper_clothing_covering_navel",
            "neckline",
            "outer_clothing_cardigan",
            "primary_color_name",
            "secondary_color_name",
            "sleeve_length",
            "Fabric_Type",
            "Pattern_Type",
        ]
        + weather_fields
        )
    # else:
    #     desired_order = (
    #         base_fields
    #         + [
    #             "lower_clothing_length",
    #             "primary_color_name",
    #             "secondary_color_name",
    #             "Fabric_Type",
    #             "Pattern_Type",
    #         ]
    #         + weather_fields
    #     )

    return row, desired_order

def bottom_wear_save_attributes(current_user_id, data):
    image_id = data.get("image_id", "")
    attributes = data.get("attributes", {})
    image_hash = data.get("image_hash", "")
    # Calculate warmth and breathability
    # warmth, breathability = calculate_scores(attributes, "clothing_type")
    # print(f"Warmth: {warmth}, Breathability: {breathability}")

    # Make a copy for weather clustering
    new_data_row = data.copy()
    # new_data_row["attributes"]["warmth_score"] = warmth
    # new_data_row["attributes"]["breathability_score"] = breathability

    # Rename keys for weather clustering model if needed
    # attribute_map = {
    # "outer_cardigan": "outer_clothing_cardigan",
    # "navel_covering": "upper_clothing_covering_navel",
    # # }
    # # for old_key, new_key in attribute_map.items():
    #     if old_key in new_data_row["attributes"]:
    #         new_data_row["attributes"][new_key] = new_data_row["attributes"].pop(
    #             old_key
    #         )

    # Get weather tags
    try:
        weather_tags = determine_bottom_wear_weather_suitability(new_data_row)
    except Exception as e:
        print(f"Warning: Failed to generate weather tags - {e}")
        weather_tags = []
   

    # Prepare row for CSV
    row = {
    "user_id": current_user_id,
    "image_id": secure_filename(image_id),
    "clothing_type": "bottom",
    "image_hash": image_hash,
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    # 'warmth_index': warmth,
    # "breathability_score": breathability,
    "weather_tags": weather_tags,
    }

    # Add all attributes
    for key, value in attributes.items():
        row[key] = value

    # row["warmth_index"] = row["warmth_score"]
    # del row["warmth_score"]
    # Build field order
    base_fields = ["user_id", "image_id", "clothing_type", "image_hash", "timestamp"]
    weather_fields = ["weather_tags"]

    desired_order = (
        base_fields
        + [
            "lower_clothing_length",
            "primary_color_name",
            "secondary_color_name",
            "Fabric_Type",
            "Pattern_Type",
        ]
        + weather_fields
    )

    return row, desired_order