import joblib
import numpy as np
import os



def compute_soft_labels(X_np, centroids, categorical_indices):
    """
    Compute soft labels (proximity scores) for a single data point to each cluster centroid.
    
    Parameters:
    - X_np: numpy array of shape (1, n_features) containing the data point
    - centroids: numpy array of shape (n_clusters, n_features) containing cluster centroids
    - categorical_indices: list of indices of categorical columns in X_np
    
    Returns:
    - proximity: numpy array of shape (n_clusters,) with proximity scores
    """
    distances = []
    row = X_np[0]  # Extract the single row (since X_np is shape (1, n_features))
    
    for center in centroids:
        d = 0
        for i in range(len(row)):
            if i in categorical_indices:
                d += (row[i] != center[i])  # Boolean treated as 0 or 1
            else:
                d += (float(row[i]) - float(center[i])) ** 2
        distances.append(np.sqrt(d))
    
    distances = np.array(distances)
    proximity = 1 / (distances + 1e-6)  # Avoid division by zero
    proximity /= proximity.sum()  # Normalize to sum to 1
    return proximity

def predict_weather_cluster(new_data_row):
    """
    Predict the cluster and weather tags for a new data row.
    
    Parameters:
    - kproto: Trained KPrototypes model
    - centroids: Cluster centroids
    - new_data_row: Dictionary-like object with feature values, possibly with nested 'attributes'
    - numerical_cols: List of numerical column names
    - categorical_cols: List of categorical column names
    - cluster_to_weather: Mapping of cluster indices to weather tags
    - threshold: Proximity threshold for including weather tags
    
    Returns:
    - hard_cluster: Predicted cluster index
    - weather_tags: List of weather tags based on proximity
    """
    # Define base path for model files
    base_path = r"C:\Users\arajaram\OneDrive - Maryland Department of Transportation(MDOT)\Desktop\Capstone project\chatbot for Project\Models\seasonality_clustering"

    # Load saved components
    kproto = joblib.load(os.path.join(base_path, "kproto_topwear_model.pkl"))
    centroids = joblib.load(os.path.join(base_path, "kproto_topwear_centroids.pkl"))
    cat_cols = joblib.load(os.path.join(base_path, "kproto_topwear_cat_indices.pkl"))
    config = joblib.load(os.path.join(base_path, "kproto_topwear_config.pkl"))

    # Extract configuration
    cluster_to_weather = config["cluster_to_weather"]
    numerical_cols = config["numerical_cols"]
    categorical_cols = config["categorical_cols"]
    threshold=0.25

    try:

        # Helper function to get value from top-level or nested attributes
        def get_value(data, col):
            if col in data:
                return data[col]
            elif 'attributes' in data and col in data['attributes']:
                return data['attributes'][col]
            raise KeyError(f"Column '{col}' not found in new_data_row or its attributes")

        # Extract numerical and categorical data
        num_data = np.array([float(get_value(new_data_row, col)) for col in numerical_cols])
        cat_data = np.array([str(get_value(new_data_row, col)) for col in categorical_cols])
        row_np = np.concatenate([num_data, cat_data])
        row_np_2d = row_np.reshape(1, -1)  # Shape (1, n_features)

        # Indices of categorical columns in the combined array
        cat_offset_indices = list(range(len(numerical_cols), len(numerical_cols) + len(categorical_cols)))

        # Predict hard cluster
        hard_cluster = kproto.predict(row_np_2d, categorical=cat_offset_indices)[0]

        # Compute soft/fuzzy proximity
        soft = compute_soft_labels(row_np_2d, centroids, cat_offset_indices)

        # Assign weather tags based on proximity threshold
        weather_tags = [cluster_to_weather[i] for i, p in enumerate(soft) if p >= threshold]
        if not weather_tags:
            weather_tags = [cluster_to_weather[hard_cluster]]  # Fallback to hard cluster's weather

        return hard_cluster, weather_tags

    except KeyError as e:
        raise KeyError(f"Missing column in new_data_row: {e}")
    except ValueError as e:
        raise ValueError(f"Invalid data type in new_data_row: {e}")

# Example usage (uncomment to test)
# new_data = {'image_id': 'PXL_20250313_145030459.jpg', 'clothing_type': 'top', 'attributes': {'upper_clothing_covering_navel': 'yes', 'neckline': 'round', 'outer_clothing_cardigan': 'no cardigan', 'primary_color_name': 'dark', 'secondary_color_name': 'charcoal', 'sleeve_length': 'long-sleeve', 'Fabric_Type': 'Cotton', 'Pattern_Type': 'Pure Color','warmth_score':0.5,'breathability_score':0.9}}


# new_data={'image_id': 'PXL_20250313_145030459.jpg', 'clothing_type': 'top', 'attributes': {'navel_covering': 'yes', 'neckline': 'round', 'outer_cardigan': 'no cardigan', 'primary_color_name': 'dark', 'secondary_color_name': 'charcoal', 'sleeve_length': 'long-sleeve', 'Fabric_Type': 'Cotton', 'Pattern_Type': 'Pure Color'}}

# new_data_row = new_data.copy()
# from calculate_scores import calculate_scores
# warmth, breathability = calculate_scores(new_data_row["attributes"])
# new_data_row['attributes']['warmth_score'] = warmth
# new_data_row['attributes']['breathability_score'] = breathability
# # Rename keys if necessary to match model's expectations
# attribute_map = {
#     'outer_cardigan': 'outer_clothing_cardigan',
#     'navel_covering': 'upper_clothing_covering_navel'

# }
# # Apply renaming
# for old_key, new_key in attribute_map.items():
#     if old_key in new_data_row['attributes']:
#         new_data_row['attributes'][new_key] = new_data_row['attributes'].pop(old_key)
# # print(new_data_row)
# cluster, weather_tag = predict_weather_cluster(new_data_row)
# print(f"Cluster: {cluster}, Weather Tags: {weather_tag}")