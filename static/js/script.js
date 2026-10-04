/**
 * FoodReview AI - Frontend Review Analysis Script
 * Manages form submission, asynchronous model inference, and dynamic DOM updates.
 */

const ASPECT_ICONS = {
    "Food": "🍕",
    "Delivery": "🚀",
    "Service": "👨‍🍳",
    "Packaging": "📦",
    "Price": "💰"
};

const SAMPLES = {
    1: {
        restaurant: "Paradise Biryani",
        review: "The biryani was delicious but delivery was late"
    },
    2: {
        restaurant: "Pizza Bella",
        review: "Crispy pizza with generous fresh toppings and delivery arrived super fast!"
    },
    3: {
        restaurant: "Burger Point",
        review: "Burger was cold, the paper packaging was damaged and delivery was delayed."
    },
    4: {
        restaurant: "Wok & Roll",
        review: "The hakka noodles tasted delicious but price was way too expensive for this small portion."
    }
};

function fillSample(id) {
    const sample = SAMPLES[id];
    if (sample) {
        document.getElementById("restaurant").value = sample.restaurant;
        document.getElementById("review").value = sample.review;
        clearError();
    }
}

function clearError() {
    const errorEl = document.getElementById("errorMessage");
    errorEl.textContent = "";
    errorEl.classList.add("hidden");
}

function showError(msg) {
    const errorEl = document.getElementById("errorMessage");
    errorEl.textContent = msg;
    errorEl.classList.remove("hidden");
}

async function analyzeReview() {
    clearError();

    const restaurantInput = document.getElementById("restaurant");
    const reviewInput = document.getElementById("review");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const btnText = document.getElementById("btnText");
    const btnLoader = document.getElementById("btnLoader");
    const resultCard = document.getElementById("resultCard");

    const restaurant = restaurantInput.value.trim() || "Customer Review";
    const review = reviewInput.value.trim();

    if (!review) {
        showError("Please enter a customer review to analyze.");
        reviewInput.focus();
        return;
    }

    analyzeBtn.disabled = true;
    btnText.textContent = "Analyzing...";
    btnLoader.classList.remove("hidden");

    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                restaurant: restaurant,
                review: review
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            showError(data.message || "Failed to analyze review.");
            return;
        }

        renderResults(data);
        resultCard.classList.remove("hidden");
        resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });

    } catch (err) {
        console.error("Network error:", err);
        showError("Cannot connect to Flask server. Please verify app.py is running.");
    } finally {
        analyzeBtn.disabled = false;
        btnText.textContent = "Analyze Review";
        btnLoader.classList.add("hidden");
    }
}

function renderResults(data) {
    document.getElementById("restaurantTag").textContent = data.restaurant;

    const sentimentBanner = document.getElementById("sentimentBanner");
    const sentimentIcon = document.getElementById("sentimentIcon");
    const sentimentText = document.getElementById("sentimentText");
    const confidenceText = document.getElementById("confidenceText");

    sentimentBanner.className = "sentiment-banner";

    if (data.sentiment === "Positive") {
        sentimentBanner.classList.add("positive");
        sentimentIcon.textContent = "😊";
    } else if (data.sentiment === "Negative") {
        sentimentBanner.classList.add("negative");
        sentimentIcon.textContent = "😞";
    } else {
        sentimentBanner.classList.add("neutral");
        sentimentIcon.textContent = "😐";
    }

    sentimentText.textContent = data.sentiment;
    confidenceText.textContent = `Confidence: ${data.confidence}%`;

    const pos = data.probabilities.Positive || 0;
    const neu = data.probabilities.Neutral || 0;
    const neg = data.probabilities.Negative || 0;

    document.getElementById("positiveProb").textContent = `${pos}%`;
    document.getElementById("neutralProb").textContent = `${neu}%`;
    document.getElementById("negativeProb").textContent = `${neg}%`;

    document.getElementById("positiveBar").style.width = `${pos}%`;
    document.getElementById("neutralBar").style.width = `${neu}%`;
    document.getElementById("negativeBar").style.width = `${neg}%`;

    const aspectsContainer = document.getElementById("aspectsContainer");
    aspectsContainer.innerHTML = "";

    const aspectEntries = Object.entries(data.aspects || {});

    if (aspectEntries.length === 0) {
        aspectsContainer.innerHTML = `
            <div class="no-aspects">
                No specific domain aspects (Food, Delivery, Packaging, Service, Price) detected in this review.
            </div>
        `;
        return;
    }

    aspectEntries.forEach(([aspect, details]) => {
        const icon = ASPECT_ICONS[aspect] || "📌";
        let badgeClass = "badge-neu";
        let sentimentEmoji = "😐";

        if (details.sentiment === "Positive") {
            badgeClass = "badge-pos";
            sentimentEmoji = "😊";
        } else if (details.sentiment === "Negative") {
            badgeClass = "badge-neg";
            sentimentEmoji = "😞";
        }

        const keywordsHtml = details.keywords.map(kw => 
            `<span class="keyword-tag">${escapeHTML(kw)}</span>`
        ).join("");

        const item = document.createElement("div");
        item.className = "aspect-card";
        item.innerHTML = `
            <div>
                <div class="aspect-title">
                    <span>${icon}</span>
                    <span>${aspect}</span>
                </div>
                <div class="aspect-keywords">
                    ${keywordsHtml}
                </div>
            </div>
            <div class="aspect-badge ${badgeClass}">
                <span>${sentimentEmoji}</span>
                <span>${details.sentiment}</span>
            </div>
        `;
        aspectsContainer.appendChild(item);
    });
}

function escapeHTML(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
