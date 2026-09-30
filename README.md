# 🍔 AI Food Review Analyzer

An AI-powered web application that analyzes food reviews and identifies the sentiment expressed in the review. The project uses Natural Language Processing (NLP) techniques to process user-provided food reviews and generate an easy-to-understand analysis.

## 🚀 Features

* 📝 Enter food reviews through a simple web interface
* 🤖 AI-based sentiment analysis
* 😊 Identifies the sentiment of the review
* 📊 Displays analysis results clearly
* ⚡ Fast and simple web-based interface
* 📱 Responsive user interface
* 🔄 Real-time review analysis

## 🛠️ Technologies Used

### Frontend

* HTML5
* CSS3
* JavaScript
* Bootstrap

### Backend

* Python
* Flask

### AI / NLP

* Natural Language Processing (NLP)
* Transformer-based language model
* Hugging Face Transformers
* PyTorch

## 📂 Project Structure

```text
AI-Food-Review-Analyzer/
│
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
├── .gitignore
└── README.md
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/karthi18-coder/AI-Food-Review-Analyzer.git
```

### 2. Open the project folder

```bash
cd AI-Food-Review-Analyzer
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## 🧠 How It Works

```text
User enters food review
        ↓
Flask receives the review
        ↓
NLP / Transformer model processes the text
        ↓
Sentiment is analyzed
        ↓
Result is displayed to the user
```

## 💡 Example

**Input:**

> The food was delicious and the service was excellent.

**Analysis:**

```text
Sentiment: Positive
```

The application processes the review and presents the corresponding sentiment result.

## 🎯 Project Objective

The main objective of this project is to demonstrate how Artificial Intelligence and Natural Language Processing can be applied to analyze customer feedback in the food industry.

Such systems can help businesses understand customer opinions and identify general patterns in their reviews.

## 🔮 Future Enhancements

* ⭐ Rating prediction from review text
* 📈 Review analytics dashboard
* 📊 Positive, negative, and neutral review statistics
* 🔍 Keyword and aspect-based analysis
* 🗂️ Review history
* 🌐 Deployment as a public web application
* 📱 Improved mobile experience

⭐ If you find this project useful, consider giving the repository a star!
