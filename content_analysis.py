"""
Content classification for Instagram reels using zero-shot classification
"""

import re
from transformers import pipeline
from collections import Counter
import torch

from config import CONTENT_CATEGORIES, CATEGORY_KEYWORDS, DEVICE
from utils import preprocess_text_cat

class ContentAnalyzer:
    def __init__(self):
        self.classifier = None
        self._initialize_classifier()

    def _initialize_classifier(self):
        """Initialize the zero-shot classification pipeline"""
        print("\nLoading Zero-shot Classification Model for Content Categorization...")
        try:
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
            print("Content Classifier Pipeline Initialized.")
        except Exception as e:
            print(f"Error initializing Content Classifier: {e}")
            self.classifier = None

    def classify_content(self, text):
        """Classify content using keywords and zero-shot model"""
        processed = preprocess_text_cat(text)

        if not processed or len(processed.split()) < 2:
            return "other", {"reason": "short_text"}

        # 1. Keyword matching (fastest)
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(re.search(rf"\b{re.escape(keyword)}\b", processed) for keyword in keywords):
                return category, {"reason": "keyword_match"}

        # 2. Model classification (more robust)
        model_text = processed[:256]  # Process first 256 characters

        if self.classifier is None:
            print("Content classifier pipeline not initialized.")
            return "other", {"reason": "classifier_not_initialized"}

        try:
            result = self.classifier(model_text, CONTENT_CATEGORIES, multi_label=False)
            top_label = result['labels'][0]
            top_score = result['scores'][0]

            if top_score > 0.5:  # Confidence threshold
                return top_label, {"reason": "model_prediction", "score": top_score}
            else:
                return "other", {"reason": "low_model_confidence", "score": top_score}

        except Exception as e:
            print(f"Error during zero-shot classification for text '{model_text}...': {e}")
            return "other", {"reason": "classification_error"}

    def analyze_reels_content(self, reels, max_to_analyze=100):
        """Complete content analysis"""
        print(f"\n--- Starting Content Categorization ({max_to_analyze} reels) ---")

        category_counts = Counter()
        detailed_categories = []

        reels_to_analyze = reels[:max_to_analyze]
        print(f"⏳ Analyzing content for {len(reels_to_analyze)} reels...")

        for i, reel in enumerate(reels_to_analyze, 1):
            caption = getattr(reel, 'caption_text', '') or getattr(reel, 'caption', '') or ''
            print(f"Classifying content for reel {i}/{len(reels_to_analyze)} (ID: {reel.id})...")

            category, details = self.classify_content(caption)
            category_counts[category] += 1

            detailed_categories.append({
                "reel_id": reel.id,
                "text": caption,
                "category": category,
                "details": details
            })

        print("\n✅ Content Analysis complete!")
        print("\n📊 Category Counts:")
        for category, count in category_counts.most_common():
            print(f"- {category.replace('_', ' ').title()}: {count}")

        return category_counts, detailed_categories

# Global instance for use across the application
content_analyzer = ContentAnalyzer()
