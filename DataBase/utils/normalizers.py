def normalize_to_percentage(value, min_val, max_val):
    """Normalize value to 0-100 scale"""
    if max_val == min_val:
        return 50.0
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    return round(max(0, min(100, normalized)), 1)

def inverse_normalize(value, min_val, max_val):
    """Inverse normalization (higher value = lower percentage, for crime)"""
    if max_val == min_val:
        return 50.0
    normalized = ((max_val - value) / (max_val - min_val)) * 100
    return round(max(0, min(100, normalized)), 1)

def calculate_density_score(count, max_count):
    """Calculate density as percentage"""
    if max_count == 0:
        return 0.0
    return round((count / max_count) * 100, 1)

def price_to_scale(price_str):
    """Convert Yelp price string to numeric scale"""
    price_map = {'$': 1, '$$': 2, '$$$': 3, '$$$$': 4}
    return price_map.get(price_str, 2)