import numpy as np
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, classification_report

MAX_TRAIN = 200000    # how many generated messages to learn from. None = use all (slow, needs lots of RAM)

df = pd.read_csv("big_data.csv")
print("Total messages in file:", len(df))
print(df["source"].value_counts())

hand = df[df["source"] == "hand"]
docs = df[df["source"] == "docs"]
rest = df[~df["source"].isin(["hand", "docs"])]

if MAX_TRAIN and len(rest) > MAX_TRAIN:
    rest = rest.sample(MAX_TRAIN, random_state=1)
print("Messages used for learning:", len(rest))


def build(data):
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), lowercase=True, sublinear_tf=True,
                          max_features=300000, min_df=3, dtype=np.float32)
    X = vec.fit_transform(data["text"])
    if hasattr(vec, "stop_words_"):
        vec.stop_words_ = None          # keeps the saved file small
    model = SGDClassifier(loss="log_loss", alpha=5e-6, max_iter=20, tol=1e-4,
                          class_weight="balanced", random_state=1)
    model.fit(X, data["label"])
    return vec, model


# 1. HONEST EXAM: learn from generated data only, test on your 131 hand-written messages
print("\nTraining for the exam (this takes a few minutes)...")
vec, model = build(rest)
pred = model.predict(vec.transform(hand["text"]))
print("\nExam on your hand-written messages (never studied):")
print("Accuracy:", round(accuracy_score(hand["label"], pred), 3))
print(classification_report(hand["label"], pred))

# 2. FINAL BRAIN: generated + document examples x5 + hand-written x5
print("Training the final brain...")
final_data = pd.concat([rest] + [hand] * 5 + [docs] * 5, ignore_index=True)
vec, model = build(final_data)
joblib.dump(model, "model.pkl")
joblib.dump(vec, "vec.pkl")
print("Saved model.pkl and vec.pkl")

# 3. Quick test
tests = [
    "Your account is blocked. Share OTP now",
    "Hey, are we meeting at 5 today?",
    "Your SBI OTP is 123456. Never share this with anyone",
    "You have an unpaid toll of Rs 325. Pay today at sunpass-etc.com/pay",
    "Buy 10 Amazon gift cards and send me the codes. Do not tell anyone",
    "Your Swiggy order is out for delivery and will arrive in 15 minutes",
]
for t in tests:
    chance = model.predict_proba(vec.transform([t]))[0][1]
    print(f"{t}  ->  scam chance: {chance:.0%}")