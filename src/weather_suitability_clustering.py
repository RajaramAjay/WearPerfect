# Import required libraries
import pandas as pd
import numpy as np
from kmodes.kprototypes import KPrototypes
import os
import toml

# Find base directory (WearPerfect folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Path to config file
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.toml")

# Load config
config = toml.load(CONFIG_PATH)
clustering_weather_data_topwear = config["paths"]["clustering_weather_data_topwear"]


# -----------------------------------
def preprocess_topwear_data(
    df,
    new_record_dict,
    normalize_scores=True,
):

    categorical_cols = [
        "sleeve_length",
        "neckline",
        "outer_clothing_cardigan",
        "upper_clothing_covering_navel",
        "Fabric_Type",
        "Pattern_Type",
    ]
    numerical_cols = ["warmth_score", "breathability_score"]

    #   if normalize_scores:
    #       df["warmth_score"] = df["warmth_score"] * 10
    #       df["breathability_score"] = df["breathability_score"] * 10

    #   df.drop(['hard_cluster', 'weather_suitability'], axis=1, inplace=True)
    new_record_df = pd.DataFrame([new_record_dict])
    # Append new record to original dataframe for clustering
    df = pd.concat([df, new_record_df], ignore_index=True)  # Combine dataframes
    cat_data = df[categorical_cols].astype(str).to_numpy()
    num_data = df[numerical_cols].astype(float).to_numpy()

    X_np = np.concatenate([num_data, cat_data], axis=1)
    cat_cols = [i for i in range(num_data.shape[1], X_np.shape[1])]
    print(df.tail(5))

    return df, X_np, cat_cols, categorical_cols, numerical_cols


# -------------------------------------------
# Function to fit K-Prototypes Clustering
# -------------------------------------------
def fit_kprototypes(X_np, cat_cols, n_clusters=4, random_state=42):
    kproto = KPrototypes(
        n_clusters=n_clusters, init="Cao", verbose=1, random_state=random_state
    )
    clusters = kproto.fit_predict(X_np, categorical=cat_cols)
    centroids = kproto.cluster_centroids_
    return kproto, clusters, centroids


# --------------------------------------------
# Function to compute soft (fuzzy) labels
# --------------------------------------------
def compute_soft_labels(X_np, centroids, categorical_cols):
    soft_labels = []
    for row in X_np:
        distances = []
        for center in centroids:
            d = 0
            for i in range(len(row)):
                if i in categorical_cols:
                    d += int(str(row[i]) != str(center[i]))
                else:
                    d += (float(row[i]) - float(center[i])) ** 2
            distances.append(np.sqrt(d))
        distances = np.array(distances)
        proximity = 1 / (distances + 1e-6)
        proximity /= proximity.sum()
        soft_labels.append(proximity)
    return np.array(soft_labels)


# ----------------------------------------------
# Function to map clusters to weather tags
# ----------------------------------------------
def assign_weather_labels(soft_scores, threshold=0.25):
    cluster_to_weather = {0: "sunny", 1: "cloudy", 2: "snowy", 3: "rainy"}
    multi_labels = []
    for row in soft_scores:
        tags = [cluster_to_weather[i] for i, p in enumerate(row) if p >= threshold]
        multi_labels.append(tags if tags else ["sunny"])
    return multi_labels


# --------------------------------------------------
# Master function to run the entire clustering flow
# --------------------------------------------------
def run_topwear_clustering(new_record_dict):
    df = pd.read_csv(clustering_weather_data_topwear)
    # Preprocessing
    df, X_np, cat_cols, categorical_cols, numerical_cols = preprocess_topwear_data(
        df, new_record_dict
    )

    # Fit clustering model
    kproto, clusters, centroids = fit_kprototypes(X_np, cat_cols)
    df["hard_cluster"] = clusters

    # Compute fuzzy labels
    soft_scores = compute_soft_labels(X_np, centroids, cat_cols)

    # Assign weather suitability
    df["weather_suitability"] = assign_weather_labels(soft_scores)
    new_record_weather_suitability = df.iloc[-1]["weather_suitability"]
    # df = df.iloc[:-1]

    return new_record_weather_suitability


