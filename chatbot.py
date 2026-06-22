import json
import random
import string
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
#latest update
# -----------------------------
# 1. DATASET
# -----------------------------
with open("dataset.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

intents = raw_data.get("intents", [])

texts = []
labels = []
responses = {}

for item in intents:
    # Handles both "tag" and "tage" keys in your dataset
    tag = item.get("tag") or item.get("tage")
    if not tag:
        continue

    patterns = item.get("patterns", [])
    for text in patterns:
        texts.append(text)
        labels.append(tag)
    responses[tag] = item.get("responses", [])

print(f"Loaded {len(set(labels))} intents, {len(texts)} total patterns")

# -----------------------------
# 3. CLEANING
# -----------------------------
def clean(text):
    text = text.lower().strip()
    text = "".join(c for c in text if c not in string.punctuation)

    # Normalize common chat typos using whole-word matching only
    replacements = {
        "helo": "hello",
        "hlo": "hello",
        "hii": "hi",
        "hiii": "hi",
        "heyy": "hey",
        "halo": "hello",
        "hy": "hi"
    }
    for k, v in replacements.items():
        text = re.sub(r'\b' + k + r'\b', v, text)
    return text

# IMPORTANT: clean training texts too so model and input match
cleaned_texts = [clean(t) for t in texts]

# -----------------------------
# 4. MODEL
# # Why TfidfVectorizer instead of CountVectorizer:
# - TF-IDF weighs rare/meaningful words higher and common words lower
# - Much better accuracy for short chatbot messages
# - ngram_range(1,2) captures both single words and two-word phrases
# # Why alpha=0.3:
# - Default alpha=1.0 over-smooths on small datasets
# - Lower alpha makes the model more decisive and accurate
# -----------------------------
vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
X = vectorizer.fit_transform(cleaned_texts)

model = MultinomialNB(alpha=0.3)
model.fit(X, labels)

# -----------------------------
# 5. TOP-2 INTENT LOGIC
# -----------------------------
def predict_intents(user_input):
    text = clean(user_input)
    vec = vectorizer.transform([text])

    # If no known words found at all, go straight to fallback
    if vec.sum() == 0:
        return ["fallback"]

    probs = model.predict_proba(vec)[0]
    classes = model.classes_

    # Sort intents from highest to lowest confidence
    sorted_idx = probs.argsort()[::-1]

    result_intents = []
    greeting_intent = None
    main_intents = []

    for i in sorted_idx:
        intent = classes[i]
        conf = probs[i]

        # Threshold of 0.10 works well with 25 tags — confidence spreads thin
        # across many tags, so 0.35 was too strict and caused everything to fallback
        if conf < 0.10:
            continue

        if intent == "greeting" and greeting_intent is None:
            greeting_intent = intent
        else:
            main_intents.append(intent)

        if len(main_intents) == 2:
            break

    # Greeting goes first, then main topic intents
    if greeting_intent:
        result_intents.append(greeting_intent)
    result_intents.extend(main_intents)

    if not result_intents:
        return ["fallback"]

    return result_intents

# -----------------------------
# 6. RESPONSE SYSTEM
# -----------------------------
def get_response(detected_intents):
    result = []

    # Priority list: lower number = shown first in the reply
    priority = {
        "greeting": 0,
        "help": 1,
        "library": 2,
        "history_university": 3,
        "fallback": 99
    }

    def get_priority(intent):
        return priority.get(intent, 50)

    # Sort by priority before building the response
    sorted_intents = sorted(detected_intents, key=get_priority)

    for intent in sorted_intents:
        if intent in responses:
            result.append(random.choice(responses[intent]))

    return "\n".join(result)

# -----------------------------
# 7. CHAT LOOP
# -----------------------------
print("Kardan University Chatbot running... type 'quit' to stop")
while True:
    user = input("You: ")
    if user.lower() == "quit":
        break
    detected_intents = predict_intents(user)
    reply = get_response(detected_intents)
    print("Bot:", reply)