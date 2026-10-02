/**
 * FoodReview AI - Dashboard Analytics Controller
 * Fetches SQLite aggregates from /api/dashboard and renders dynamic visual charts.
 */

document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
});

async function loadDashboard() {
    try {
        const response = await fetch("/api/dashboard");
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const data = await response.json();

        document.getElementById("totalReviews").textContent = data.total;
        document.getElementById("positiveReviews").textContent = data.positive;
        document.getElementById("neutralReviews").textContent = data.neutral;
        document.getElementById("negativeReviews").textContent = data.negative;
        document.getElementById("posPercentText").textContent = `${data.positive_percentage}%`;

        renderDonut(data.total, data.positive, data.neutral, data.negative);
        renderTable(data.recent_reviews);

    } catch (err) {
        console.error("Dashboard fetch error:", err);
        const tbody = document.getElementById("reviewsTableBody");
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="table-empty" style="color: #ef4444;">
                    Could not retrieve dashboard data. Make sure Flask is running.
                </td>
            </tr>
        `;
    }
}

function renderDonut(total, pos, neu, neg) {
    const donut = document.getElementById("sentimentDonut");
    if (!total || total === 0) {
        donut.style.background = "#e2e8f0";
        return;
    }

    const posDeg = (pos / total) * 360;
    const neuDeg = (neu / total) * 360;

    const posEnd = posDeg;
    const neuEnd = posDeg + neuDeg;

    donut.style.background = `conic-gradient(
        #10b981 0deg ${posEnd}deg,
        #f59e0b ${posEnd}deg ${neuEnd}deg,
        #ef4444 ${neuEnd}deg 360deg
    )`;
}

function renderTable(reviews) {
    const tbody = document.getElementById("reviewsTableBody");
    tbody.innerHTML = "";

    if (!reviews || reviews.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="table-empty">
                    No customer reviews logged yet. Analyze some reviews from the Home page!
                </td>
            </tr>
        `;
        return;
    }

    reviews.forEach(row => {
        let badgeClass = "badge-neu";
        let emoji = "😐";

        if (row.sentiment === "Positive") {
            badgeClass = "badge-pos";
            emoji = "😊";
        } else if (row.sentiment === "Negative") {
            badgeClass = "badge-neg";
            emoji = "😞";
        }

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${escapeHTML(row.restaurant)}</strong></td>
            <td>${escapeHTML(row.review)}</td>
            <td>
                <span class="aspect-badge ${badgeClass}">
                    <span>${emoji}</span>
                    <span>${escapeHTML(row.sentiment)}</span>
                </span>
            </td>
            <td><strong>${row.confidence}%</strong></td>
            <td><small style="color: #64748b;">${escapeHTML(row.created_at)}</small></td>
        `;
        tbody.appendChild(tr);
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
