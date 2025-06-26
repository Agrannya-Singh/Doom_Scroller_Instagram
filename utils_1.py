"""
Utility functions for text processing and data manipulation
"""

import re
import emoji

def preprocess_text(text):
    """Enhanced text cleaning with multilingual support"""
    if not text:
        return ""

    # Convert emojis to text
    text = emoji.demojize(text, delimiters=(" ", " "))

    # Remove URLs and mentions
    text = re.sub(r"http\S+|@\w+", "", text)

    # Expand common abbreviations
    abbrevs = {
        r"\bomg\b": "oh my god",
        r"\btbh\b": "to be honest",
        r"\bky\b": "kyun",  # Hindi 'why'
        r"\bkb\b": "kab",   # Hindi 'when'
        r"\bkya\b": "kya",  # Hindi 'what'
        r"\bkahan\b": "kahan",  # Hindi 'where'
        r"\bkaisa\b": "kaisa"   # Hindi 'how'
    }

    for pattern, replacement in abbrevs.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def preprocess_text_cat(text):
    """Basic text cleaning for categorization"""
    if not text:
        return ""

    # Remove URLs, mentions, hashtags, and convert to lower case
    text = re.sub(r"http\S+|@\w+|#\w+", "", text).lower()

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def detect_language(text):
    """Improved language detection"""
    if re.search(r"[\u0900-\u097F]", text):  # Devanagari script
        return "hi"

    # Simple check for common Hindi/Hinglish words
    hinglish_keywords = ["hai", "kyun", "nahi", "kya", "acha", "bas", "yaar", "main"]
    if any(re.search(rf"\b{kw}\b", text.lower()) for kw in hinglish_keywords):
        return "hi-latin"

    # Fallback to English if no strong Hindi/Hinglish indicators
    return "en"

def personality_save_decision(reel, personality_profile=None):
    """
    Custom logic for INTJ-T personality based on specific traits
    """
    score = 0

    # Extract reel attributes safely
    tags = getattr(reel, 'tags', []) + getattr(reel, 'hashtags', [])
    desc = getattr(reel, 'caption_text', '') or getattr(reel, 'caption', '') or ''
    desc_lower = desc.lower()

    # HIGH INQUISITIVENESS (90) - Knowledge, learning, exploration
    intellectual_keywords = ['science', 'research', 'explained', 'how', 'why', 'theory',
                           'analysis', 'study', 'facts', 'discovery', 'experiment',
                           'psychology', 'philosophy', 'history', 'technology', 'learn', 'knowledge']
    if any(word in desc_lower for word in intellectual_keywords):
        score += 3

    # HIGH AESTHETIC APPRECIATION (97) - Visual beauty, art, design
    aesthetic_keywords = ['aesthetic', 'art', 'design', 'beautiful', 'visual',
                         'cinematography', 'photography', 'architecture', 'minimal',
                         'composition', 'color', 'artistic', 'stunning', 'view']
    if any(word in desc_lower for word in aesthetic_keywords):
        score += 3

    # HIGH AUTONOMY (97) - Independence, self-reliance, unconventional
    autonomy_keywords = ['independent', 'solo', 'self', 'individual', 'unique',
                        'unconventional', 'different', 'original', 'personal', 'alone']
    if any(word in desc_lower for word in autonomy_keywords):
        score += 2

    # HIGH CREATIVITY (83) & INNOVATION (87) - Creative content, new ideas
    creative_keywords = ['creative', 'innovative', 'invention', 'new', 'original',
                        'diy', 'build', 'create', 'design', 'craft', 'make', 'idea']
    if any(word in desc_lower for word in creative_keywords):
        score += 2

    # HIGH INTELLECTUAL EFFICIENCY (67) - Concise, efficient information
    length = getattr(reel, 'video_duration', 0)
    if 10 <= length <= 60:  # Preference for medium-length content
        score += 1
    elif length > 120:  # Penalize very long content
        score -= 1

    # DEDUCT for LOW SOCIABILITY (3-7) - Avoid highly social content
    social_keywords = ['party', 'friends', 'group', 'social', 'together', 'crowd',
                      'everyone', 'people', 'community', 'team', 'vlog', 'challenge']
    if any(word in desc_lower for word in social_keywords):
        score -= 2

    # DEDUCT for LOW AFFILIATION (13) - Avoid relationship/emotional content
    emotional_keywords = ['relationship', 'love', 'heart', 'feelings', 'emotional',
                         'together', 'couple', 'romantic', 'cute', 'sweet', 'sad', 'happy', 'feel']
    if any(word in desc_lower for word in emotional_keywords):
        score -= 2

    # BONUS for complexity and depth
    complex_keywords = ['complex', 'deep', 'detailed', 'comprehensive', 'advanced',
                       'expert', 'professional', 'technical', 'analysis', 'explained', 'theory']
    if any(word in desc_lower for word in complex_keywords):
        score += 1

    # BONUS for educational/tutorial content
    educational_keywords = ['tutorial', 'learn', 'guide', 'tip', 'hack', 'skill',
                           'knowledge', 'education', 'teach', 'lesson', 'how-to']
    if any(word in desc_lower for word in educational_keywords):
        score += 2

    # Check for negative sentiment keywords
    negative_keywords = ["hate", "worst", "bad", "terrible", "awful", "cringe"]
    if any(word in desc_lower for word in negative_keywords):
        score -= 3

    return score
