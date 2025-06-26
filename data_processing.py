"""
Data processing operations for Instagram reels
"""

import time
import random
from collections import Counter
from instagram_auth import instagram_auth
from sentiment_analysis import ReelSentimentAnalyzer
from content_analysis import content_analyzer
from utils import personality_save_decision

class ReelProcessor:
    def __init__(self):
        self.sentiment_analyzer = None
        self.content_analyzer = content_analyzer
        self.processed_reels = []

    def initialize_sentiment_analyzer(self):
        """Initialize sentiment analyzer if not already done"""
        if self.sentiment_analyzer is None:
            try:
                self.sentiment_analyzer = ReelSentimentAnalyzer()
                print("Sentiment analyzer initialized in ReelProcessor.")
            except Exception as e:
                print(f"Error initializing sentiment analyzer: {e}")
                return False
        return True

    def fetch_and_filter_reels(self, target_count=100, min_saves=7, max_saves=15):
        """
        Fetch reels and filter them based on personality scoring

        Args:
            target_count: Number of reels to process for filtering
            min_saves: Minimum number of reels to save
            max_saves: Maximum number of reels to save

        Returns:
            tuple: (selected_reels, all_fetched_reels, processing_summary)
        """
        if not instagram_auth.is_logged_in:
            raise Exception("Not logged in to Instagram")

        # Fetch reels
        try:
            all_reels = instagram_auth.fetch_explore_reels(limit=target_count)
            print(f"Fetched {len(all_reels)} reels for processing")
        except Exception as e:
            raise Exception(f"Error fetching reels: {e}")

        if not all_reels:
            return [], [], "No reels fetched"

        # Score reels based on personality preferences
        candidate_reels = []
        for i, reel in enumerate(all_reels[:target_count], 1):
            score = personality_save_decision(reel)
            candidate_reels.append((reel, score))
            print(f"Scored reel {i}/{min(target_count, len(all_reels))} (ID: {reel.id}): {score}")

        # Sort by score (highest first)
        candidate_reels.sort(key=lambda x: x[1], reverse=True)

        # Select top reels within the min_saves to max_saves range
        positive_scoring_reels = [(r, s) for r, s in candidate_reels if s > 0]
        num_to_save = min(max_saves, max(min_saves, len(positive_scoring_reels)))

        if len(positive_scoring_reels) < min_saves:
            selected_reels = [r for r, s in candidate_reels[:min_saves]]
            summary = f"Selected {min_saves} reels (not enough positive-scoring reels)"
        else:
            selected_reels = [r for r, s in positive_scoring_reels[:num_to_save]]
            summary = f"Selected {len(selected_reels)} reels based on personality match"

        return selected_reels, all_reels, summary

    def batch_analyze_sentiment(self, reels, max_to_analyze=100):
        """
        Perform batch sentiment analysis on reels

        Args:
            reels: List of reel objects
            max_to_analyze: Maximum number of reels to analyze

        Returns:
            tuple: (sentiment_results_counter, detailed_results_list)
        """
        if not self.initialize_sentiment_analyzer():
            raise Exception("Failed to initialize sentiment analyzer")

        print(f"Starting batch sentiment analysis for {min(len(reels), max_to_analyze)} reels...")

        results = Counter()
        detailed_results = []

        for i, reel in enumerate(reels[:max_to_analyze], 1):
            caption = getattr(reel, 'caption_text', '') or getattr(reel, 'caption', '') or ''

            try:
                label, confidence, details = self.sentiment_analyzer.analyze_content(caption)
                results[label] += 1

                detailed_results.append({
                    "reel_id": reel.id,
                    "text": caption[:100] + "..." if len(caption) > 100 else caption,
                    "label": label,
                    "confidence": confidence,
                    "details": details
                })

                print(f"Analyzed reel {i}/{min(len(reels), max_to_analyze)}: {label} ({confidence:.2f})")

            except Exception as e:
                print(f"Error analyzing reel {reel.id}: {e}")
                results["error"] += 1
                detailed_results.append({
                    "reel_id": reel.id,
                    "text": caption[:100] + "..." if len(caption) > 100 else caption,
                    "label": "error",
                    "confidence": 0.0,
                    "details": {"error": str(e)}
                })

        print("Batch sentiment analysis completed.")
        return results, detailed_results

    def batch_analyze_content(self, reels, max_to_analyze=100):
        """
        Perform batch content analysis on reels

        Args:
            reels: List of reel objects
            max_to_analyze: Maximum number of reels to analyze

        Returns:
            tuple: (category_counts_counter, detailed_results_list)
        """
        print(f"Starting batch content analysis for {min(len(reels), max_to_analyze)} reels...")

        category_counts = Counter()
        detailed_results = []

        for i, reel in enumerate(reels[:max_to_analyze], 1):
            caption = getattr(reel, 'caption_text', '') or getattr(reel, 'caption', '') or ''

            try:
                category, details = self.content_analyzer.classify_content(caption)
                category_counts[category] += 1

                detailed_results.append({
                    "reel_id": reel.id,
                    "text": caption[:100] + "..." if len(caption) > 100 else caption,
                    "category": category,
                    "details": details
                })

                print(f"Classified reel {i}/{min(len(reels), max_to_analyze)}: {category}")

            except Exception as e:
                print(f"Error classifying reel {reel.id}: {e}")
                category_counts["error"] += 1
                detailed_results.append({
                    "reel_id": reel.id,
                    "text": caption[:100] + "..." if len(caption) > 100 else caption,
                    "category": "error",
                    "details": {"error": str(e)}
                })

        print("Batch content analysis completed.")
        return category_counts, detailed_results

    def comprehensive_analysis(self, reels, max_to_analyze=100):
        """
        Perform both sentiment and content analysis on reels

        Args:
            reels: List of reel objects
            max_to_analyze: Maximum number of reels to analyze

        Returns:
            dict: Combined analysis results
        """
        print(f"Starting comprehensive analysis for {min(len(reels), max_to_analyze)} reels...")

        # Sentiment analysis
        sentiment_results, sentiment_details = self.batch_analyze_sentiment(reels, max_to_analyze)

        # Content analysis
        content_results, content_details = self.batch_analyze_content(reels, max_to_analyze)

        # Combine results
        analysis_summary = {
            "total_reels_analyzed": min(len(reels), max_to_analyze),
            "sentiment_analysis": {
                "results": dict(sentiment_results),
                "details": sentiment_details
            },
            "content_analysis": {
                "results": dict(content_results),
                "details": content_details
            },
            "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        print("Comprehensive analysis completed.")
        return analysis_summary

    def save_selected_reels_to_collection(self, reels, collection_name="Collab Reels"):
        """
        Save selected reels to Instagram collection

        Args:
            reels: List of reel objects to save
            collection_name: Name of the collection to save to

        Returns:
            str: Summary of save operation
        """
        if not instagram_auth.is_logged_in:
            return "Error: Not logged in to Instagram"

        try:
            result = instagram_auth.save_reels_to_collection(reels)
            return result
        except Exception as e:
            return f"Error saving reels to collection: {e}"

# Global instance for use across the application
reel_processor = ReelProcessor()
