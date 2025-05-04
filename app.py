# app.py - Flask backend
import uuid
from flask import Flask, redirect, request, jsonify, render_template, send_from_directory, session, Response
import os
from src.llm_response import LLMInvoke
from werkzeug.utils import secure_filename
from flask_cors import CORS
# Import your prediction function
from src.AttributePred import get_all_attribute_predictions
import sys
import csv
import json
from datetime import datetime, timedelta
# from calculate_scores import calculate_scores
from src.get_color import get_image_colors
import imagehash
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
import toml
from src.weather import get_datecity_forecast, get_weather_json
from src.calculate_scores import calculate_scores
from src.get_color import get_image_colors
from src.clothing_shortlist import read_clothing_csv
from src.predict_cluster import predict_weather_cluster
from src.weather_suitability_clustering import get_weathercluster_list

config_path = os.path.join('config', 'config.toml')
config = toml.load(config_path)



app = Flask(__name__)
CORS(app)


app.secret_key = '0236182485f3cc06f485de4d5156a91c0aa15222c8530ff3d11096681344c4de'   # Required for session management

UPLOAD_FOLDER = config['paths']['UPLOAD_FOLDER']
top_csv = config['paths']['top_wear_csv']
bottom_csv = config['paths']['bottom_wear_csv']
users_csv = config['paths']['users_csv']


print("UPLOAD_FOLDER:", UPLOAD_FOLDER)
print("Top wear CSV:", top_csv)
print("Bottom wear CSV:", bottom_csv)


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('login.html')  # your separate login file

@app.route('/app')
def main_app():
    if 'username' not in session:
        return redirect('/')  # force back to login if not authenticated


    return render_template('online_wardrobe.html', username=session['username'], user_gender=session['user_id'])  # your separate main app file

@app.route('/reset_password_page')
def reset_password_page():
    return render_template('reset_password.html')

