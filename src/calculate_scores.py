def calculate_top_wear_warmth_score(row):
    # Assign warmth score based on extracted features
    warmth_score = 0

    # Sleeve Length Contribution
    sleeve_warmth = {
        "sleeveless": 1,
        "short-sleeve": 2,
        "medium-sleeve": 3,
        "long-sleeve": 4,
    }
    # Convert sleeve_length to string before applying strip and lower
    sleeve_length = str(row.get("sleeve_length", "short-sleeve"))
    warmth_score += sleeve_warmth.get(sleeve_length.strip().lower(), 2)

    # Fabric Type Contribution
    fabric_warmth = {
        "chiffon": 1,
        "cotton": 2,
        "denim": 3,
        "knitted": 4,
        "furry": 5,
        "leather": 5,
        "other": 2,
    }
    # Convert fabric_type to string before applying strip and lower
    fabric_type = str(row.get("fabric_type", "other"))
    # print(fabi)
    warmth_score += fabric_warmth.get(fabric_type.strip().lower(), 2)

    # Outer Clothing (Cardigan) Contribution
    # Convert outer_clothing_cardigan to string before applying strip and lower
    outer_clothing_cardigan = str(row.get("outer_clothing_cardigan", "no cardigan"))
    if outer_clothing_cardigan.strip().lower() == "yes cardigan":
        warmth_score += 3  # Adding extra warmth for layering

    # Upper Clothing Covering Navel
    # Convert upper_clothing_covering_navel to string before applying strip and lower
    upper_clothing_covering_navel = str(row.get("upper_clothing_covering_navel", "no"))
    if upper_clothing_covering_navel.strip().lower() == "yes":
        warmth_score += 2  # More coverage = more warmth

    return warmth_score


def calculate_top_wear_breathability_score(row):
    # Assign breathability score based on extracted features
    breathability_score = 0

    # Sleeve Length Contribution (More exposure = more breathable)
    sleeve_breathability = {
        "sleeveless": 5,
        "short-sleeve": 4,
        "medium-sleeve": 3,
        "long-sleeve": 2,
    }
    breathability_score += sleeve_breathability.get(
        row.get("sleeve_length", "short-sleeve").strip().lower(), 4
    )

    # Fabric Type Contribution (Lighter fabrics = more breathable)
    fabric_breathability = {
        "chiffon": 5,
        "cotton": 4,
        "denim": 2,
        "knitted": 2,
        "furry": 1,
        "leather": 1,
        "other": 3,
    }
    breathability_score += fabric_breathability.get(
        row.get("fabric_type", "other").strip().lower(), 3
    )

    # Neckline Contribution (More open = more breathable)
    neckline_breathability = {
        "round": 3,
        "v-shape": 5,
        "lapel": 4,
        "standing": 2,
        "square": 3,
        "suspenders": 5,
    }
    breathability_score += neckline_breathability.get(
        row.get("neckline", "round").strip().lower(), 3
    )

    return breathability_score

def calculate_scores(clothing_item, clothing_type):
    if clothing_type.lower() == "top":
        warmth = calculate_top_wear_warmth_score(clothing_item)
        breathability = calculate_top_wear_breathability_score(clothing_item)

    warmth = warmth / 10
    breathability = breathability / 10
    return warmth, breathability

