from datetime import datetime

def calculate_rank_score(
    distance,
    customer_heading,
    merchant_heading,
    customer_speed,
    category
):
    score = 0.0

    # 1. DISTANCE (55%) - Proximity is the absolute strongest indicator
    if distance < 0.02:    # Inside/very close (20m)
        score += 55.0
    elif distance < 0.05:  # Within 50m
        score += 48.0
    elif distance < 0.1:   # Within 100m
        score += 40.0
    elif distance < 0.3:   # Within 300m
        score += 30.0
    elif distance < 0.8:   # Within 800m
        score += 20.0
    else:                  # Further away
        score += 10.0

    # 2. DIRECTION (20%) - Heading diff matters only when user is actually moving
    if customer_speed > 1.0:
        heading_difference = abs(customer_heading - merchant_heading)
        # Normalize difference to [0, 180]
        if heading_difference > 180:
            heading_difference = 360.0 - heading_difference
        direction_score = max(0.0, 20.0 - (heading_difference / 9.0))
        score += direction_score
    else:
        # Stationary user: don't penalize for heading since GPS compass is noisy when still
        score += 20.0

    # 3. SPEED CONTEXT (10%)
    if customer_speed < 2.0:
        # User is stationary/walking: Cafe, Restaurant, Grocery, Clothing, Salon, Retail, Stationery
        if category in ["Cafe", "Restaurant", "Grocery", "Clothing", "Salon", "Retail", "Stationery", "Other", "Restaurant", "Grocery"]:
            score += 10.0
    else:
        # User is moving fast: Medical, Grocery, Electronics
        if category in ["Medical", "Grocery", "Electronics", "Retail", "Other"]:
            score += 10.0

    # 4. TIME CONTEXT (10%)
    hour = datetime.now().hour
    
    if 6 <= hour <= 11:
        # Morning: Cafe, Restaurant, Grocery, Medical
        if category in ["Cafe", "Restaurant", "Grocery", "Medical"]:
            score += 10.0
    elif 12 <= hour <= 16:
        # Afternoon: Restaurant, Cafe, Clothing, Retail, Grocery
        if category in ["Restaurant", "Cafe", "Clothing", "Retail", "Grocery"]:
            score += 10.0
    elif 17 <= hour <= 22:
        # Evening: Restaurant, Cafe, Grocery, Clothing, Salon, Retail
        if category in ["Restaurant", "Cafe", "Grocery", "Clothing", "Salon", "Retail"]:
            score += 10.0
    else:
        # Night: Medical, Restaurant, Other
        if category in ["Medical", "Restaurant", "Other"]:
            score += 10.0

    # 5. CATEGORY FREQUENCY BONUS (5%)
    # Give a minor base bonus for highly frequent payment categories
    if category in ["Restaurant", "Cafe", "Grocery", "Medical", "Retail"]:
        score += 5.0
    else:
        score += 2.0

    return round(score, 2)