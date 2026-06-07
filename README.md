# 🎓 MBBS FAQ Chatbot

An AI-powered FAQ chatbot built using **Python, Flask, NLP, TF-IDF Vectorization, and Cosine Similarity**. The chatbot is designed to answer frequently asked questions related to **MBBS Abroad Admissions**, including eligibility, countries, fees, scholarships, admission process, licensing exams, student life, visas, and career opportunities.

---

## 📌 Features

- 💬 Interactive chatbot interface
- 🧠 NLP-based question matching
- 🔍 TF-IDF Vectorization for text understanding
- 📊 Cosine Similarity for answer retrieval
- 📂 Category-wise FAQ filtering
- 🎯 Confidence score for responses
- 🔄 Related question suggestions
- 📱 Responsive modern UI
- ⚡ Fast and lightweight Flask backend

---

## 🛠 Technologies Used

### Backend
- Python
- Flask
- NLTK
- NumPy
- Scikit-learn

### NLP Techniques
- Tokenization
- Stopword Removal
- Synonym Mapping
- TF-IDF Vectorization
- Cosine Similarity

### Frontend
- HTML5
- CSS3
- JavaScript

---

## 📁 Project Structure

```text
MBBS-FAQ-Chatbot/
│
├── app.py
├── requirements.txt
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── chat.js
│
└── README.md
```

---

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/BOMMAGANISRUTHI/MBBS-FAQ-Chatbot.git
cd MBBS-FAQ-Chatbot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Application

```bash
python app.py
```

Open browser:

```text
http://127.0.0.1:5000
```

---

## 📚 FAQ Categories

The chatbot contains knowledge about:

- Eligibility
- Countries
- Fees & Scholarships
- Admission Process
- Curriculum & Duration
- Recognition & Licensing
- Student Life & Safety
- Visa & Travel
- After MBBS
- General Queries

---

## 🔍 How It Works

1. User enters a question.
2. Text is preprocessed using NLP.
3. TF-IDF converts text into vectors.
4. Cosine Similarity compares the query with FAQ data.
5. Best matching answer is returned.
6. Confidence score and related questions are displayed.

---

## 🎯 Sample Questions

- Is NEET mandatory for MBBS abroad?
- Which country is best for MBBS abroad?
- What is the average cost of MBBS abroad?
- Is MBBS from Russia valid in India?
- What is FMGE?
- How do I apply for a student visa?

---

## 📈 Future Improvements

- Voice-based interaction
- Multi-language support
- Database integration
- GPT/LLM integration
- User authentication
- Chat history storage

---

## 👩‍💻 Author

**Bommagani Sruthi**

- B.Tech Student
- Interested in AI, NLP, Web Development, and Design

GitHub:
https://github.com/BOMMAGANISRUTHI

---

## 📄 License

This project is developed for educational and learning purposes.
