
import sys
from pathlib import Path
import pickle
import sqlite3
import re
from datetime import datetime

# Windows terminal encoding safety
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
MODEL_FILE = BASE_DIR / "model" / "sentiment_model.pkl"
DATABASE_FILE = BASE_DIR / "reviews.db"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = Flask(__name__)


# --------------------------------------------------
# 1. Startup Verifications & Model Loading
# --------------------------------------------------

if not TEMPLATES_DIR.exists():
    print(f"[WARNING] Templates directory not found at {TEMPLATES_DIR}")

if not STATIC_DIR.exists():
    print(f"[WARNING] Static directory not found at {STATIC_DIR}")

model = None
if not MODEL_FILE.exists():
    print("\n" + "=" * 60)
    print(" [WARNING] Trained model file not found!")
    print(f" Expected at: {MODEL_FILE}")
    print(" Action required: Run 'python train_model.py' to generate model.")
    print("=" * 60 + "\n")
else:
    try:
        with open(MODEL_FILE, "rb") as file:
            model = pickle.load(file)
        print(f"[SUCCESS] Loaded ML model from: {MODEL_FILE.name}")
    except Exception as e:
        print(f"[ERROR] Failed to load model artifact: {e}")
        model = None


# --------------------------------------------------
# 2. Database Initialization
# --------------------------------------------------

def get_db_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    try:
        connection = get_db_connection()
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant TEXT NOT NULL,
                review TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                confidence REAL NOT NULL,
                aspects TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()
        connection.close()
        print("[SUCCESS] SQLite database verified (reviews.db)")
    except sqlite3.Error as e:
        print(f"[ERROR] Database initialization failed: {e}")


# --------------------------------------------------
# 3. Aspect-Based Sentiment Analysis Lexicon & Rules
# --------------------------------------------------

ASPECT_KEYWORDS = {
    "Food": [
        "food", "taste", "tasty", "delicious", "biryani", "pizza",
        "burger", "dosa", "noodles", "paneer", "chicken", "rice",
        "crust", "flavour", "flavor", "fresh", "cold", "hot", "spicy",
        "bland", "stale", "sweet", "wings", "curry", "quality"
    ],
    "Delivery": [
        "delivery", "delivered", "arrived", "late", "fast", "slow",
        "time", "order", "rider", "delay", "delayed", "quick", "prompt"
    ],
    "Service": [
        "service", "staff", "restaurant", "rude", "friendly", "support",
        "courteous", "polite", "behavior", "executive"
    ],
    "Packaging": [
        "packaging", "packed", "package", "spilled", "damaged",
        "container", "box", "leakage", "clean", "spill", "leak", "sealed"
    ],
    "Price": [
        "price", "expensive", "cheap", "value", "money", "cost",
        "portion", "quantity", "affordable", "overpriced", "worth"
    ]
}

POSITIVE_WORDS = {
    "good", "great", "amazing", "excellent", "delicious", "tasty",
    "fresh", "fast", "friendly", "wonderful", "fantastic", "perfect",
    "love", "loved", "best", "hot", "reasonable", "courteous", "crispy",
    "juicy", "clean", "polite", "affordable", "filling", "spill-proof",
    "quick", "prompt", "rich", "tender", "generous"
}

NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "poor", "late", "cold", "rude",
    "slow", "disappointing", "disappointed", "expensive", "damaged",
    "spill", "spilled", "wrong", "incomplete", "tasteless", "small",
    "worst", "stale", "soggy", "bland", "leaked", "leaking", "oily",
    "undercooked", "delayed", "overpriced", "unacceptable", "inedible",
    "missing", "crushed"
}

NEGATION_WORDS = {"not", "no", "never", "hardly", "barely", "scarcely", "without"}


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def calculate_aspect_sentiment(review_text):
    """
    Performs clause-level aspect extraction and polarity scoring.
    Segments the review by punctuation and conjunctions (e.g. 'The biryani was delicious but delivery was late')
    so each aspect receives its local clause sentiment.
    """
    clauses = re.split(r"[.,;!?]|\b(?:but|however|although|while|yet|and)\b", review_text, flags=re.IGNORECASE)
    clauses = [c.strip() for c in clauses if c.strip()]

    aspect_results = {}

    for aspect, keywords in ASPECT_KEYWORDS.items():
        aspect_clauses = []
        matched_aspect_keywords = []

        for clause in clauses:
            clause_clean = clean_text(clause)
            clause_tokens = clause_clean.split()
            found_kw = [kw for kw in keywords if kw in clause_tokens or f" {kw} " in f" {clause_clean} "]
            if found_kw:
                aspect_clauses.append((clause, clause_tokens))
                matched_aspect_keywords.extend(found_kw)

        if not matched_aspect_keywords:
            continue

        matched_aspect_keywords = list(dict.fromkeys(matched_aspect_keywords))
        matched_sentiment_words = []

        pos_score = 0
        neg_score = 0

        for _, tokens in aspect_clauses:
            for i, word in enumerate(tokens):
                is_negated = False
                for j in range(max(0, i - 3), i):
                    if tokens[j] in NEGATION_WORDS:
                        is_negated = True
                        break

                if word in POSITIVE_WORDS:
                    matched_sentiment_words.append(word)
                    if is_negated:
                        neg_score += 1
                    else:
                        pos_score += 1
                elif word in NEGATIVE_WORDS:
                    matched_sentiment_words.append(word)
                    if is_negated:
                        pos_score += 1
                    else:
                        neg_score += 1

        if pos_score > neg_score:
            sentiment = "Positive"
        elif neg_score > pos_score:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        combined_keywords = list(dict.fromkeys(matched_aspect_keywords + matched_sentiment_words))

        aspect_results[aspect] = {
            "sentiment": sentiment,
            "keywords": combined_keywords
        }

    return aspect_results


