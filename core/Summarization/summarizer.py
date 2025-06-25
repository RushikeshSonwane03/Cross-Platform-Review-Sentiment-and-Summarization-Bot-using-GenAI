# Core/Summarization/summarizer.py

import pandas as pd
import requests
import json
import os

from dotenv import load_dotenv
from google.genai import types

load_dotenv()
api_key = api_key=os.getenv("GEMINI_API_KEY")
    

def create_summarization_prompt(dataframe: pd.DataFrame) -> str:
    """
    Concatenates all review_texts and constructs a Gemini summarization prompt.
    """
    if 'review_text' not in dataframe.columns:
        raise ValueError("DataFrame must contain a 'review_text' column.")

    all_reviews = ' '.join(dataframe['review_text'].fillna('').astype(str))

    prompt = f"""
    Please summarize the following customer reviews for potential buyers.
    The summary should be highly concise, informative, and directly assist a customer
    in making a quick decision: "to buy or not to buy?".

    Your summary should include the following sections:

    1.  **Overall Sentiment:** Provide a brief general feeling about the product.
    2.  **Key Strengths (Pros):** Bullet points of praised aspects.
    3.  **Key Weaknesses (Cons):** Bullet points of complaints.
    4.  **Important Considerations/Advice:** Advice or quirks to consider before purchase.

    Interpret any emojis in the reviews, and reflect or include them in the summary.

    ---
    **Customer Review Texts:**
    {all_reviews}
    """

    return prompt

def call_gemini_api(prompt_text: str) -> str:
    """
    Calls the Gemini 1.5 Flash API and returns the summary.
    """
    global api_key
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt_text}]
            }
        ]
    }

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        result = response.json()
        if result and result.get('candidates'):
            parts = result['candidates'][0].get('content', {}).get('parts', [])
            if parts and 'text' in parts[0]:
                return parts[0]['text']
            else:
                return "Error: No summary text found in API response."
        else:
            return "Error: No candidates in API response."

    except requests.exceptions.RequestException as e:
        return f"API request failed: {e}"
    except json.JSONDecodeError as e:
        return f"Failed to decode JSON: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def generate_summary(dataframe: pd.DataFrame) -> str:
    """
    High-level function: create prompt -> call API -> return summary string.
    """
    print("[INFO] Starting summarization process...")
    prompt = create_summarization_prompt(dataframe)
    summary = call_gemini_api(prompt)
    return summary