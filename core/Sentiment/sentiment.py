# your_app/sentiment.py
import numpy as np
import pandas as pd
from scipy.special import softmax
import matplotlib.pyplot as plt
import seaborn as sns
import os

from tqdm.auto import tqdm
from . import tokenizer, model  # imported from __init__.py

from .generate_sentiment_graphs import generate_sentiment_graphs  # Generate Graphs


# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

def roberta_polarity_scores(text):
    try:
        encoded_text = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
        output = model(**encoded_text)
        scores = softmax(output.logits.detach().numpy())

        neg, neu, pos = scores[0]
        sentiment = max(zip(['Negative', 'Neutral', 'Positive'], scores[0]), key=lambda x: x[1])[0]
        return {'neg': neg, 'neu': neu, 'pos': pos, 'sentiment': sentiment}
    except Exception as e:
        print(f"[ERROR] Failed to process text: {e}")
        return {'neg': np.nan, 'neu': np.nan, 'pos': np.nan, 'sentiment': 'Error'}

def analyze_sentiments(df, text_col='review_text', rating_col='rating'):
    print("Analysing Sentiments .....")
    df['review_text_cleaned'] = df[text_col].fillna('').astype(str)
    print("[INFO] Starting sentiment analysis...")
    
    results = {}
    for i, row in tqdm(df.iterrows(), total=len(df)):
        results[i] = roberta_polarity_scores(row['review_text_cleaned'])
    
    result_df = pd.DataFrame.from_dict(results, orient='index')
    df_merged = pd.concat([df, result_df], axis=1)

    # print("\n ------------------------------------------------------------------ \n")
    # print(df_merged)
    # print("\n ------------------------------------------------------------------ \n")
    
    print("[INFO] Sentiment analysis complete.")

    # Generate and save graphs
    generate_sentiment_graphs(df_merged, rating_col=rating_col)


    return df_merged
