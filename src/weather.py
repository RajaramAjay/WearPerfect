import requests
import pandas as pd
import pickle
import json
from datetime import datetime
import os
import toml

# Find base directory (WearPerfect folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Path to config file
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.toml")

# Load config
config = toml.load(CONFIG_PATH)
top_wear_csv = config["paths"]["top_wear_csv"]
bottom_wear_csv = config["paths"]["bottom_wear_csv"]
weather_suitability_model = config["paths"]["weather_suitability_model"]


def get_location():
    """Fetch user's location using ipinfo.io API."""
    try:
        response = requests.get("https://ipinfo.io", timeout=5)
        response.raise_for_status()
        data = response.json()
        loc = data["loc"].split(",")
        return {
            "city": data.get("city", "region"),
            "latitude": float(loc[0]),
            "longitude": float(loc[1]),
        }
    except (requests.RequestException, ValueError, KeyError):
        return None

def get_weather(city):
    """Fetch current weather data for a given city using WeatherAPI."""
    if not city:
        return None

    API_KEY = "00be02fb14e54d57be2230920252404"
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&aqi=no"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            return None

        current_month = datetime.now().month
        season_map = {
            12: "Winter",
            1: "Winter",
            2: "Winter",
            3: "Spring",
            4: "Spring",
            5: "Spring",
            6: "Summer",
            7: "Summer",
            8: "Summer",
            9: "Fall",
            10: "Fall",
            11: "Fall",
        }

        precip_mm = data["current"]["precip_mm"]
        precip_prob = min((precip_mm * 10), 100)

        return {
            "Temperature": data["current"]["temp_c"],
            "Humidity": data["current"]["humidity"],
            "Wind Speed": data["current"]["wind_kph"],
            "Precipitation (%)": precip_prob,
            "Cloud Cover": data["current"]["condition"]["text"],
            "Atmospheric Pressure": data["current"]["pressure_mb"],
            "UV Index": data["current"]["uv"],
            "Visibility (km)": data["current"]["vis_km"],
            "Location": [f"{data['location']['name']}, {data['location']['country']}"],
            "Season": [season_map[current_month]],
        }
    except (requests.RequestException, KeyError, ValueError):
        return None


def predict_weather(input_data, model_path=weather_suitability_model):
    """Predict weather type using a trained model."""
    try:
        with open(model_path, "rb") as file:
            model = pickle.load(file)
    except FileNotFoundError:
        return None

    if isinstance(input_data, str):
        try:
            input_data = json.loads(input_data)
        except json.JSONDecodeError:
            return None
    elif not isinstance(input_data, dict):
        return None

    processed_data = input_data.copy()
    for key, value in processed_data.items():
        if isinstance(value, list):
            processed_data[key] = value[0] if value else ""

    input_df = pd.DataFrame([processed_data])

    try:
        return model.predict(input_df)[0]
    except Exception:
        return None


def get_weather_json():
    """Generate JSON result with three components"""
    result = {"location": None, "weather_data": None, "prediction": None}

    location = get_location()
    if not location:
        return json.dumps(result)
    weather_data = get_weather(location["city"])
    # weather_data = get_weather(location['latitude'],location['longitude'] )
    if not weather_data:
        result["location"] = location
        return json.dumps(result)

    prediction = predict_weather(weather_data)

    result.update(
        {"location": location, "weather_data": weather_data, "prediction": prediction}
    )

    return json.dumps(result, indent=2)


# Replace with your actual API key
from src.clothing_shortlist import get_next_wardrobe_batch


def get_datecity_forecast(city, date, user_id, event=None):
    """
    Fetch weather forecast for a given city and date (up to 14 days ahead on free plan).

    Args:
        city (str): City name (e.g., 'Baltimore')
        date (str or datetime): Date in 'YYYY-MM-DD' format or datetime object

    Returns:
        dict: Weather features or error message
    """

    result = {
        "city": city,
        "date": date,
        "prediction": None,
        "top_wear_items": None,
        "bottom_wear_items": None,
    }

    API_KEY = "00be02fb14e54d57be2230920252404"
    # Convert date to string if it’s a datetime object
    if isinstance(date, datetime):
        date = date.strftime("%Y-%m-%d")

    # Build the API URL
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&dt={date}"

    try:
        response = requests.get(url)
        data = response.json()
        # print("data--------------",data)

        if "error" in data:
            return {"error": data["error"]["message"]}

        # Forecast values for the day
        forecast_day = data["forecast"]["forecastday"][0]["day"]
        avg_temp = forecast_day["avgtemp_c"]
        humidity = forecast_day["avghumidity"]
        wind_kph = forecast_day["maxwind_kph"]
        precip_mm = forecast_day["totalprecip_mm"]
        condition = forecast_day["condition"]["text"]
        uv_index = forecast_day["uv"]

        # Convert precipitation mm to rough probability percentage
        precip_prob = min((precip_mm * 10), 100)

        # Estimate season
        month = datetime.strptime(date, "%Y-%m-%d").month
        season_map = {
            12: "Winter",
            1: "Winter",
            2: "Winter",
            3: "Spring",
            4: "Spring",
            5: "Spring",
            6: "Summer",
            7: "Summer",
            8: "Summer",
            9: "Fall",
            10: "Fall",
            11: "Fall",
        }

        w_data = {
            "Temperature": avg_temp,
            "Humidity": humidity,
            "Wind Speed": wind_kph,
            "Precipitation (%)": precip_prob,
            "Cloud Cover": condition,
            "Atmospheric Pressure": (
                data["current"]["pressure_mb"] if "current" in data else "N/A"
            ),
            "UV Index": uv_index,
            "Visibility (km)": (
                data["current"]["vis_km"] if "current" in data else "N/A"
            ),
            "Location": [f"{data['location']['name']}, {data['location']['country']}"],
            "Season": [season_map[month]],
        }

        prediction = predict_weather(w_data)
        top_wear_items = get_next_wardrobe_batch(user_id, prediction, "top")
        bottom_wear_items = get_next_wardrobe_batch(user_id, prediction, "bottom")

        result.update(
            {
                "city": city,
                "date": date,
                "prediction": prediction,
                "top_wear_items": top_wear_items,
                "bottom_wear_items": bottom_wear_items,
            }
        )

        return json.dumps(result, indent=2)

    except Exception as e:
        return {"error": str(e)}





