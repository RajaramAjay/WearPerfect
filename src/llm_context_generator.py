def generate_llm_context(location, date, weather, event, top_wear_items=None, bottom_wear_items=None):
    """
    Generates a structured context string for the LLM based on trip and wardrobe data.
    
    Args:
        location (str): The trip destination (e.g., "Baltimore").
        date (str): The date of the trip day (e.g., "2025-05-03").
        weather (str): The weather forecast (e.g., "Cloudy").
        event (str): The planned event(s) (e.g., "casual outing").
        top_wear_items (list): List of top wear items from wardrobe (default: None).
        bottom_wear_items (list): List of bottom wear items from wardrobe (default: None).
    
    Returns:
        str: A formatted context string for the LLM.
    """
    # Initialize wardrobe lists
    top_wear_items = top_wear_items or []
    bottom_wear_items = bottom_wear_items or []

    # Format top wear details
    top_wear_details = []
    for item in top_wear_items:
        top_wear_details.append(
            f"- Image: {item.get('image_id', 'N/A')}, "
            f"Type: {item.get('clothing_type', 'N/A')}, "
            f"Primary Color: {item.get('primary_color_name', 'N/A')}, "
            f"Secondary Color: {item.get('secondary_color_name', 'N/A')}, "
            f"Neckline: {item.get('neckline', 'N/A')}, "
            f"Sleeve Length: {item.get('sleeve_length', 'N/A')}, "
            f"Fabric: {item.get('Fabric_Type', 'N/A')}, "
            f"Pattern: {item.get('Pattern_Type', 'N/A')}, "
            f"Warmth Index: {item.get('warmth_index', 'N/A')}, "
            f"Breathability: {item.get('breathability_score', 'N/A')}, "
            f"Weather Tags: {item.get('weather_tags', 'N/A')}"
        )
    top_wear_text = "\n".join(top_wear_details) if top_wear_details else "None"

    # Format bottom wear details
    bottom_wear_details = []
    for item in bottom_wear_items:
        bottom_wear_details.append(
            f"- Image: {item.get('image_id', 'N/A')}, "
            f"Type: {item.get('clothing_type', 'N/A')}, "
            f"Primary Color: {item.get('primary_color_name', 'N/A')}, "
            f"Secondary Color: {item.get('secondary_color_name', 'N/A')}, "
            f"Fabric: {item.get('Fabric_Type', 'N/A')}, "
            f"Pattern: {item.get('Pattern_Type', 'N/A')}, "
            f"Warmth Index: {item.get('warmth_index', 'N/A')}, "
            f"Breathability: {item.get('breathability_score', 'N/A')}, "
            f"Weather Tags: {item.get('weather_tags', 'N/A')}"
        )
    bottom_wear_text = "\n".join(bottom_wear_details) if bottom_wear_details else "None"

    # Create the context string
    context = f"""
        You are a friendly and expert travel packing assistant specializing in personalized fashion recommendations, outfit advice, and packing tips based on weather, location, planned activities, and the user’s wardrobe.

        Here is the user’s trip information:
        - Location: {location}
        - Date: {date}
        - Weather forecast: {weather}
        - Planned event(s): {event}

        Here are the user’s available wardrobe items for this day:
        - Top wear:
        {top_wear_text}
        - Bottom wear:
        {bottom_wear_text}

        Your role:
        ✅ Provide a warm, conversational recommendation on what the user should wear, referencing specific wardrobe items (e.g., colors, fabrics, warmth index) and explaining why they suit the weather and event.
        ✅ Suggest outfit combinations, layering options, and accessories (e.g., scarves, hats, shoes) that complement the wardrobe items and event.
        ✅ Offer packing tips, such as fabric care, weather preparedness, or space-saving techniques.
        ✅ If no suitable wardrobe items are available, suggest general clothing types and link to Amazon for shopping.
        ✅ Answer follow-up questions related to packing, clothing, or trip preparation.
        ❌ Politely refuse or redirect unrelated questions by explaining that you only assist with trip fashion and packing advice.
    """

    return context.strip()