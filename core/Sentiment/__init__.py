# core/Sentiment/__init__.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification

print("[INFO] Loading RoBERTa model and tokenizer...")

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"

# Load tokenizer and model only once when app starts
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

print("[INFO] RoBERTa sentiment model loaded.")
