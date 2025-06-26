"""
Main entry point for Instagram Reels Analysis application
"""

import sys
import argparse
from gradio_interface import launch_app
from data_processing import reel_processor
from instagram_auth import instagram_auth
from config import USERNAME

def run_cli_analysis():
    """Run analysis in CLI mode (without Gradio interface)"""
    print("=== Instagram Reels Analysis - CLI Mode ===")

    # Login
    print("\nLogging in to Instagram...")
    try:
        result = instagram_auth.login()
        print(result)
    except Exception as e:
        print(f"Login failed: {e}")
        return

    # Fetch reels
    print("\nFetching reels...")
    try:
        reels = instagram_auth.fetch_explore_reels(limit=50)
        print(f"Fetched {len(reels)} reels")
    except Exception as e:
        print(f"Error fetching reels: {e}")
        return

    # Analyze reels
    print("\nPerforming comprehensive analysis...")
    try:
        analysis_results = reel_processor.comprehensive_analysis(reels, max_to_analyze=20)

        print("\n=== ANALYSIS RESULTS ===")
        print(f"Total reels analyzed: {analysis_results['total_reels_analyzed']}")

        print("\nSentiment Distribution:")
        for sentiment, count in analysis_results['sentiment_analysis']['results'].items():
            print(f"  {sentiment.title()}: {count}")

        print("\nContent Category Distribution:")
        for category, count in analysis_results['content_analysis']['results'].items():
            print(f"  {category.title()}: {count}")

        print(f"\nAnalysis completed at: {analysis_results['analysis_timestamp']}")

    except Exception as e:
        print(f"Error during analysis: {e}")

    # Logout
    instagram_auth.logout()
    print("\nLogged out successfully.")

def run_gradio_app(share=True, debug=False):
    """Run the Gradio web interface"""
    print("=== Instagram Reels Analysis - Web Interface ===")
    print("Starting Gradio web interface...")

    try:
        launch_app(share=share, debug=debug)
    except Exception as e:
        print(f"Error launching Gradio app: {e}")

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(description="Instagram Reels Analysis Tool")
    parser.add_argument(
        "--mode", 
        choices=["web", "cli"], 
        default="web",
        help="Run mode: 'web' for Gradio interface, 'cli' for command line"
    )
    parser.add_argument(
        "--no-share", 
        action="store_true",
        help="Don't create a public Gradio link (only for web mode)"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug mode"
    )

    args = parser.parse_args()

    if args.mode == "cli":
        run_cli_analysis()
    elif args.mode == "web":
        share = not args.no_share
        run_gradio_app(share=share, debug=args.debug)

if __name__ == "__main__":
    main()
