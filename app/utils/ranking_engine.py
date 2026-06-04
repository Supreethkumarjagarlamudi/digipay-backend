from datetime import datetime

def calculate_rank_score(

    distance,

    customer_heading,

    merchant_heading,

    customer_speed,

    category

):

    score = 0

    # DISTANCE (40%)

    if distance < 0.1:

        score += 40

    elif distance < 0.5:

        score += 30

    elif distance < 1:

        score += 20

    else:

        score += 10

    # DIRECTION (20%)

    heading_difference = abs(

        customer_heading -

        merchant_heading

    )

    direction_score = max(
        0,
        20 - (
            heading_difference / 18
        )
    )

    score += direction_score

    # SPEED CONTEXT (15%)

    if customer_speed < 2:

        if category in [

            "Cafe",
            "Restaurant",
            "Medical"

        ]:

            score += 15

    else:

        if category in [

            "Medical",
            "Grocery",
            "Electronics"

        ]:

            score += 15

    # TIME CONTEXT (15%)

    hour = datetime.now().hour

    if 6 <= hour <= 11:

        if category in [

            "Cafe",
            "Restaurant"

        ]:

            score += 15

    elif 12 <= hour <= 16:

        if category == "Restaurant":

            score += 15

    elif hour >= 20:

        if category in [

            "Medical",
            "Restaurant"

        ]:

            score += 15

    # CATEGORY BONUS (10%)

    if category in [

        "Restaurant",
        "Cafe",
        "Medical"

    ]:

        score += 10

    return round(score, 2)