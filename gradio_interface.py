"""
Gradio web interface for Instagram Reels Analysis
"""

import gradio as gr
from collections import Counter

from instagram_auth import instagram_auth
from sentiment_analysis import ReelSentimentAnalyzer
from content_analysis import content_analyzer
from visualization import plot_sentiment_pie, plot_category_distribution
from config import USERNAME

class GradioInterface:
    def __init__(self):
        self.sentiment_analyzer = None
        self.explore_reels_list = []
        self._initialize_analyzers()

    def _initialize_analyzers(self):
        """Initialize the sentiment analyzer"""
        try:
            self.sentiment_analyzer = ReelSentimentAnalyzer()
            print("Sentiment Analyzer initialized for Gradio interface.")
        except Exception as e:
            print(f"Error initializing Sentiment Analyzer: {e}")
            self.sentiment_analyzer = None

    def login_auto(self):
        """Automatic login function for Gradio"""
        try:
            result = instagram_auth.login()
            return result, gr.update(visible=False)  # Hide OTP input on success
        except Exception as e:
            error_message = str(e)
            if "Two factor challenged" in error_message or "challenge_required" in error_message:
                return f"Login failed: Two-factor authentication required. Please enter the code below.", gr.update(visible=True)
            else:
                return f"Error during login: {error_message}", gr.update(visible=False)

    def submit_otp(self, otp_code):
        """Handle OTP submission"""
        try:
            result = instagram_auth.handle_two_factor(otp_code)
            return result, "", gr.update(visible=False)  # Clear OTP input and hide field
        except Exception as e:
            return f"OTP submission failed: {e}. Please try again.", "", gr.update(visible=True)

    def fetch_reels(self):
        """Fetch explore reels"""
        try:
            self.explore_reels_list = instagram_auth.fetch_explore_reels(limit=100)
            return f"Successfully fetched {len(self.explore_reels_list)} explore reels."
        except Exception as e:
            self.explore_reels_list = []
            return f"Error fetching reels: {e}"

    def analyze_reels(self, max_to_analyze):
        """Analyze fetched reels and generate plots"""
        if not self.explore_reels_list:
            return "Error: No reels fetched yet. Please fetch reels first.", None, None

        # Ensure max_to_analyze does not exceed the number of fetched reels
        num_reels_to_process = min(max_to_analyze, len(self.explore_reels_list))
        reels_to_analyze = self.explore_reels_list[:num_reels_to_process]

        if not reels_to_analyze:
            return "Error: No reels available to analyze.", None, None

        # Check if analyzers are initialized
        if self.sentiment_analyzer is None:
            return "Error: Sentiment Analyzer not initialized.", None, None

        if content_analyzer.classifier is None:
            return "Error: Content Classifier not initialized.", None, None

        analysis_status_messages = []
        sentiment_plot_figure = None
        content_plot_figure = None

        # Perform Sentiment Analysis
        try:
            analysis_status_messages.append(f"Starting Sentiment Analysis for {len(reels_to_analyze)} reels...")
            sentiment_results, detailed_sentiment_results = self.sentiment_analyzer.analyze_reels(
                reels_to_analyze,
                max_to_analyze=len(reels_to_analyze)
            )

            sentiment_plot_figure = plot_sentiment_pie(
                sentiment_results, 
                title=f"Sentiment of {len(reels_to_analyze)} Instagram Reels"
            )
            analysis_status_messages.append("Sentiment Analysis Complete.")
        except Exception as e:
            analysis_status_messages.append(f"Error during Sentiment Analysis: {e}")
            sentiment_plot_figure = None

        # Perform Content Categorization
        try:
            analysis_status_messages.append(f"Starting Content Categorization for {len(reels_to_analyze)} reels...")
            category_counts, detailed_content_categories = content_analyzer.analyze_reels_content(
                reels_to_analyze,
                max_to_analyze=len(reels_to_analyze)
            )

            content_plot_figure = plot_category_distribution(category_counts)
            analysis_status_messages.append("Content Categorization Complete.")
        except Exception as e:
            analysis_status_messages.append(f"Error during Content Analysis: {e}")
            content_plot_figure = None

        final_status_message = "\n".join(analysis_status_messages)
        return final_status_message, sentiment_plot_figure, content_plot_figure

    def create_interface(self):
        """Create and return the Gradio interface"""
        with gr.Blocks(title="Instagram Reels Analysis") as demo:
            gr.Markdown("# Instagram Reels Analysis")
            gr.Markdown("Analyze sentiment and content categories of Instagram explore reels using AI models.")

            # Login Section
            with gr.Row():
                connect_button = gr.Button("Connect Instagram", variant="primary")
                login_status_output = gr.Label(label="Login Status")

            # OTP Input (initially hidden)
            with gr.Row(visible=False) as otp_row:
                otp_input = gr.Textbox(label="Enter OTP Code", placeholder="123456")
                otp_submit_button = gr.Button("Submit OTP")

            # Fetch Reels Section
            with gr.Row():
                fetch_button = gr.Button("Fetch Reels", variant="secondary")
                fetch_status_output = gr.Label(label="Fetch Status")

            # Analysis Configuration
            with gr.Row():
                max_reels_input = gr.Slider(
                    minimum=1, maximum=100, value=10, step=1,
                    label="Number of Reels to Analyze"
                )
                analyze_button = gr.Button("Analyze Reels", variant="primary")

            analyze_status_output = gr.Label(label="Analysis Status")

            # Results Section
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## Sentiment Analysis")
                    sentiment_plot_output = gr.Plot(label="Sentiment Distribution")

                with gr.Column():
                    gr.Markdown("## Content Analysis")
                    content_plot_output = gr.Plot(label="Content Distribution")

            # Event handlers
            connect_button.click(
                fn=self.login_auto,
                inputs=None,
                outputs=[login_status_output, otp_row]
            )

            otp_submit_button.click(
                fn=self.submit_otp,
                inputs=otp_input,
                outputs=[login_status_output, otp_input, otp_row]
            )

            fetch_button.click(
                fn=self.fetch_reels,
                inputs=None,
                outputs=fetch_status_output
            )

            analyze_button.click(
                fn=self.analyze_reels,
                inputs=max_reels_input,
                outputs=[analyze_status_output, sentiment_plot_output, content_plot_output]
            )

        return demo

def launch_app(share=True, debug=False):
    """Launch the Gradio application"""
    interface = GradioInterface()
    demo = interface.create_interface()
    demo.launch(share=share, debug=debug)

if __name__ == "__main__":
    launch_app()
