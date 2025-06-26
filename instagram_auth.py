"""
Instagram authentication and session management
"""

import time
import random
from instagrapi import Client
from google.colab import userdata
from config import USERNAME, COLLECTION_NAME, MIN_SAVES, MAX_SAVES
from utils import personality_save_decision

class InstagramAuth:
    def __init__(self):
        self.client = None
        self.is_logged_in = False

    def login(self, username=None, password=None):
        """Login to Instagram using credentials"""
        if username is None:
            username = USERNAME

        if password is None:
            try:
                password = userdata.get('password')
            except Exception as e:
                raise Exception(f"Error accessing password secret: {e}")

        if not password:
            raise Exception("Instagram password not found in Colab secrets")

        self.client = Client()

        try:
            self.client.login(username, password)
            self.is_logged_in = True
            return f"Successfully logged in as {username}"
        except Exception as e:
            self.client = None
            self.is_logged_in = False
            raise Exception(f"Error during login: {e}")

    def handle_two_factor(self, otp_code):
        """Handle two-factor authentication"""
        if not self.client:
            raise Exception("Client not initialized")

        try:
            self.client.two_factor_login(otp_code)
            self.is_logged_in = True
            return f"OTP successful. Successfully logged in as {USERNAME}"
        except Exception as e:
            raise Exception(f"OTP submission failed: {e}")

    def fetch_explore_reels(self, limit=100):
        """Fetch explore reels from Instagram"""
        if not self.is_logged_in or not self.client:
            raise Exception("Not logged in")

        try:
            reels = self.client.explore_reels()[:limit]
            return reels
        except Exception as e:
            raise Exception(f"Error fetching explore reels: {e}")

    def save_reels_to_collection(self, reels, target_count=100):
        """Save selected reels to collection based on personality scoring"""
        if not self.is_logged_in or not self.client:
            raise Exception("Not logged in")

        saved_reels = []
        processed_reels = 0
        candidate_reels = []

        # First pass: Score reels
        for reel in reels[:target_count]:
            processed_reels += 1
            score = personality_save_decision(reel)
            candidate_reels.append((reel, score))

        # Sort by score (highest first)
        candidate_reels.sort(key=lambda x: x[1], reverse=True)

        # Select top reels within MIN_SAVES to MAX_SAVES range
        positive_scoring_reels = [(r, s) for r, s in candidate_reels if s > 0]
        num_to_save = min(MAX_SAVES, max(MIN_SAVES, len(positive_scoring_reels)))

        if len(positive_scoring_reels) < MIN_SAVES:
            selected_reels = candidate_reels[:MIN_SAVES]
        else:
            selected_reels = positive_scoring_reels[:num_to_save]

        # Save to collection
        try:
            collections = self.client.collections()
            collab_collection = next((c for c in collections if c.name == COLLECTION_NAME), None)

            if not collab_collection:
                return f"Collection '{COLLECTION_NAME}' not found. Please create it manually."

            for i, (reel, score) in enumerate(selected_reels, 1):
                try:
                    self.client.media_save(media_id=reel.id, collection_ids=[collab_collection.id])
                    saved_reels.append(reel.id)
                    time.sleep(random.uniform(1, 2))  # Human-like delay
                except Exception as save_error:
                    print(f"Could not save reel {reel.id}: {save_error}")
                    time.sleep(random.uniform(5, 10))

            return f"Saved {len(saved_reels)} reels to '{COLLECTION_NAME}'"

        except Exception as e:
            return f"Error during collection management: {e}"

    def logout(self):
        """Logout from Instagram"""
        if self.client:
            try:
                self.client.logout()
            except:
                pass
        self.client = None
        self.is_logged_in = False

# Global instance for use across the application
instagram_auth = InstagramAuth()
