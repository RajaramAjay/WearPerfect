import csv
import json
import ast
import random
import os
import toml

config_path = os.path.join("config", "config.toml")
config = toml.load(config_path)


user_batch_state = {}


def get_next_wardrobe_batch(user_id, weather, clothing_type, max_items=5):
    """
    Returns the next batch of clothing items for the given user, weather, and clothing type.
    If no session exists, it initializes and shuffles the list.
    """
    global user_batch_state
    weather = weather.strip().lower()
    key = (user_id, clothing_type, weather)
    csv_file = (
        config["paths"]["top_wear_csv"]
        if clothing_type.lower() == "top"
        else config["paths"]["bottom_wear_csv"]
    )

    # Initialize if first time or no state
    if key not in user_batch_state:
        eligible_items = load_and_filter_clothing(csv_file, weather, user_id)
        random.shuffle(eligible_items)
        user_batch_state[key] = {"items": eligible_items, "index": 0}

    user_state = user_batch_state[key]
    items = user_state["items"]
    index = user_state["index"]

    # If no eligible items, return empty list
    if not items:
        return []

    # Get next batch
    batch = items[index : index + max_items]

    user_state["index"] += max_items

    if user_state["index"] >= len(items):
        random.shuffle(items)
        user_state["index"] = 0

    return batch


def load_and_filter_clothing(csv_file, weather_prediction, user_id):
    """
    Loads and filters clothing items from CSV by weather suitability.
    """
    matching_items = []
    weather_prediction = weather_prediction.strip().lower()

    try:
        with open(csv_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Check if row belongs to this user
                row_user_id = row.get("user_id", "").strip()
                if str(row_user_id) != str(user_id):
                    continue  # skip other users' items

                # Check if weather matches
                if is_suitable_for_weather(row.get("weather_tags", ""), weather_prediction):
                    matching_items.append(row)
                
    except Exception as e:
        print(f"Error loading {csv_file}: {e}")

    return matching_items


def is_suitable_for_weather(weather_tags_str, weather_prediction):
    """
    Checks if the weather_prediction matches any of the weather_tags.
    """
    weather_tags_str = weather_tags_str.strip()
    if not weather_tags_str:
        return False

    try:
        if weather_tags_str.startswith("[") and weather_tags_str.endswith("]"):
            weather_list = ast.literal_eval(weather_tags_str)
        else:
            weather_list = [w.strip() for w in weather_tags_str.split(",")]
        weather_list = [w.lower() for w in weather_list]
        return any(weather_prediction in tag for tag in weather_list)
    except Exception:
        return weather_prediction in weather_tags_str.lower()

