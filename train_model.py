
import sys
from pathlib import Path
import pickle

# Ensure Windows terminal encoding safety
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "reviews.csv"
MODEL_DIR = BASE_DIR / "model"
MODEL_FILE = MODEL_DIR / "sentiment_model.pkl"


def main():
    print("\n=======================================================")
    print("   FoodReview AI - Machine Learning Training Pipeline")
    print("=======================================================")

    # 1. Verify Dataset Existence
    if not DATA_FILE.exists():
        print(f"[ERROR] Dataset not found at: {DATA_FILE}")
        print("Please ensure 'data/reviews.csv' exists before training.")
        sys.exit(1)

    print(f"[1/5] Loading dataset from: {DATA_FILE.name}")
    try:
        df = pd.read_csv(DATA_FILE, encoding="utf-8")
    except Exception as e:
        print(f"[ERROR] Failed to read CSV file: {e}")
        sys.exit(1)

    # 2. Validate Required Columns
    if "review" not in df.columns or "sentiment" not in df.columns:
        print("[ERROR] CSV must contain both 'review' and 'sentiment' columns.")
        sys.exit(1)

    # 3. Clean and Preprocess
    initial_count = len(df)
    df = df.dropna(subset=["review", "sentiment"]).copy()
    df["review"] = df["review"].astype(str).str.strip()
    df["sentiment"] = df["sentiment"].astype(str).str.lower().str.strip()
    df = df[df["review"].str.len() > 0]

    print(f"[2/5] Cleaned dataset: {len(df)} valid records (dropped {initial_count - len(df)} invalid)")
    print("      Class Distribution:")
    for label, count in df["sentiment"].value_counts().items():
        print(f"        - {label.capitalize():<10}: {count} samples")

    # 4. Train / Test Split
    X = df["review"]
    y = df["sentiment"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
    print(f"[3/5] Split dataset: {len(X_train)} training samples, {len(X_test)} testing samples")

    # 5. Build Pipeline: TF-IDF (unigrams + bigrams) + Logistic Regression
    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 2),
                sublinear_tf=True
            )
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                C=2.0,
                random_state=42
            )
        )
    ])

    print("[4/5] Training TF-IDF + Logistic Regression model...")
    pipeline.fit(X_train, y_train)

    # 6. Evaluation
    predictions = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    print("\n-------------------------------------------------------")
    print(f"   Model Accuracy on Test Split: {accuracy * 100:.2f}%")
    print("-------------------------------------------------------")
    print("\nClassification Report:\n")
    print(classification_report(y_test, predictions, target_names=["Negative", "Neutral", "Positive"]))

    # 7. Save Model Artifact
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_FILE, "wb") as f:
        pickle.dump(pipeline, f)

    print(f"[5/5] Success! Trained model serialized to:")
    print(f"      {MODEL_FILE}")
    print("=======================================================\n")


if __name__ == "__main__":
    main()
