"""
Configuration settings for Instagram Reels Analysis
"""

import os
import torch
from typing import Dict, Any, List, Set, Optional
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'app.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Custom exception for configuration errors"""
    pass

def get_env_variable(name: str, default: Any = None, required: bool = False) -> str:
    """Get environment variable with error handling"""
    value = os.getenv(name, default)
    if required and value is None:
        raise ConfigError(f"Required environment variable {name} is not set")
    return value

# Model Configuration
CONFIG: Dict[str, Any] = {
    "max_length": 128,
    "batch_size": 16,
    "learning_rate": 2e-5,
    "num_train_epochs": 3,
    "few_shot_examples": 5,  # per class
    "confidence_threshold": float(get_env_variable('SENTIMENT_THRESHOLD', '0.7')),
    "neutral_reanalysis_threshold": float(get_env_variable('NEUTRAL_THRESHOLD', '0.33'))
}

# Instagram Settings
USERNAME: str = get_env_variable('INSTAGRAM_USERNAME', required=True)
PASSWORD: str = get_env_variable('INSTAGRAM_PASSWORD', required=True)
TARGET_REELS_COUNT: int = int(get_env_variable('TARGET_REELS_COUNT', '50'))
MIN_SAVES: int = int(get_env_variable('MIN_SAVES', '5'))
MAX_SAVES: int = int(get_env_variable('MAX_SAVES', '15'))
COLLECTION_NAME: str = get_env_variable('COLLECTION_NAME', 'Saved Reels')

# Optional Proxy Settings
PROXY: Optional[str] = get_env_variable('INSTAGRAM_PROXY')

# Two-Factor Authentication
ENABLE_2FA: bool = get_env_variable('ENABLE_2FA', 'false').lower() == 'true'
TRUSTED_DEVICE_NAME: str = get_env_variable('TRUSTED_DEVICE_NAME', 'My Device')

# Content Categories
CONTENT_CATEGORIES: List[str] = [
    "news", "meme", "sports", "science", "music", "movie",
    "gym", "comedy", "food", "technology", "travel", "fashion", "art", "business"
]

# Category Keywords
CATEGORY_KEYWORDS: Dict[str, Set[str]] = {
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
DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"

# Log configuration
logger.info(f"Configuration loaded for user: {USERNAME}")
logger.info(f"Using device: {DEVICE}")
logger.info(f"Target reels count: {TARGET_REELS_COUNT}")

# Validate configuration
if MIN_SAVES > MAX_SAVES:
    error_msg = f"MIN_SAVES ({MIN_SAVES}) cannot be greater than MAX_SAVES ({MAX_SAVES})"
    logger.error(error_msg)
    raise ConfigError(error_msg)

# Neutral Keywords
NEUTRAL_KEYWORDS = {
    "ad", "sponsored", "promo", "sale", "discount", "offer", "giveaway",
    "buy", "shop", "link in bio",
    "विज्ञापन", "प्रचार", "ऑफर", "डिस्काउंट", "बिक्री", "लिंक बायो में"
}
