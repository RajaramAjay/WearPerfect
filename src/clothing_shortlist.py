import csv
import json
import ast

def read_clothing_csv(csv_file, weather_prediction):
    """Read clothing items from CSV and filter by weather suitability"""
    items = []
    
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # import pdb; pdb.set_trace()
            for row in reader:
                # Check if this item is suitable for the current weather
                if is_suitable_for_weather(row, weather_prediction):
                    items.append(row)
    except FileNotFoundError:
        print(f"Warning: {csv_file} not found")
    except Exception as e:
        print(f"Error reading {csv_file}: {str(e)}")
    
    return items



def is_suitable_for_weather(clothing_item, weather_prediction):
    """Check if a clothing item is suitable for the given weather prediction"""
    # Get weather suitability from the item
    weather_suitability = clothing_item.get('weather_tags', '')
    
    # Handle different formats of Weather_suitability field
    if not weather_suitability:
        return False
    
    # Handle lists in string format like "[sunny, cold]"
    if weather_suitability.startswith('[') and weather_suitability.endswith(']'):
        try:
            # Convert string representation of list to actual list
            weather_list = ast.literal_eval(weather_suitability.replace(' ', ', '))
            return any(condition.lower() in weather_prediction.lower() for condition in weather_list)
        except:
            # If parsing fails, do a simple string match
            return weather_prediction.lower() in weather_suitability.lower()
    else:
        # Simple string match
        return weather_prediction.lower() in weather_suitability.lower()
    

# top_wear_csv=r"C:\Users\arajaram\OneDrive - Maryland Department of Transportation(MDOT)\Desktop\Capstone project\chatbot for Project\data\top_wear.csv"
# weather_prediction="cloudy"
# items = read_clothing_csv(top_wear_csv,weather_prediction)
# print(items)