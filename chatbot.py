import json
import random
import string
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

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
    tag = item.get("tag") or item.get("tage")
    if not tag:
        continue

    patterns = item.get("patterns", [])
    for text in patterns:
        texts.append(text)
        labels.append(tag)

    responses[tag] = item.get("responses", [])

print(texts)
print(labels)

# -----------------------------
# 3. CLEANING
# -----------------------------

def clean(text):
    text = text.lower().strip()
    text = "".join(c for c in text if c not in string.punctuation)

    # 🔥 normalize common chat typos
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
        text = text.replace(k, v)

    return text

# -----------------------------
# 4. MODEL
# -----------------------------

vectorizer = CountVectorizer(ngram_range=(1,2))
X = vectorizer.fit_transform(texts)

model = MultinomialNB()
model.fit(X, labels)

# -----------------------------
# 5. TOP-2 INTENT LOGIC (FIXED)
# -----------------------------

def predict_intents(user_input):
    text = clean(user_input)
    vec = vectorizer.transform([text])

    if vec.sum() == 0: 
        return ["fallback"]

    probs = model.predict_proba(vec)[0]
    classes = model.classes_

    sorted_idx = probs.argsort()[::-1]

    intents = []

    greeting = None
    main_intents = []

    for i in sorted_idx:
        intent = classes[i]
        conf = probs[i]

        if conf < 0.20:
            continue

        if intent == "greeting" and greeting is None:
            greeting = intent
        else:
            main_intents.append(intent)

        if len(main_intents) == 2:
            break

    # build final result
    if greeting:
        intents.append(greeting)

    intents.extend(main_intents)

    if not intents:
        return ["fallback"]

    return intents

# -----------------------------
# 6. RESPONSE SYSTEM (FIXED)
# -----------------------------

def get_response(intents):
    result = []

    # ✅ Define priority (lower number = higher priority)
    priority = {
    "greeting": 0,
    "help": 1,
    "library": 2,
    "history_university": 3,
    "fallback": 99
    }

    # default priority for others
    def get_priority(intent):
        return priority.get(intent, 5)

    # ✅ Sort intents based on priority
    intents = sorted(intents, key=lambda x: priority.get(x, 50))

    for intent in intents:
        if intent in responses:
            result.append(random.choice(responses[intent]))

    return "\n".join(result)


# -----------------------------
# 7. CHAT LOOP
# -----------------------------

print("Chatbot running... type 'quit' to stop")

while True:
    user = input("You: ")

    if user.lower() == "quit":
        break

    intents = predict_intents(user)
    reply = get_response(intents)

    print("Bot:", reply)