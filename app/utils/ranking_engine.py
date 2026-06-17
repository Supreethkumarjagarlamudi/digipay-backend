from datetime import datetime

def calculate_rank_score(
    distance,
    customer_heading,
    merchant_heading,
    customer_speed,
    category
):
    score = 0.0
    category_lower = category.lower() if category else "other"

    # 1. DISTANCE (65%) - Proximity is the absolute strongest indicator
    if distance < 0.05:    # Inside/very close (50m)
        score += 65.0
    elif distance < 0.15:  # Within 150m
        score += 60.0
    elif distance < 0.3:   # Within 300m
        score += 50.0
    elif distance < 0.8:   # Within 800m
        score += 35.0
    else:                  # Further away
        score += 15.0

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

    # 3. SPEED CONTEXT (10%) - Lenient category recognition
    # All standard categories are supported dynamically
    valid_categories = ["cafe", "restaurant", "food", "grocery", "clothing", "salon", "retail", "stationery", "other", "electronics", "medical", "shopping", "entertainment", "bills"]
    
    if customer_speed < 2.0:
        # Walking speed
        if category_lower in valid_categories:
            score += 10.0
    else:
        # In transit speed
        if category_lower in valid_categories:
            score += 10.0

    # 4. TIME CONTEXT (10%)
    hour = datetime.now().hour
    
    if 6 <= hour <= 11:
        # Morning
        if category_lower in ["cafe", "restaurant", "food", "grocery", "medical", "retail", "other"]:
            score += 10.0
    elif 12 <= hour <= 16:
        # Afternoon
        if category_lower in ["restaurant", "cafe", "food", "clothing", "retail", "grocery", "electronics", "shopping", "other"]:
            score += 10.0
    elif 17 <= hour <= 22:
        # Evening
        if category_lower in ["restaurant", "cafe", "food", "grocery", "clothing", "salon", "retail", "shopping", "entertainment", "other"]:
            score += 10.0
    else:
        # Night
        if category_lower in ["medical", "restaurant", "food", "other", "cafe"]:
            score += 10.0

    # 5. CATEGORY FREQUENCY BONUS (5%)
    if category_lower in ["restaurant", "cafe", "food", "grocery", "medical", "retail", "electronics", "shopping", "entertainment", "bills", "other"]:
        score += 5.0
    else:
        score += 2.0

    return round(score, 2)