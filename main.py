"""
Main entry point for Instagram Reels Analysis application
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, Optional, List

# Configure logging before importing other modules
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'app.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Import after configuring logging
from gradio_interface import launch_app
from data_processing import reel_processor
from instagram_auth import InstagramAuth
from config import (
    USERNAME, TARGET_REELS_COUNT, MIN_SAVES, MAX_SAVES,
    COLLECTION_NAME, CONTENT_CATEGORIES, CONFIG, ConfigError
)

# Initialize Instagram auth
instagram_auth = InstagramAuth()

def run_cli_analysis() -> None:
    """Run analysis in CLI mode (without Gradio interface)"""
    from rich.console import Console
    from rich.table import Table
    from rich.progress import track
    
    console = Console()
    console.print("\n[bold blue]=== Instagram Reels Analysis - CLI Mode ===[/bold blue]\n")

    try:
        # Login
        with console.status("[bold green]Logging in to Instagram..."):
            try:
                result = instagram_auth.login()
                console.print(f"[green]✓ {result}[/green]")
            except Exception as e:
                console.print(f"[red]✗ Login failed: {e}[/red]")
                if "2FA" in str(e):
                    otp = console.input("Enter 6-digit 2FA code: ").strip()
                    try:
                        result = instagram_auth.handle_two_factor(otp)
                        console.print(f"[green]✓ {result}[/green]")
                    except Exception as two_fa_error:
                        console.print(f"[red]✗ 2FA failed: {two_fa_error}[/red]")
                        return
                else:
                    return

        # Fetch reels
        with console.status("[bold green]Fetching reels..."):
            try:
                reels = instagram_auth.fetch_explore_reels(limit=TARGET_REELS_COUNT)
                if not reels:
                    console.print("[yellow]No reels found. Please try again later.[/yellow]")
                    return
                console.print(f"[green]✓ Fetched {len(reels)} reels[/green]")
            except Exception as e:
                console.print(f"[red]✗ Error fetching reels: {e}[/red]")
                return

        # Analyze reels
        console.print("\n[bold]Performing comprehensive analysis...[/bold]")
        try:
            analysis_results = reel_processor.comprehensive_analysis(
                reels,
                max_to_analyze=min(20, len(reels)),
                config=CONFIG
            )

            # Display results in a table
            table = Table(title="\nAnalysis Results", show_header=True, header_style="bold magenta")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Total Reels Analyzed", str(analysis_results['total_reels_analyzed']))
            table.add_row("Analysis Timestamp", analysis_results['analysis_timestamp'])
            
            # Add sentiment distribution
            sentiment_row = "\n".join(
                f"{sentiment.title()}: {count}" 
                for sentiment, count in analysis_results['sentiment_analysis']['results'].items()
            )
            table.add_row("Sentiment Distribution", sentiment_row)
            
            # Add content categories
            categories_row = "\n".join(
                f"{category.title()}: {count}" 
                for category, count in analysis_results['content_analysis']['results'].items()
            )
            table.add_row("Content Categories", categories_row)
            
            console.print(table)

        except Exception as e:
            logger.exception("Error during analysis")
            console.print(f"[red]✗ Error during analysis: {e}[/red]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
    except Exception as e:
        logger.exception("Unexpected error in CLI mode")
        console.print(f"[red]✗ An unexpected error occurred: {e}[/red]")
    finally:
        # Logout
        try:
            if instagram_auth.is_logged_in:
                instagram_auth.logout()
                console.print("\n[green]✓ Successfully logged out.[/green]")
        except Exception as e:
            logger.warning(f"Error during logout: {e}")

def run_gradio_app(share: bool = True, debug: bool = False) -> None:
    """Run the Gradio web interface"""
    logger.info("Starting Gradio web interface...")
    try:
        launch_app(
            share=share,
            debug=debug,
            auth=instagram_auth,
            config={
                'target_reels': TARGET_REELS_COUNT,
                'min_saves': MIN_SAVES,
                'max_saves': MAX_SAVES,
                'collection_name': COLLECTION_NAME,
                'content_categories': CONTENT_CATEGORIES
            }
        )
    except Exception as e:
        logger.exception("Error in Gradio app")
        print(f"Error launching Gradio app: {e}")
        sys.exit(1)

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
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
        help="Enable debug mode (more verbose output)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level"
    )
    return parser.parse_args()

def main() -> None:
    """Main function with command line argument parsing and initialization"""
    try:
        args = parse_arguments()
        
        # Update log level based on command line
        logging.getLogger().setLevel(args.log_level)
        
        if args.mode == "cli":
            run_cli_analysis()
        elif args.mode == "web":
            run_gradio_app(share=not args.no_share, debug=args.debug)
            
    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        sys.exit(0)
    except Exception as e:
        logger.exception("Fatal error in main")
        sys.exit(1)

if __name__ == "__main__":
    main()
