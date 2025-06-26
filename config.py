"""
Configuration settings for Instagram Reels Analysis
"""

import torch

# Model Configuration
CONFIG = {
    "max_length": 128,
    "batch_size": 16,
    "learning_rate": 2e-5,
    "num_train_epochs": 3,
    "few_shot_examples": 5,  # per class
    "confidence_threshold": 0.7,
    "neutral_reanalysis_threshold": 0.33
}

# Instagram Settings
USERNAME = "jattman1993"  # Replace with your preset username
TARGET_REELS_COUNT = 100  # Process up to this many reels
MIN_SAVES = 7
MAX_SAVES = 15
COLLECTION_NAME = "Collab Reels"

# Content Categories
CONTENT_CATEGORIES = [
    "news", "meme", "sports", "science", "music", "movie",
    "gym", "comedy", "food", "technology", "travel", "fashion", "art", "business"
]

# Category Keywords
CATEGORY_KEYWORDS = {
    "news": {"news", "update", "breaking", "reported", "headlines"},
    "meme": {"meme", "funny", "lol", "haha", "relatable"},
    "sports": {"sports", "cricket", "football", "match", "game", "team", "score"},
    "science": {"science", "research", "discovery", "experiment", "facts", "theory"},
    "music": {"music", "song", "album", "release", "artist", "beats"},
    "movie": {"movie", "film", "bollywood", "trailer", "series", "actor"},
    "gym": {"gym", "workout", "fitness", "exercise", "training", "bodybuilding"},
    "comedy": {"comedy", "joke", "humor", "standup", "skit", "laugh"},
    "food": {"food", "recipe", "cooking", "eat", "delicious", "restaurant", "kitchen"},
    "technology": {"tech", "phone", "computer", "ai", "gadget", "software", "innovation"},
    "travel": {"travel", "trip", "vacation", "explore", "destination", "adventure"},
    "fashion": {"fashion", "style", "ootd", "outfit", "trends", "clothing"},
    "art": {"art", "artist", "painting", "drawing", "creative", "design"},
    "business": {"business", "startup", "marketing", "money", "finance", "entrepreneur"}
}

# Device Configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Neutral Keywords
NEUTRAL_KEYWORDS = {
    "ad", "sponsored", "promo", "sale", "discount", "offer", "giveaway",
    "buy", "shop", "link in bio",
    "विज्ञापन", "प्रचार", "ऑफर", "डिस्काउंट", "बिक्री", "लिंक बायो में"
}