def get_weathercluster_list(record):
    # Define the fields you want
    fields_to_extract = [
        "image_id",
        "sleeve_length",
        "neckline",
        "outer_clothing_cardigan",
        "upper_clothing_covering_navel",
        "Fabric_Type",
        "Pattern_Type",
        "warmth_score",
        "breathability_score",
    ]

    # Create a new dictionary by extracting required fields
    new_record = {
        "Image_ID": record.get("image_id"),  # First get image_id from top level
        "sleeve_length": record["attributes"].get("sleeve_length"),
        "neckline": record["attributes"].get("neckline"),
        "outer_clothing_cardigan": record["attributes"].get("outer_clothing_cardigan"),
        "upper_clothing_covering_navel": record["attributes"].get(
            "upper_clothing_covering_navel"
        ),
        "Fabric_Type": record["attributes"].get("Fabric_Type"),
        "Pattern_Type": record["attributes"].get("Pattern_Type"),
        "warmth_score": record["attributes"].get("warmth_score"),
        "breathability_score": record["attributes"].get("breathability_score"),
    }

    #   print(new_record)
    new_record_weather_suitability = run_topwear_clustering(new_record)
    return new_record_weather_suitability


# record = {'image_id': 'WhatsApp_Image_2025-04-14_at_2.50.47_PM.jpeg', 'clothing_type': 'top', 'attributes': {'neckline': 'lapel', 'primary_color_name': 'gunmetal', 'secondary_color_name': 'brownish grey', 'sleeve_length': 'long-sleeve', 'Fabric_Type': 'Cotton', 'Pattern_Type': 'Pure Color', 'warmth_score': 0.6, 'breathability_score': 0.9, 'outer_clothing_cardigan': 'no cardigan', 'upper_clothing_covering_navel': 'yes'}}
# new_record_weather_suitability = get_weathercluster_list(record)
# print(new_record_weather_suitability)

# import pandas as pd

# # Load your CSV file
# input_csv = 'final_top_wear_with_color (1).csv'
# df = pd.read_csv(input_csv)

def determine_bottom_wear_weather_suitability(row):
    fabric = str(row['attributes'].get('Fabric_Type', '')).strip().lower()
    length = str(row['attributes'].get('lower_clothing_length', '')).strip().lower()

    suitability = set()
    unknown_flags = []

    # Fabric-based weather suitability
    if fabric in ['denim', 'corduroy', 'wool', 'leather']:
        fabric_suit = {'cloudy', 'snowy'}
    elif fabric in ['cotton', 'linen', 'rayon']:
        fabric_suit = {'sunny', 'cloudy'}
    elif fabric in ['polyester', 'spandex']:
        fabric_suit = {'sunny', 'rainy'}
    elif fabric in ['twill']:
        fabric_suit = {'cloudy', 'sunny'}
    else:
        fabric_suit = set()
        unknown_flags.append(f"Unknown fabric: {fabric}")

    # Length-based weather suitability
    if length == 'long':
        length_suit = {'cloudy', 'snowy'}
    elif length == 'medium short':
        length_suit = {'sunny', 'cloudy'}
    elif length == 'three-quarter':
        length_suit = {'sunny', 'cloudy', 'rainy'}
    elif length == 'three-point':
        length_suit = {'sunny', 'rainy'}
    else:
        length_suit = set()
        unknown_flags.append(f"Unknown length: {length}")
    # Combine logic: intersection if both sets exist, else whichever exists
    if fabric_suit and length_suit:
        suitability = fabric_suit.intersection(length_suit)
    else:
        suitability = fabric_suit.union(length_suit)

    # Ensure at least one tag
    if not suitability:
        suitability.add('general')

    # Count how many seasons this item fits
    season_count = len(suitability)

    # Log unknowns for debugging
    if unknown_flags:
        print(f"Row ID {row.get('image_id', 'N/A')}: ", '; '.join(unknown_flags))

    return ', '.join(suitability)
    # return pd.Series({
    #     'weather_suitability': ', '.join(sorted(suitability)),
    #     'season_count': season_count
    # })

# # Apply the function and expand results
# df[['weather_suitability', 'season_count']] = df.apply(determine_weather_suitability, axis=1)

# # Save the updated CSV
# output_csv = 'final_lower_wear_with_weather_suitability.csv'
# df.to_csv(output_csv, index=False)

# print(f"✅ Weather suitability and season count columns added and saved to {output_csv}")
