import math
from datetime import datetime

def calculate_rank_score(
    distance,
    customer_heading,
    merchant_heading,
    customer_speed,
    category,
    user_category_preference=0.0,  # Float 0.0 to 1.0
    merchant_popularity=0.0        # Float 0.0 to 1.0
):
    score = 0.0
    category_lower = category.lower() if category else "other"

    # 1. DISTANCE DECAY (50%) - Exponential decay
    # scale factor d0 = 0.5 km (500 meters half-life decay)
    # This ensures scores drop to near-zero as distance increases (e.g. 5km is <0.02% of score)
    d0 = 0.5
    distance_score = 50.0 * math.exp(-distance / d0)
    score += distance_score

    # 2. DIRECTION / HEADING (25%) - Alignment checks
    if customer_speed > 1.0:
        heading_difference = abs(customer_heading - merchant_heading)
        if heading_difference > 180:
            heading_difference = 360.0 - heading_difference
        # High sensitivity: full points for 0-10 deg diff, dropping linearly
        direction_score = max(0.0, 25.0 - (heading_difference / 7.2))
        score += direction_score
    else:
        # Stationary user: compas noise exemption
        score += 25.0

    # 3. USER CATEGORY PREFERENCE BOOST (10%) - Co-location tie-breaker
    # Boost if user regularly buys from this category
    score += (user_category_preference * 10.0)

    # 4. STORE POPULARITY BOOST (10%) - Co-location tie-breaker
    score += (merchant_popularity * 10.0)

    # 5. TIME CONTEXT (5%)
    hour = datetime.utcnow().hour
    time_score = 0.0
    if 6 <= hour <= 11:
        if category_lower in ["cafe", "restaurant", "food", "grocery", "medical"]:
            time_score = 5.0
    elif 12 <= hour <= 16:
        if category_lower in ["restaurant", "cafe", "food", "shopping", "electronics"]:
            time_score = 5.0
    elif 17 <= hour <= 22:
        if category_lower in ["restaurant", "cafe", "food", "grocery", "shopping", "entertainment"]:
            time_score = 5.0
    else:
        if category_lower in ["medical", "restaurant", "food", "cafe"]:
            time_score = 5.0
            
    score += time_score

    # Limit score to maximum of 100
    return round(min(100.0, score), 2)