# --------------------------------------------------
# 4. Web View Routes
# --------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# --------------------------------------------------
# 5. REST API Endpoints
# --------------------------------------------------

@app.route("/api/analyze", methods=["POST"])
def analyze_review():
    global model
    if model is None:
        if MODEL_FILE.exists():
            try:
                with open(MODEL_FILE, "rb") as file:
                    model = pickle.load(file)
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": f"Error loading model: {str(e)}"
                }), 500
        else:
            return jsonify({
                "success": False,
                "message": "Model not loaded. Please run 'python train_model.py' first."
            }), 500

    data = request.get_json(silent=True) or {}
    restaurant = str(data.get("restaurant", "")).strip() or "Unnamed Restaurant"
    review = str(data.get("review", "")).strip()

    if not review:
        return jsonify({
            "success": False,
            "message": "Please enter a customer review."
        }), 400

    try:
        prediction = model.predict([review])[0]
        probabilities = model.predict_proba([review])[0]
        classes = model.classes_

        confidence = float(max(probabilities) * 100)
        prediction_title = prediction.capitalize()

        aspects = calculate_aspect_sentiment(review)

        prob_dict = {
            str(classes[i]).capitalize(): round(float(probabilities[i] * 100), 2)
            for i in range(len(classes))
        }

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = get_db_connection()
            conn.execute(
                """
                INSERT INTO reviews (restaurant, review, sentiment, confidence, aspects, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (restaurant, review, prediction_title, round(confidence, 2), str(aspects), created_at)
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as db_err:
            print(f"[WARNING] Database write failed: {db_err}")

        return jsonify({
            "success": True,
            "restaurant": restaurant,
            "review": review,
            "sentiment": prediction_title,
            "confidence": round(confidence, 2),
            "probabilities": prob_dict,
            "aspects": aspects
        })

    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
        return jsonify({
            "success": False,
            "message": f"Analysis error: {str(e)}"
        }), 500


@app.route("/api/dashboard", methods=["GET"])
def dashboard_data():
    try:
        conn = get_db_connection()
        rows = conn.execute(
            """
            SELECT sentiment, COUNT(*) AS count
            FROM reviews
            GROUP BY sentiment
            """
        ).fetchall()

        total_row = conn.execute("SELECT COUNT(*) AS count FROM reviews").fetchone()
        recent_rows = conn.execute(
            """
            SELECT restaurant, review, sentiment, confidence, created_at
            FROM reviews
            ORDER BY id DESC
            LIMIT 10
            """
        ).fetchall()
        conn.close()

        counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        for row in rows:
            s = row["sentiment"]
            if s in counts:
                counts[s] = row["count"]

        total = total_row["count"] if total_row else 0
        positive_percentage = round((counts["Positive"] / total) * 100, 2) if total > 0 else 0.0

        return jsonify({
            "total": total,
            "positive": counts["Positive"],
            "negative": counts["Negative"],
            "neutral": counts["Neutral"],
            "positive_percentage": positive_percentage,
            "recent_reviews": [
                {
                    "restaurant": row["restaurant"],
                    "review": row["review"],
                    "sentiment": row["sentiment"],
                    "confidence": round(float(row["confidence"]), 2),
                    "created_at": row["created_at"]
                }
                for row in recent_rows
            ]
        })
    except sqlite3.Error as e:
        print(f"[ERROR] Database query failed: {e}")
        return jsonify({
            "total": 0,
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "positive_percentage": 0.0,
            "recent_reviews": []
        }), 500


# --------------------------------------------------
# 6. Server Initialization
# --------------------------------------------------

if __name__ == "__main__":
    create_database()

    print("\n=======================================================")
    print("    FoodReview AI - Sentiment Analysis System")
    print("=======================================================")
    print(" * Application running locally on:")
    print("   -> Home Interface : http://127.0.0.1:5000")
    print("   -> Dashboard View : http://127.0.0.1:5000/dashboard")
    print("=======================================================\n")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
