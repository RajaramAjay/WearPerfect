import csv
import json
import ast
import random
import os
import toml

config_path = os.path.join("config", "config.toml")
config = toml.load(config_path)


# Global in-memory store
# Structure: { (user_id, clothing_type, weather): {'items': [...], 'index': int} }
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
        eligible_items = load_and_filter_clothing(csv_file, weather)
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

    # Advance index
    user_state["index"] += max_items

    # If reached end, reset (reshuffle or restart)
    if user_state["index"] >= len(items):
        random.shuffle(items)
        user_state["index"] = 0

    return batch


def load_and_filter_clothing(csv_file, weather_prediction):
    """
    Loads and filters clothing items from CSV by weather suitability.
    """
    matching_items = []
    weather_prediction = weather_prediction.strip().lower()

    try:
        with open(csv_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if is_suitable_for_weather(
                    row.get("weather_tags", ""), weather_prediction
                ):
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


# def read_clothing_csv(csv_file, weather_prediction):
#     """Read clothing items from CSV and filter by weather suitability"""
#     items = []

#     try:
#         with open(csv_file, mode='r', encoding='utf-8') as file:
#             reader = csv.DictReader(file)
#             # import pdb; pdb.set_trace()
#             for row in reader:
#                 # Check if this item is suitable for the current weather
#                 if is_suitable_for_weather(row, weather_prediction):
#                     items.append(row)
#     except FileNotFoundError:
#         print(f"Warning: {csv_file} not found")
#     except Exception as e:
#         print(f"Error reading {csv_file}: {str(e)}")

#     return items


# def is_suitable_for_weather(clothing_item, weather_prediction):
#     """Check if a clothing item is suitable for the given weather prediction"""
#     # Get weather suitability from the item
#     weather_suitability = clothing_item.get('weather_tags', '')

#     # Handle different formats of Weather_suitability field
#     if not weather_suitability:
#         return False

#     # Handle lists in string format like "[sunny, cold]"
#     if weather_suitability.startswith('[') and weather_suitability.endswith(']'):
#         try:
#             # Convert string representation of list to actual list
#             weather_list = ast.literal_eval(weather_suitability.replace(' ', ', '))
#             return any(condition.lower() in weather_prediction.lower() for condition in weather_list)
#         except:
#             # If parsing fails, do a simple string match
#             return weather_prediction.lower() in weather_suitability.lower()
#     else:
#         # Simple string match
#         return weather_prediction.lower() in weather_suitability.lower()


# top_wear_csv=r"C:\Users\arajaram\OneDrive - Maryland Department of Transportation(MDOT)\Desktop\Capstone project\chatbot for Project\data\top_wear.csv"
# weather_prediction="cloudy"
# items = read_clothing_csv(top_wear_csv,weather_prediction)
# print(items)
