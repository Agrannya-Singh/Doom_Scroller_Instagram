"""
Visualization functions for generating charts and plots
"""

import matplotlib.pyplot as plt
import numpy as np
import io

def plot_sentiment_pie(results, title="Reels Sentiment Analysis"):
    """
    Creates a pie chart from sentiment analysis results

    Args:
        results: Counter object or dict with 'positive', 'neutral', 'negative' keys
        title: Chart title

    Returns:
        Matplotlib Figure object, or None if no data
    """
    labels = ['Positive', 'Neutral', 'Negative']
    sizes = [results.get('positive', 0), results.get('neutral', 0), results.get('negative', 0)]

    if sum(sizes) == 0:
        return None

    colors = ['#4CAF50', '#FFC107', '#F44336']  # Green, Yellow, Red
    explode = (0.05, 0, 0.05)  # Slight highlight on positive and negative

    fig, ax = plt.subplots(figsize=(8, 6))

    # Filter out slices with size 0 for cleaner plot
    filtered_labels = [label for i, label in enumerate(labels) if sizes[i] > 0]
    filtered_sizes = [size for size in sizes if size > 0]
    filtered_colors = [colors[i] for i, size in enumerate(sizes) if size > 0]

    # Adjust explode based on which slices exist
    explode_map = {'Positive': 0.05, 'Neutral': 0, 'Negative': 0.05}
    filtered_explode = [explode_map.get(label, 0) for label in filtered_labels]

    ax.pie(filtered_sizes, explode=filtered_explode, labels=filtered_labels, 
           colors=filtered_colors, autopct='%1.1f%%', shadow=True, startangle=140,
           textprops={'fontsize': 12, 'color': 'black'})

    ax.axis('equal')  # Equal aspect ratio ensures pie is drawn as circle
    plt.title(title, fontsize=16, pad=20)
    plt.tight_layout()

    return fig

def plot_category_distribution(counter, title="Reels Content Distribution"):
    """
    Generate pie chart from category counts

    Args:
        counter: Counter object with category counts
        title: Chart title

    Returns:
        Matplotlib Figure object, or None if no data
    """
    labels = []
    sizes = []

    total = sum(counter.values())
    if total == 0:
        return None

    # Categories less than 2% go into 'Other'
    threshold = total * 0.02
    other_count = 0

    sorted_categories = counter.most_common()

    for category, count in sorted_categories:
        if count >= threshold and category != "other":
            labels.append(category.replace('_', ' ').title())
            sizes.append(count)
        elif category == "other":
            other_count += count
        else:
            other_count += count

    if other_count > 0:
        labels.append("Other")
        sizes.append(other_count)

    if not sizes:
        return None

    fig, ax = plt.subplots(figsize=(10, 8))

    # Use a vibrant colormap
    colors = plt.cm.viridis(np.linspace(0, 1, len(sizes)))

    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140,
           colors=colors, wedgeprops={'edgecolor': 'white', 'linewidth': 1},
           textprops={'fontsize': 11, 'color': 'black'})

    plt.title(title, pad=20, fontsize=15)
    plt.axis('equal')  # Equal aspect ratio ensures pie is circular
    plt.tight_layout()

    return fig

def plot_sentiment_pie_bytes(results, title="Reels Sentiment Analysis"):
    """
    Creates a pie chart from sentiment analysis results and returns it as PNG bytes

    Args:
        results: Counter object or dict with 'positive', 'neutral', 'negative' keys
        title: Chart title

    Returns:
        Bytes of the PNG image of the plot, or None if no data
    """
    fig = plot_sentiment_pie(results, title)
    if fig is None:
        return None

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()

def plot_category_distribution_bytes(counter, title="Reels Content Distribution"):
    """
    Generate pie chart from category counts and returns it as PNG bytes

    Args:
        counter: Counter object with category counts
        title: Chart title

    Returns:
        Bytes of the PNG image of the plot, or None if no data
    """
    fig = plot_category_distribution(counter, title)
    if fig is None:
        return None

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()

def create_analysis_summary_plot(sentiment_results, category_counts):
    """
    Create a combined summary plot showing both sentiment and category analysis

    Args:
        sentiment_results: Counter object with sentiment analysis results
        category_counts: Counter object with category counts

    Returns:
        Matplotlib Figure object
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Sentiment pie chart
    sentiment_labels = ['Positive', 'Neutral', 'Negative']
    sentiment_sizes = [sentiment_results.get('positive', 0), 
                      sentiment_results.get('neutral', 0), 
                      sentiment_results.get('negative', 0)]
    sentiment_colors = ['#4CAF50', '#FFC107', '#F44336']

    if sum(sentiment_sizes) > 0:
        filtered_sentiment_labels = [label for i, label in enumerate(sentiment_labels) if sentiment_sizes[i] > 0]
        filtered_sentiment_sizes = [size for size in sentiment_sizes if size > 0]
        filtered_sentiment_colors = [sentiment_colors[i] for i, size in enumerate(sentiment_sizes) if size > 0]

        ax1.pie(filtered_sentiment_sizes, labels=filtered_sentiment_labels, 
               colors=filtered_sentiment_colors, autopct='%1.1f%%', startangle=140)
        ax1.set_title('Sentiment Distribution', fontsize=14, pad=20)

    # Category pie chart
    if sum(category_counts.values()) > 0:
        # Get top categories
        top_categories = category_counts.most_common(8)  # Show top 8 categories
        other_count = sum(count for cat, count in category_counts.items() 
                         if cat not in [item[0] for item in top_categories])

        category_labels = [cat.replace('_', ' ').title() for cat, _ in top_categories]
        category_sizes = [count for _, count in top_categories]

        if other_count > 0:
            category_labels.append('Other')
            category_sizes.append(other_count)

        colors = plt.cm.Set3(np.linspace(0, 1, len(category_sizes)))

        ax2.pie(category_sizes, labels=category_labels, autopct='%1.1f%%', 
               startangle=140, colors=colors)
        ax2.set_title('Content Category Distribution', fontsize=14, pad=20)

    plt.tight_layout()
    return fig
