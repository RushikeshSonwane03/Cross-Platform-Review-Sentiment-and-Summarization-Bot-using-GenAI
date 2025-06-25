# Core/Sentiment/generate_sentiment_graphs.py

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for server or script rendering

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('ggplot')  # Match notebook style

def generate_sentiment_graphs(df, rating_col='rating'):
    """
    Generates all visualizations used in the notebook and saves them to Static/images.
    """

    print("[INFO] Generating graphs in Static/images/...")

    # Locate Static/images folder
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    image_dir = os.path.join(project_root, 'Static','sentiment_graphs')
    os.makedirs(image_dir, exist_ok=True)

    # ======================= 1. RATING DISTRIBUTION ===========================
    plt.figure(figsize=(12, 6))
    rating_colors = sns.color_palette("YlGnBu", n_colors=df[rating_col].nunique())
    ax = df[rating_col].value_counts().sort_index().plot(kind='bar', color=rating_colors)
    plt.title('Distribution of Star Ratings in Reviews', fontsize=16)
    plt.xlabel('Star Rating', fontsize=12)
    plt.ylabel('Number of Reviews', fontsize=12)
    plt.xticks(rotation=0, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    total_ratings = len(df)
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(f'{int(height)}\n({height/total_ratings:.1%})',
                    (p.get_x() + p.get_width() / 2., height),
                    ha='center', va='center',
                    xytext=(0, 9), textcoords='offset points',
                    fontsize=9, weight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(image_dir, 'rating_distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # ======================= 2. RoBERTa SENTIMENT DISTRIBUTION ===========================
    plt.figure(figsize=(8, 6))
    sentiment_colors = {'Positive': 'limegreen', 'Neutral': 'lightgray', 'Negative': 'tomato'}
    ax = sns.countplot(x='sentiment', data=df, palette=sentiment_colors,
                       order=['Positive', 'Neutral', 'Negative'])
    plt.title('RoBERTa Sentiment Distribution of Reviews', fontsize=16)
    plt.xlabel('Sentiment', fontsize=12)
    plt.ylabel('Number of Reviews', fontsize=12)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    total = len(df.dropna(subset=['sentiment']))
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f'{int(height)}\n({height/total:.1%})',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='center',
                        xytext=(0, 9), textcoords='offset points',
                        fontsize=9, weight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(image_dir, 'roberta_sentiment_distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # ======================= 3. HEATMAP: SENTIMENT vs RATING ===========================
    plt.figure(figsize=(12, 7))
    heatmap_data = pd.crosstab(df[rating_col], df['sentiment'], normalize='index')
    sns.heatmap(heatmap_data, annot=True, cmap='RdYlGn', fmt=".2%", linewidths=.5, linecolor='black')
    plt.title('RoBERTa Sentiment Distribution by Star Rating (Row Normalized)', fontsize=16)
    plt.xlabel('RoBERTa Sentiment', fontsize=12)
    plt.ylabel('Original Star Rating', fontsize=12)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10, rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(image_dir, 'roberta_sentiment_by_rating_heatmap.png'), dpi=300, bbox_inches='tight')
    plt.close()

    print("[INFO] All graphs saved successfully to Static/images/")