@app.route('/recommendation')
def recommendation():
    user_id = session['user_id']
    username = session.get('username', '')
    gender = ''

    # Look up gender from users.csv
    if os.path.exists(users_csv):
        with open(users_csv, mode='r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['user_id'] == user_id:
                    gender = row.get('gender', '')
                    break

    return render_template('instant_recommendations.html', username=username, user_id=user_id, gender=gender)


@app.route('/chatbot')
def chatbot():
    user_id = session['user_id']
    username = session.get('username', '')
    gender = ''

    # Look up gender from users.csv
    if os.path.exists(users_csv):
        with open(users_csv, mode='r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['user_id'] == user_id:
                    gender = row.get('gender', '')
                    break

    return render_template('chatbot.html', username=username, user_id=user_id, gender=gender)


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    gender =  data.get('gender')
    # import pdb; pdb.set_trace()

    # Generate unique user_id
    user_id = str(uuid.uuid4())

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if os.path.exists(users_csv):
        with open(users_csv, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'].lower() == username.lower():
                    return jsonify({'error': 'Username already exists, Please select an unique user name...'}), 400

    password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    file_exists = os.path.isfile(users_csv)
    with open(users_csv, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['user_id', 'username', 'password', 'gender'])
        if not file_exists:
            writer.writeheader()

        writer.writerow({
            'user_id': user_id,
            'username': username,
            'password': password_hash,
            'gender': gender
        })

    return jsonify({'message': 'User registered successfully',  'user_id': user_id}), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if os.path.exists(users_csv):
        with open(users_csv, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'].lower() == username.lower():
                    if check_password_hash(row['password'], password):
                        session['user_id'] = row['user_id']
                        session['username'] = username
                        return jsonify({'message': 'Login successful'}), 200
                    else:
                        return jsonify({'error': 'Invalid password'}), 401

    return jsonify({'error': 'User not found'}), 404

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    username = data.get('username')
    new_password = data.get('new_password')

    if not username or not new_password:
        return jsonify({'error': 'Username and new password are required'}), 400

    updated = False
    updated_rows = []

    if os.path.exists(users_csv):
        with open(users_csv, mode='r', newline='') as f:
            reader = list(csv.DictReader(f))
            for row in reader:
                if row['username'].lower() == username.lower():
                    row['password_hash'] = generate_password_hash(new_password, method='pbkdf2:sha256')
                    updated = True
                updated_rows.append(row)

    if updated:
        with open(users_csv, mode='w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['user_id', 'username', 'password', 'gender'])
            writer.writeheader()
            writer.writerows(updated_rows)
        return jsonify({'message': 'Password reset successful'}), 200
    else:
        return jsonify({'error': 'Username not found'}), 404




def get_image_hash(image_path):
    """
    Generate perceptual hash (pHash) for a given image.
    Returns the hash as a string.
    """
    img = Image.open(image_path)
    hash_value = imagehash.phash(img)
    return str(hash_value)

    
@app.route('/analyze_clothing', methods=['POST'])
def analyze_clothing():

    if 'username' not in session:
        return jsonify({'error': 'Unauthorized: Please log in'}), 401

    current_user = session['username']

    if 'image' not in request.files:
        return jsonify({'error': 'No image found'}), 400

    file = request.files['image']
    clothing_type = request.form.get('type', 'top')

    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400

    filename = secure_filename(file.filename)
    user_upload_folder = os.path.join(UPLOAD_FOLDER, current_user)
    os.makedirs(user_upload_folder, exist_ok=True)
    # filepath = os.path.join(UPLOAD_FOLDER, filename)
    filepath = os.path.join(user_upload_folder, filename)

    # import pdb; pdb.set_trace()
    # Save temporarily to compute hash
    file.save(filepath)
    new_hash = get_image_hash(filepath)


    # Check against existing hashes in CSV
    # csv_files = ['clothing_attributes.csv', 'bottom_wear_clothing_attributes.csv']
    csv_files = [config['paths']['top_wear_csv'], config['paths']['bottom_wear_csv']]

    for csv_file in csv_files:
        if os.path.exists(csv_file):
            with open(csv_file, mode='r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_hash = row.get('image_hash')
                    if existing_hash:
                        # Compare using Hamming distance
                        if imagehash.hex_to_hash(existing_hash) - imagehash.hex_to_hash(new_hash) <= 5:
                            os.remove(filepath)  # clean up temp file
                            return jsonify({'error': 'A visually similar image already exists in the system'}), 400

    try:
        # Process the image (your existing logic)
        result = get_all_attribute_predictions(filepath, clothing_type)
        colors = get_image_colors(filepath)

        result["primary_color_name"] = colors["primary_color_name"]
        result["secondary_color_name"] = colors["secondary_color_name"]
        result['clothing_type'] = clothing_type
        result['image_hash'] = new_hash  # add hash to result for later saving

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/save_attributes', methods=['POST'])
def save_attributes():

    # import pdb; pdb.set_trace()
    # if 'username' not in session:
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized: Please log in'}), 401

    # current_user = session['username']
    current_user_id = session['user_id']

    data = request.json
    image_id = data.get('image_id', '')
    clothing_type = data.get('clothing_type', '')
    attributes = data.get('attributes', {})
    image_hash = data.get('image_hash', '')

    # Calculate warmth and breathability
    warmth, breathability = calculate_scores(attributes, clothing_type)
    print(f"Warmth: {warmth}, Breathability: {breathability}")

    # Make a copy for weather clustering
    new_data_row = data.copy()
    new_data_row['attributes']['warmth_score'] = warmth
    new_data_row['attributes']['breathability_score'] = breathability

    # Rename keys for weather clustering model if needed
    attribute_map = {
        'outer_cardigan': 'outer_clothing_cardigan',
        'navel_covering': 'upper_clothing_covering_navel'
    }
    for old_key, new_key in attribute_map.items():
        if old_key in new_data_row['attributes']:
            new_data_row['attributes'][new_key] = new_data_row['attributes'].pop(old_key)

    # Get weather tags
    try:
        weather_tags = get_weathercluster_list(new_data_row)
    except Exception as e:
        print(f"Warning: Failed to generate weather tags - {e}")
        weather_tags = []
    # import pdb; pdb.set_trace()
    # Select CSV file
    csv_file = config['paths']['top_wear_csv'] if clothing_type.lower() == 'top' else config['paths']['bottom_wear_csv']
    file_exists = os.path.isfile(csv_file)

    # Prepare row for CSV
    row = {
        'user_id': current_user_id,
        'image_id': image_id,
        'clothing_type': clothing_type,
        'image_hash': image_hash,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        # 'warmth_index': warmth,
        'breathability_score': breathability,
        'weather_tags': ', '.join(weather_tags)
    }

    # Add all attributes
    for key, value in attributes.items():
        row[key] = value

    row['warmth_index'] = row['warmth_score']
    del row['warmth_score']
    # Build field order
    base_fields = ['user_id', 'image_id', 'clothing_type', 'image_hash', 'timestamp']
    weather_fields = ['warmth_index', 'breathability_score', 'weather_tags']

    if clothing_type == 'top':
        desired_order = base_fields + [
            'upper_clothing_covering_navel', 'neckline', 'outer_clothing_cardigan',
            'primary_color_name', 'secondary_color_name',
            'sleeve_length', 'Fabric_Type', 'Pattern_Type',
        ] + weather_fields
    else:
        desired_order = base_fields + [
            'lower_clothing_length', 'primary_color_name',
            'secondary_color_name', 'Fabric_Type', 'Pattern_Type'
        ] + weather_fields

    # Keep only fields present
    fieldnames = [field for field in desired_order if field in row]
    
    # Write to CSV
    try:
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

        display_name = generate_item_name(attributes)
        return jsonify({
            'status': 'success',
            'message': 'Attributes saved to CSV',
            'display_name': display_name
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def generate_item_name(attributes):
    attributes = {k: v for k, v in attributes.items() if k is not None}

    # Extract top-wear related attributes
    sleeve = (attributes.get('sleeve_length') or '').lower()
    neckline = (attributes.get('neckline') or '').lower()
    cardigan = (attributes.get('outer_cardigan') or '').lower()

    # Extract bottom-wear related attributes
    length = (attributes.get('lower_clothing_length') or '').lower()
    fabric = (attributes.get('Fabric_Type') or '').lower()
    pattern = (attributes.get('Pattern_Type') or '').lower()

    # Shared fields
    primary_color = (attributes.get('primary_color_name') or '').lower()
    secondary_color = (attributes.get('secondary_color_name') or '').lower()

    name_parts = []

    # -----------------
    # Bottom wear logic
    # -----------------
    if length:
        if length in ['three-point', 'three-quarter', 'short']:
            name_parts.append("Sporty")
        elif length in ['medium', 'medium short']:
            name_parts.append("Casual")
        elif length in ['long', 'full']:
            name_parts.append("Cozy")
        else:
            name_parts.append(length.capitalize())

    if fabric:
        name_parts.append(fabric.capitalize())

    if pattern and pattern not in ['na', 'other']:
        name_parts.append(pattern.capitalize())

    # ----------------
    # Top wear logic
    # ----------------
    adjective_map = {
        'sleeveless': 'Breezy',
        'short-sleeve': 'Casual',
        'medium-sleeve': 'Smart',
        'long-sleeve': 'Cozy'
    }

    if sleeve in adjective_map:
        name_parts.insert(0, adjective_map[sleeve])

    if neckline:
        name_parts.append(f"{neckline.capitalize()} Neck")

    if cardigan == 'yes cardigan':
        name_parts.append('Cardigan')

    # Final display
    display_name = ' '.join(name_parts).strip()
    return display_name if display_name else 'Stylish Outfit'


def load_wardrobe_items_from_csv(csv_file, current_user_id, current_user):
    wardrobe_items = []

    if not os.path.isfile(csv_file):
        return wardrobe_items

    with open(csv_file, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get('user_id') != current_user_id:
                continue  # only include current user's items

            image_id = row.get('image_id')
            clothing_type = row.get('clothing_type')
            attributes = {key: row[key] for key in row if key not in ['username', 'image_id', 'clothing_type', 'timestamp', 'warmth_index', 'breathability_score']}
            attributes = {k: v for k, v in attributes.items() if k is not None}
            # import pdb; pdb.set_trace()
            item = {
                'image_id': image_id,
                'clothing_type': clothing_type,
                'display_name': generate_item_name(attributes),
                'image_url': f"http://127.0.0.1:5002/uploads/{current_user}/{image_id}",
                'attributes': attributes
            }
            wardrobe_items.append(item)

    wardrobe_items.reverse()
    return wardrobe_items


@app.route('/get_wardrobe_items', methods=['GET'])
def get_combined_wardrobe_items():
    # if 'username' not in session:
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized: Please log in'}), 401

    current_user_id = session['user_id']
    current_user = session['username']

    # top_csv = 'clothing_attributes.csv'
    # bottom_csv = 'bottom_wear_clothing_attributes.csv'
    top_csv = config['paths']['top_wear_csv']
    bottom_csv = config['paths']['bottom_wear_csv']


    # top_items = load_wardrobe_items_from_csv(top_csv)
    # bottom_items = load_wardrobe_items_from_csv(bottom_csv)

    top_items = load_wardrobe_items_from_csv(top_csv, current_user_id, current_user)
    bottom_items = load_wardrobe_items_from_csv(bottom_csv, current_user_id, current_user)

    return jsonify(top_items + bottom_items)


# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/uploads/<username>/<filename>')
def uploaded_file(username, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, username), filename)


@app.route('/delete_item/<image_id>', methods=['DELETE'])
def delete_item(image_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized: Please log in'}), 401

    current_user = session['username']

    # top_csv = 'clothing_attributes.csv'
    # bottom_csv = 'bottom_wear_clothing_attributes.csv'
    top_csv = config['paths']['top_wear_csv']
    bottom_csv = config['paths']['bottom_wear_csv']

    try:
        user_upload_folder = os.path.join(UPLOAD_FOLDER, current_user)
        image_path = os.path.join(user_upload_folder, image_id)

        # image_path = os.path.join(UPLOAD_FOLDER, image_id)
        if os.path.exists(image_path):
            os.remove(image_path)

        for csv_file in [top_csv, bottom_csv]:
            if os.path.exists(csv_file):
                with open(csv_file, mode='r', newline='') as file:
                    reader = list(csv.DictReader(file))
                    updated_rows = [row for row in reader if row['image_id'] != image_id]
                    fieldnames = reader[0].keys() if reader else []

                with open(csv_file, mode='w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(updated_rows)

        return jsonify({'status': 'success', 'message': f'Item {image_id} deleted successfully.'}), 200

    except Exception as e:
        print(f"Error deleting item {image_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

@app.route('/api/weather')
def weather_api():
    weather_data = get_weather_json()
    return Response(weather_data, mimetype='application/json')

@app.route('/api/instant-clothing-recommendations')
def clothing_recommendations():
    try:
        # from src.weather import get_weather_json
        weather_data = json.loads(get_weather_json())
        weather_prediction = weather_data.get('prediction', '').lower()
        
        top_wear_items = read_clothing_csv(top_csv, weather_prediction)
        bottom_wear_items = read_clothing_csv(bottom_csv, weather_prediction)

        return jsonify({
            'top_wear': top_wear_items,
            'bottom_wear': bottom_wear_items,
            'weather': weather_prediction
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route("/api/instant-outfit-suggestion", methods=["POST"])
def get_outfit_suggestion():
    if not request.is_json:
        return jsonify({"success": False, "error": "Invalid input, expecting JSON."}), 400

    try:
        data = request.get_json(force=True)
        weather = data.get("weather", "N/A")
        top_wear = data.get("top_wear", [])
        bottom_wear = data.get("bottom_wear", [])
        location = data.get("location", "Unknown")
        gender = data.get("gender", "Unknown")

        llm = LLMInvoke()
        context = generate_llm_context(
            location=location,
            date=datetime.now().strftime("%Y-%m-%d"),
            weather=weather,
            event="casual",
            top_wear_items=top_wear,
            bottom_wear_items=bottom_wear
        )

        query = (
            "Based on the weather and user’s wardrobe, provide a concise outfit recommendation for today. "
            "Use short sentences. Format as an HTML unordered list (<ul><li>...</li></ul>). "
            "Include: "
            "- Top wear (reference wardrobe item or suggest type). "
            "- Bottom wear (reference wardrobe item or suggest type). "
            "- Shoes and accessories. "
            "- One styling tip. "
            "Focus on weather suitability and casual style. If no wardrobe items fit, suggest Amazon shopping with '[shop on Amazon]' placeholder. "
            "Stay friendly and practical."
        )

        llm_result = llm.llm_response(query, context)
        suggestion = llm_result.get("answer", "<ul><li>No outfit suggestion available.</li></ul>")

        return jsonify({"success": True, "suggestion": suggestion})

    except Exception as e:
        print("Error generating outfit suggestion:", e)
        return jsonify({"success": False, "error": str(e)}), 500



from src.llm_context_generator import generate_llm_context  # Adjust import based on your file structure

@app.route("/plan_trip", methods=["POST"])
def plan_trip():
    if not request.is_json:
        return jsonify({"success": False, "error": "Invalid input, expecting JSON."}), 400

    try:
        data = request.get_json(force=True)
        location = data.get("location")
        dates = data.get("dates")
        event = data.get("event")

        if not location or not dates or not event:
            return jsonify({"success": False, "error": "Missing location/dates/event"}), 400

        # Parse dates
        date_parts = dates.split(" to ")
        start_date = datetime.strptime(date_parts[0], "%Y-%m-%d")
        end_date = datetime.strptime(date_parts[1], "%Y-%m-%d")

        # Initialize LLM
        llm = LLMInvoke()

        recommendations = []
        curr = start_date
        while curr <= end_date:
            rec = get_datecity_forecast(location, curr.strftime("%Y-%m-%d"), event)
            if isinstance(rec, str):
                import json
                rec = json.loads(rec)

            # Generate LLM context using the plug-and-play function
            context = generate_llm_context(
                location=location,
                date=curr.strftime("%Y-%m-%d"),
                weather=rec.get("prediction", "N/A"),
                event=event,
                top_wear_items=rec.get("top_wear_items", []),
                bottom_wear_items=rec.get("bottom_wear_items", [])
            )
            # print(context)
            # Define the LLM query
            query = (
                "Based on the trip details and the user’s wardrobe items, "
                "generate a friendly, bulleted, and conversational response suggesting what the user should wear for the day. "
                "Reference specific wardrobe item attributes (e.g., color, fabric, warmth index) and explain why they are suitable for the weather and event. "
                "Suggest a complete outfit, including layering and accessories, and provide packing tips tailored to the trip. "
                "If no wardrobe items are suitable, recommend appropriate clothing types and include a suggestion to shop on Amazon. "
                "Stay supportive and focused on trip-related fashion and packing advice."
            )

            # Get LLM response
            llm_result = llm.llm_response(query, context)
            llm_response = llm_result.get("answer", "No additional tips available.")
            print(llm_response)

            recommendations.append({
                "date": curr.strftime("%Y-%m-%d"),
                "weather": rec.get("prediction", ""),
                "top_wear": rec.get("top_wear_items", []),
                "bottom_wear": rec.get("bottom_wear_items", []),
                "llm_response": llm_response
            })
            curr += timedelta(days=1)

        return jsonify({"success": True, "recommendations": recommendations})

    except Exception as e:
        print("Error during trip planning:", e)
        return jsonify({"success": False, "error": str(e)}), 500
    

@app.route("/ask_question", methods=["POST"])
def ask_question():
    if not request.is_json:
        return jsonify({"success": False, "error": "Invalid input, expecting JSON."}), 400

    try:
        data = request.get_json(force=True)
        question = data.get("question")
        recommendations = data.get("recommendations", [])
        location = data.get("location", "Unknown")
        event = data.get("event", "Unknown")

        if not question:
            return jsonify({"success": False, "error": "Missing question"}), 400

        # Initialize LLM
        llm = LLMInvoke()

        # Generate context for each day’s wardrobe data
        context_parts = []
        for rec in recommendations:
            context = generate_llm_context(
                location=location,
                date=rec.get("date", "Unknown"),
                weather=rec.get("weather", "N/A"),
                event=event,
                top_wear_items=rec.get("top_wear", []),
                bottom_wear_items=rec.get("bottom_wear", [])
            )
            context_parts.append(context)

        # Combine contexts for all days
        full_context = "\n\n".join(context_parts) if context_parts else generate_llm_context(
            location=location,
            date="Unknown",
            weather="N/A",
            event=event
        )

        # Append question-specific instructions
        full_context += f"\n\nUser’s question: {question}\n\nAnswer the user’s question in a friendly, conversational tone, using the wardrobe and trip details above. Focus on trip-related fashion, outfit advice, and packing tips. If the question is unrelated, politely explain that you only assist with trip fashion and packing advice."

        # Query the LLM
        llm_result = llm.llm_response(question, full_context)
        answer = llm_result.get("answer", "Sorry, I couldn’t generate a response. Please try again!")

        return jsonify({"success": True, "answer": answer})

    except Exception as e:
        print("Error processing question:", e)
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5002)


