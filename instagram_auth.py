"""
Instagram authentication and session management
"""

import os
import time
import random
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired,
    ClientError,
    ChallengeRequired,
    TwoFactorRequired,
    SelectContactPointRecoveryForm,
    RecaptchaChallengeForm,
    FeedbackRequired,
    PleaseWaitFewMinutes
)

from config import (
    USERNAME, PASSWORD, PROXY, 
    ENABLE_2FA, TRUSTED_DEVICE_NAME,
    ConfigError
)
from utils import personality_save_decision

logger = logging.getLogger(__name__)

class InstagramAuth:
    """Handles Instagram authentication and session management"""
    
    SESSION_FILE = 'session.json'
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.is_logged_in: bool = False
        self._session_loaded: bool = False
        self._session_file = Path(self.SESSION_FILE)

    def _setup_client(self) -> None:
        """Initialize the Instagram client with proper settings"""
        self.client = Client()
        
        # Configure proxy if provided
        if PROXY:
            self.client.set_proxy(PROXY)
            logger.info(f"Using proxy: {PROXY}")
            
        # Set up device settings to mimic a real device
        self.client.set_locale('en_US')
        self.client.set_timezone_offset(5.5 * 60 * 60)  # IST
        self.client.set_uuids({
            'phone_id': str(uuid.uuid4()),
            'uuid': str(uuid.uuid4()),
            'client_session_id': str(uuid.uuid4()),
            'advertising_id': str(uuid.uuid4()),
        })
        
        # Load session if exists
        self._load_session()

    def _load_session(self) -> bool:
        """Load session from file if it exists"""
        if self._session_file.exists():
            try:
                self.client.load_settings(self._session_file)
                self._session_loaded = True
                logger.info("Session loaded from file")
                return True
            except Exception as e:
                logger.warning(f"Failed to load session: {e}")
                self._session_loaded = False
        return False

    def _save_session(self) -> None:
        """Save the current session to file"""
        if not self.client:
            return
            
        try:
            session = self.client.get_settings()
            with open(self._session_file, 'w') as f:
                json.dump(session, f, indent=2)
            logger.debug("Session saved to file")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")

    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> str:
        """
        Login to Instagram using credentials or session
        
        Args:
            username: Instagram username (optional, uses config if not provided)
            password: Instagram password (optional, uses config if not provided)
            
        Returns:
            str: Status message
            
        Raises:
            ConfigError: If required credentials are missing
            ClientError: If login fails
        """
        username = username or USERNAME
        password = password or PASSWORD
        
        if not username or not password:
            raise ConfigError("Instagram username and password are required")
            
        self._setup_client()
        
        try:
            # Try to resume session if available
            if self._session_loaded:
                try:
                    self.client.get_timeline_feed()
                    self.is_logged_in = True
                    logger.info(f"Resumed session for {username}")
                    return f"Resumed session for {username}"
                except (LoginRequired, ClientError):
                    logger.info("Session expired, logging in with credentials")
            
            # Perform fresh login
            login_result = self.client.login(username, password)
            
            if login_result:
                self.is_logged_in = True
                self._save_session()
                logger.info(f"Successfully logged in as {username}")
                return f"Successfully logged in as {username}"
            else:
                raise ClientError("Login failed: Unknown error")
                
        except TwoFactorRequired:
            logger.info("Two-factor authentication required")
            if ENABLE_2FA:
                return "2FA required"
            raise ConfigError("Two-factor authentication is required but not enabled in config")
            
        except ChallengeRequired as e:
            logger.warning(f"Challenge required: {e}")
            return self._handle_challenge()
            
        except Exception as e:
            self.is_logged_in = False
            logger.error(f"Login failed: {str(e)}")
            raise ClientError(f"Login failed: {str(e)}")

    def _handle_challenge(self) -> str:
        """Handle Instagram's challenge process"""
        if not self.client:
            raise ClientError("Client not initialized")
            
        try:
            challenge_info = self.client.last_json.get('challenge', {})
            challenge_url = challenge_info.get('api_path', '').lstrip('/')
            
            if not challenge_url:
                raise ClientError("Challenge URL not found")
                
            # Handle different types of challenges
            if 'select_verify_method' in challenge_url:
                # User needs to select a verification method
                self.client.select_verify_method(challenge_url, '0')  # Default to first method
                return "Verification method selected"
                
            elif 'send_verify_code' in challenge_url:
                # Resend verification code
                self.client.send_verify_code(challenge_url, TRUSTED_DEVICE_NAME)
                return "Verification code sent"
                
            return "Challenge response handled"
            
        except Exception as e:
            logger.error(f"Challenge handling failed: {e}")
            raise ClientError(f"Challenge handling failed: {e}")

    def handle_two_factor(self, otp_code: str) -> str:
        """
        Handle two-factor authentication
        
        Args:
            otp_code: The one-time password from the authenticator app
            
        Returns:
            str: Status message
            
        Raises:
            ClientError: If 2FA fails
        """
        if not self.client:
            raise ClientError("Client not initialized")
            
        if not otp_code or not otp_code.isdigit() or len(otp_code) != 6:
            raise ClientError("Invalid OTP code. Please enter a 6-digit number.")
            
        try:
            self.client.two_factor_login(otp_code)
            self.is_logged_in = True
            self._save_session()
            logger.info("2FA successful")
            return "Successfully logged in with 2FA"
            
        except Exception as e:
            logger.error(f"2FA failed: {e}")
            raise ClientError(f"2FA failed: {e}")
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
