# Instagram Reels Analysis

A comprehensive tool for analyzing Instagram reels using AI models for sentiment analysis and content classification. The project includes both a web interface (Gradio) and command-line interface.

## Project Structure

```
instagram-reels-analysis/
├── config.py                 # Configuration settings and constants
├── utils.py                  # Utility functions for text processing
├── instagram_auth.py         # Instagram authentication and session management
├── sentiment_analysis.py     # Sentiment analysis using multilingual models
├── content_analysis.py       # Content classification using zero-shot learning
├── visualization.py          # Plot generation functions
├── data_processing.py        # Data fetching and processing operations
├── gradio_interface.py       # Main Gradio web interface
├── main.py                   # Entry point to run the application
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## Features

- **Instagram Authentication**: Secure login with 2FA support
- **Reel Fetching**: Fetch explore reels from Instagram
- **Sentiment Analysis**: Multilingual sentiment analysis (English, Hindi, Hinglish)
- **Content Classification**: Categorize reels by content type (news, meme, sports, etc.)
- **Personality-based Filtering**: Filter reels based on INTJ-T personality preferences
- **Visualization**: Interactive pie charts showing analysis results
- **Web Interface**: User-friendly Gradio web application
- **CLI Mode**: Command-line interface for batch processing
-**Recommendation Engine**:Fetches and saves reels to the "Collab Reels" folder based on user's taste.
## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd instagram-reels-analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Instagram credentials:
   - In Google Colab: Add your Instagram password to Colab secrets with key 'password'
   - For local setup: Set environment variables or modify config.py

## Usage

### Web Interface (currently not supported)

Run the Gradio web application:
```bash
python main.py --mode web
```

The interface will provide:
1. **Connect Instagram**: Login to your Instagram account
2. **Fetch Reels**: Retrieve explore reels
3. **Analyze**: Perform sentiment and content analysis with visualization

## Deployment Behavior: Temporary vs Permanent

The Instagram Doom Scroller app exhibits different behavior between temporary Gradio deployments (local/CLI) and permanent Hugging Face deployments due to several technical and policy constraints:

### Temporary Deployment (Local/Gradio CLI) Works Because:
✅ **Local Network Environment**  
   - Runs from your personal IP address which isn't flagged by Instagram's bot detection
   - Maintains consistent session cookies from your authenticated browser

✅ **Lower Rate Limits**  
   - Instagram applies less strict rate limiting to residential IPs

✅ **Full System Access**  
   - Can access local browser profiles, saved sessions, and developer credentials

✅ **No Sandbox Restrictions**  
   - No security policies blocking automation tools

### Permanent Deployment (Hugging Face) Fails Because:
❌ **Cloud IP Restrictions**  
   - Hugging Face servers use cloud provider IPs often flagged as bots
   - Instagram blocks many datacenter IP ranges

❌ **Meta Automation Policies**  
   - Violates [Instagram's Terms](https://help.instagram.com/581066165581870) prohibiting:
     - Automated data collection without API approval
     - Headless/scripted login attempts

❌ **Sandbox Limitations**  
   - Hugging Face's containerized environment:
     - Blocks certain automation libraries
     - Restricts persistent login sessions
     - Limits network-level customization

❌ **Credential Security**  
   - Permanent deployments shouldn't store personal login credentials
   - Environment variables behave differently in cloud vs local

### Technical Symptoms You'll Observe:
- **Temporary Deployment**: Successful login → reel collection → sentiment analysis
- **Permanent Deployment**:  
  - UI loads but analysis fails silently
  - Console shows `403 Forbidden` or `rate limited` errors
  - Possible `AutomationDetected` warnings in logs

### Recommended Solutions:
1. Use Instagram's official [Graph API](https://developers.facebook.com/docs/instagram-api/) with approved permissions
2. Switch to user-provided URLs instead of automated collection
3. Implement a local proxy service (though this violates ToS)
4. Use cached demo data for the permanent deployment

### Command Line Interface(Recommended)

Run analysis in CLI mode:
```bash
python main.py --mode cli
```

### Command Line Options

```bash
python main.py --help
```

- `--mode {web,cli}`: Choose between web interface or CLI
- `--no-share`: Don't create public Gradio link (web mode only)
- `--debug`: Enable debug mode

## Configuration

Edit `config.py` to customize:

- **USERNAME**: Your Instagram username
- **TARGET_REELS_COUNT**: Number of reels to process
- **CONTENT_CATEGORIES**: Categories for content classification
- **MODEL_CONFIG**: AI model parameters
- **PERSONALITY_SCORING**: Criteria for reel filtering

## Models Used

### Sentiment Analysis
- **English Emotion**: `finiteautomata/bertweet-base-emotion-analysis`
- **English Sentiment**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Hindi/Hinglish**: `ai4bharat/indic-bert` (fine-tunable)

### Content Classification
- **Zero-shot Classification**: `facebook/bart-large-mnli`

## Module Details

### `config.py`
- Central configuration management
- Model parameters and thresholds
- Category definitions and keywords

### `utils.py`
- Text preprocessing functions
- Language detection
- Personality-based scoring logic

### `instagram_auth.py`
- Instagram login/logout handling
- 2FA support
- Reel fetching and collection management

### `sentiment_analysis.py`
- `ReelSentimentAnalyzer` class
- Multilingual sentiment analysis
- Model ensemble and confidence handling

### `content_analysis.py`
- `ContentAnalyzer` class
- Zero-shot content classification
- Keyword-based categorization

### `visualization.py`
- Chart generation functions
- Matplotlib-based plotting
- Multiple output formats (figure/bytes)

### `data_processing.py`
- `ReelProcessor` class
- Batch analysis operations
- Data filtering and aggregation

### `gradio_interface.py`
- `GradioInterface` class
- Web UI components and event handlers
- Interactive analysis workflow

### `main.py`
- Application entry point
- Command-line argument parsing
- Mode selection (web/cli)

## Security Notes

- Never commit Instagram credentials to version control
- Use environment variables or secure secret management
- The application respects Instagram's rate limits
- 2FA codes are handled securely and not stored

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational and research purposes. Please respect Instagram's Terms of Service and API usage guidelines.

## Troubleshooting

### Common Issues

1. **Login Failed**: Check credentials and 2FA settings
2. **Model Loading Error**: Ensure sufficient memory and internet connection
3. **Gradio Interface Not Loading**: Check firewall settings and port availability
4. **Rate Limiting**: Reduce batch sizes and add delays between requests

### Debug Mode

Enable debug mode for verbose logging:
```bash
python main.py --mode web --debug
```

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review error logs in debug mode
3. Open an issue on the repository
