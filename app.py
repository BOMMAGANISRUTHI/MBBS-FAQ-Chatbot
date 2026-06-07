from flask import Flask, render_template, request, jsonify
import nltk
import string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

app = Flask(__name__)

# ==============================================================
# FAQ DATABASE — MBBS Abroad Questions
# ==============================================================
FAQ_DATA = [
    # ---------- GENERAL (greetings & overview) ----------
    {
        "id": 101, "category": "General",
        "question": "hello",
        "answer": "Hello! How can I help you regarding MBBS abroad?"
    },
    {
        "id": 102, "category": "General",
        "question": "hi",
        "answer": "Hi! How can I help you regarding MBBS abroad?"
    },
    {
        "id": 103, "category": "General",
        "question": "hey",
        "answer": "Hello! Ask me anything about MBBS abroad."
    },
    {
        "id": 104, "category": "General",
        "question": "good morning",
        "answer": "Good Morning! How may I assist you today?"
    },
    {
        "id": 105, "category": "General",
        "question": "thank you",
        "answer": "You're welcome! Feel free to ask more questions."
    },
    {
        "id": 106, "category": "General",
        "question": "What are the advantages of studying MBBS abroad?",
        "answer": "Key advantages: 1) Lower total cost compared to Indian private colleges 2) No donation or capitation fees 3) Global exposure and international curriculum 4) English-medium instruction in popular destinations 5) Globally recognised degrees 6) Better doctor-to-patient ratio in teaching hospitals 7) Cultural exposure and personal development 8) NMC-approved degrees allow practice in India."
    },
    {
        "id": 107, "category": "General",
        "question": "What are the disadvantages of studying MBBS abroad?",
        "answer": "Key challenges: 1) Low FMGE pass rate (15–25%) — tough licensing exam 2) Distance from family and cultural adjustment 3) Language barriers in daily life (in non-English countries) 4) Quality of clinical exposure varies widely 5) Risk of choosing non-NMC approved universities 6) Currency fluctuation affecting fees 7) Limited clinical exposure compared to Indian teaching hospitals in some countries."
    },
    {
        "id": 108, "category": "General",
        "question": "How do I choose the best university for MBBS abroad?",
        "answer": "Checklist for choosing: 1) Verify NMC approval and WDOMS listing 2) Check FMGE pass rate of students from that university 3) Evaluate clinical hospital affiliation quality 4) Confirm English-medium instruction 5) Review total fee structure (no hidden costs) 6) Check Indian student community presence 7) Evaluate location and safety 8) Talk to current students or alumni. Never choose based on agent recommendation alone."
    },

    # ---------- ELIGIBILITY ----------
    {
        "id": 1, "category": "Eligibility",
        "question": "What is the minimum eligibility to study MBBS abroad?",
        "answer": "To study MBBS abroad you must have completed 10+2 (or equivalent) with Physics, Chemistry, and Biology (PCB). You need a minimum of 50% aggregate in PCB (40% for reserved categories in India). You must also qualify NEET-UG if you are an Indian student, as it is mandatory by the NMC (National Medical Commission)."
    },
    {
        "id": 2, "category": "Eligibility",
        "question": "Is NEET mandatory for MBBS abroad?",
        "answer": "Yes. As per NMC regulations effective 2018, NEET-UG is mandatory for all Indian students wishing to pursue MBBS abroad. Without a valid NEET score you will not be eligible to obtain a Foreign Medical Graduate (FMG) registration in India after completing your degree."
    },
    {
        "id": 3, "category": "Eligibility",
        "question": "What is the minimum age to apply for MBBS abroad?",
        "answer": "You must be at least 17 years of age on or before December 31st of the year of admission. There is no upper age limit for MBBS abroad, though some countries may have their own age restrictions that you should verify with the specific university."
    },
    {
        "id": 4, "category": "Eligibility",
        "question": "What NEET score is required for MBBS abroad?",
        "answer": "To be eligible to practice medicine in India after studying abroad, NMC requires you to qualify NEET (not just appear). For general category students, the qualifying percentile is 50th, while for SC/ST/OBC it is 40th. Many countries and universities also set their own minimum NEET score benchmarks, typically 150+ marks."
    },
    {
        "id": 5, "category": "Eligibility",
        "question": "Can I study MBBS abroad without a science background?",
        "answer": "No. A science background with Physics, Chemistry, and Biology in 10+2 is a fundamental requirement for MBBS admission anywhere in the world. This is non-negotiable regardless of the country you choose to study in."
    },

    # ---------- COUNTRIES ----------
    {
        "id": 6, "category": "Countries",
        "question": "Which are the best countries to study MBBS abroad?",
        "answer": "Top countries for MBBS abroad include Russia, Ukraine (pre-conflict status varies — verify current situation), China, Philippines, Kazakhstan, Kyrgyzstan, Georgia, Bangladesh, and Nepal. Russia and the Philippines are currently among the most popular due to globally recognised universities, English-medium instruction, and affordable fees."
    },
    {
        "id": 7, "category": "Countries",
        "question": "Is MBBS from Russia valid in India?",
        "answer": "Yes. MBBS degrees from NMC-approved Russian universities are valid in India. After completing the degree, you must pass the Foreign Medical Graduate Examination (FMGE) or NExT exam (from 2025 onwards) conducted by NBE to obtain a license to practice medicine in India."
    },
    {
        "id": 8, "category": "Countries",
        "question": "Is MBBS from the Philippines valid in India?",
        "answer": "Yes, provided the university is listed in the NMC (National Medical Commission) approved list and the World Directory of Medical Schools (WDOMS). Philippine MBBS graduates must clear FMGE/NExT to practice in India. The Philippines is popular as the medium of instruction is English and the curriculum is US-based."
    },
    {
        "id": 9, "category": "Countries",
        "question": "Is MBBS from China recognized in India?",
        "answer": "MBBS from China is recognized in India if the university is NMC-approved. However, since COVID-19, many Chinese universities have been conducting online classes which are not recognized by NMC. Students must ensure physical attendance and that their university remains on the approved list."
    },
    {
        "id": 10, "category": "Countries",
        "question": "Which country is cheapest to study MBBS abroad?",
        "answer": "Kazakhstan, Kyrgyzstan, Bangladesh, and Nepal offer the most affordable MBBS programs, with total fees ranging from $15,000 to $25,000 for the entire course. Russia and Georgia are mid-range at $25,000–$40,000. The Philippines is slightly higher but offers excellent value given its English-medium and US-aligned curriculum."
    },
    {
        "id": 11, "category": "Countries",
        "question": "Can I study MBBS in Germany?",
        "answer": "Germany does not offer MBBS in English. Medical degrees in Germany are taught in German (Medizinstudium). To study medicine in Germany you must have a strong command of German (at least B2/C1 level), pass the Hochschulzulassung, and meet the academic requirements. It is an excellent but demanding option."
    },
    {
        "id": 12, "category": "Countries",
        "question": "Is MBBS from Georgia valid in India?",
        "answer": "Yes, Georgia has several NMC-approved medical universities. Georgian MBBS degrees are globally recognised and the country has become a popular destination due to English-medium instruction, European standard education, and relatively low fees. You must still clear FMGE/NExT to practice in India."
    },

    # ---------- FEES & SCHOLARSHIPS ----------
    {
        "id": 13, "category": "Fees & Scholarships",
        "question": "What is the average total cost of MBBS abroad?",
        "answer": "The total cost of MBBS abroad (tuition + accommodation + living) varies by country: Russia: $30,000–$45,000 | Philippines: $35,000–$55,000 | Kazakhstan: $20,000–$30,000 | Georgia: $30,000–$45,000 | Kyrgyzstan: $18,000–$25,000. These are 6-year totals and do not include flight costs or visa fees."
    },
    {
        "id": 14, "category": "Fees & Scholarships",
        "question": "Are there scholarships available for MBBS abroad?",
        "answer": "Yes. Several scholarships are available: Russian Government Scholarship (covers tuition, offers ~15,000 seats globally), Chinese Government Scholarship (CSC), Philippine government scholarships, and university-level merit scholarships. Indian students can also explore education loans from SBI, Bank of Baroda, Axis Bank, and HDFC Credila at interest rates of 8–12%."
    },
    {
        "id": 15, "category": "Fees & Scholarships",
        "question": "Can I get an education loan for MBBS abroad?",
        "answer": "Yes. Major Indian banks including SBI (Global Ed-Vantage scheme), Bank of Baroda (Baroda Scholar), and HDFC Credila offer education loans for MBBS abroad. Loan amounts typically range from ₹20 lakh to ₹1.5 crore depending on the bank and collateral. Interest rates range from 8% to 12% per annum."
    },
    {
        "id": 16, "category": "Fees & Scholarships",
        "question": "What is the annual tuition fee at top Russian medical universities?",
        "answer": "Annual tuition fees at top Russian medical universities range from $3,500 to $6,000 per year. For example: Kazan Federal University charges around $4,000/year, Sechenov University is around $6,500/year, and Peoples' Friendship University (RUDN) is around $5,500/year. Hostel and living costs add approximately $1,500–$2,500 per year."
    },
    {
        "id": 17, "category": "Fees & Scholarships",
        "question": "Is MBBS abroad cheaper than private medical colleges in India?",
        "answer": "In most cases, yes. Private medical college fees in India can range from ₹60 lakh to ₹1.5 crore for the full course, plus management quota donations. MBBS abroad in countries like Russia, Kazakhstan, or Kyrgyzstan can cost as little as ₹20–35 lakh total, making it significantly more affordable."
    },

    # ---------- ADMISSION PROCESS ----------
    {
        "id": 18, "category": "Admission Process",
        "question": "What is the admission process for MBBS abroad?",
        "answer": "The typical admission process: 1) Clear NEET-UG 2) Research and shortlist NMC-approved universities 3) Submit online application with documents 4) Receive offer/admission letter 5) Apply for student visa 6) Pay initial tuition fee 7) Travel and complete enrollment. Most universities have direct admission without entrance exams, purely based on 10+2 marks and NEET score."
    },
    {
        "id": 19, "category": "Admission Process",
        "question": "What documents are required to apply for MBBS abroad?",
        "answer": "Standard documents required: 10th and 12th mark sheets and certificates, NEET scorecard, passport (minimum 18 months validity), passport-size photographs, birth certificate, medical fitness certificate, police clearance certificate (for some countries), bank statement showing sufficient funds, and HIV test certificate (required by some countries like Russia and China)."
    },
    {
        "id": 20, "category": "Admission Process",
        "question": "When does MBBS admission start abroad?",
        "answer": "Most universities abroad have intakes in September–October (major intake) and February–March (minor intake for some countries). Applications typically open 3–6 months before the intake. Since NEET results are declared in June, the September intake aligns well for Indian students. It is advisable to begin applications immediately after NEET results."
    },
    {
        "id": 21, "category": "Admission Process",
        "question": "Do I need an agent or consultant to apply for MBBS abroad?",
        "answer": "You do not legally need a consultant, but a reputable consultant can streamline the process — especially for visa applications, document authentication, and university shortlisting. Always verify that your consultant is registered and avoid those who claim guaranteed admissions or ask for cash payments. You can also apply directly through university websites."
    },
    {
        "id": 22, "category": "Admission Process",
        "question": "Is there a direct admission for MBBS abroad without entrance exam?",
        "answer": "Most countries (Russia, Kazakhstan, Georgia, Philippines) offer direct admissions to MBBS based on your 10+2 marks and NEET score — no additional university entrance exam. However, you must still have a valid NEET qualifying score. Some universities may conduct a basic English proficiency interview."
    },

    # ---------- CURRICULUM & DURATION ----------
    {
        "id": 23, "category": "Curriculum & Duration",
        "question": "How many years is MBBS abroad?",
        "answer": "MBBS abroad is typically 6 years: 5 years of academic study (pre-clinical and clinical) plus 1 year of compulsory internship (rotatory clinical internship). Some countries like the Philippines have a 5.5-year program. The degree awarded may be called MD (Doctor of Medicine) in some countries, which is equivalent to MBBS."
    },
    {
        "id": 24, "category": "Curriculum & Duration",
        "question": "Is the MBBS curriculum abroad the same as in India?",
        "answer": "The core medical curriculum (anatomy, physiology, biochemistry, pathology, pharmacology, clinical medicine) is largely universal and aligned with WHO standards. However, the teaching style, clinical exposure, and grading system vary. NMC mandates that the duration and subject coverage must be equivalent to what is required in India."
    },
    {
        "id": 25, "category": "Curriculum & Duration",
        "question": "Is MBBS taught in English abroad?",
        "answer": "Yes, many popular countries for Indian students offer MBBS entirely in English: Philippines, Russia (most universities offer English-medium tracks), Georgia, Kazakhstan, Kyrgyzstan, and Bangladesh. Some countries like Germany or Poland primarily teach in their local language, though English-medium programs are increasingly available."
    },
    {
        "id": 26, "category": "Curriculum & Duration",
        "question": "What subjects are taught in the first year of MBBS abroad?",
        "answer": "The first year of MBBS abroad typically covers: Anatomy (gross anatomy, histology, embryology), Physiology, and Biochemistry. These three subjects form the pre-clinical foundation across most countries. Some universities also include Medical Biology and Chemistry in the first year. Laboratory practicals are a key component."
    },
    {
        "id": 27, "category": "Curriculum & Duration",
        "question": "How is clinical training handled in MBBS abroad?",
        "answer": "Clinical training typically begins from the 3rd or 4th year. Students rotate through departments like Internal Medicine, Surgery, Pediatrics, OB-GYN, and Psychiatry in affiliated teaching hospitals. The quality of clinical exposure varies significantly by university and country — this is one of the most important factors to evaluate before choosing a university."
    },

    # ---------- RECOGNITION & LICENSING ----------
    {
        "id": 28, "category": "Recognition & Licensing",
        "question": "What is FMGE and is it mandatory?",
        "answer": "FMGE (Foreign Medical Graduate Examination) is a licensing exam conducted by the National Board of Examinations (NBE) in India. It is mandatory for Indian citizens who have completed their MBBS from a foreign medical institution and wish to practice medicine in India. From 2025, FMGE is being replaced by NExT (National Exit Test), which all medical graduates (Indian and foreign) must clear."
    },
    {
        "id": 29, "category": "Recognition & Licensing",
        "question": "What is the FMGE pass rate?",
        "answer": "The FMGE pass rate has historically been low — ranging from 15% to 25% annually. This means a large proportion of foreign MBBS graduates struggle to clear the licensing exam. The low pass rate highlights the importance of consistent study throughout the MBBS program and dedicated FMGE preparation in the final year."
    },
    {
        "id": 30, "category": "Recognition & Licensing",
        "question": "What is NExT exam and how does it affect MBBS abroad students?",
        "answer": "NExT (National Exit Test) is the new unified licensing and postgraduate entrance exam that will replace both FMGE (for foreign graduates) and NEET-PG (for Indian graduates). Once implemented (expected 2025), all medical graduates — from India or abroad — must clear NExT Step 1 and Step 2 to get a license to practice in India. This levels the playing field."
    },
    {
        "id": 31, "category": "Recognition & Licensing",
        "question": "How do I check if a university abroad is NMC approved?",
        "answer": "Visit the official NMC website (www.nmc.org.in) and check the approved list of foreign medical institutions. You should also cross-verify with the World Directory of Medical Schools (www.wdoms.org). Both listings together confirm global recognition. Always verify before applying — studying at a non-approved university means your degree will not be recognised in India."
    },
    {
        "id": 32, "category": "Recognition & Licensing",
        "question": "Can I practice medicine in other countries after MBBS abroad?",
        "answer": "Yes, but you must meet the licensing requirements of each country. For the USA, you need to clear USMLE Steps 1, 2CK, and 2CS. For the UK, clear PLAB 1 and 2. For Australia, clear AMC MCQ and clinical exams. The Philippines MBBS is particularly valued for the USMLE pathway due to its US-based curriculum."
    },
    {
        "id": 33, "category": "Recognition & Licensing",
        "question": "Is MBBS from abroad valid for PG admission in India?",
        "answer": "Yes, after clearing FMGE/NExT, foreign MBBS graduates are eligible to apply for PG medical admissions (MD/MS/DNB) in India. They must appear in NEET-PG (currently) or NExT Step 2 (from 2025). The same rules and reservation policies apply as for Indian MBBS graduates."
    },

    # ---------- STUDENT LIFE & SAFETY ----------
    {
        "id": 34, "category": "Student Life & Safety",
        "question": "Is it safe to study MBBS in Russia?",
        "answer": "Russia has been a popular destination for Indian students for decades. Major medical university cities like Moscow, Saint Petersburg, Kazan, and Volgograd have large Indian student communities. However, students should exercise general safety precautions. Due to the ongoing Ukraine conflict, check for any travel advisories from the Indian Ministry of External Affairs (MEA) before making decisions."
    },
    {
        "id": 35, "category": "Student Life & Safety",
        "question": "What is the food and accommodation like for Indian students abroad?",
        "answer": "Most universities offer on-campus hostels at subsidised costs ($50–$150/month). Many cities in Russia, Kazakhstan, and the Philippines have Indian restaurants and grocery stores catering to Indian students. Indian student associations in these countries actively help newcomers settle in. Self-cooking is common and affordable."
    },
    {
        "id": 36, "category": "Student Life & Safety",
        "question": "What is the cost of living for MBBS students abroad?",
        "answer": "Monthly living costs (accommodation + food + transport + miscellaneous): Russia: $200–$350/month | Philippines: $300–$450/month | Kazakhstan: $150–$250/month | Georgia: $250–$400/month | Kyrgyzstan: $120–$200/month. These are estimates and can vary by city and lifestyle."
    },
    {
        "id": 37, "category": "Student Life & Safety",
        "question": "Is there an Indian community in countries popular for MBBS?",
        "answer": "Yes. Countries like Russia, the Philippines, Kazakhstan, Georgia, and Kyrgyzstan have substantial Indian student communities, especially in university cities. There are active Indian Student Associations, WhatsApp groups, and cultural communities that organise festivals like Diwali and Holi. This makes the transition significantly easier for Indian students."
    },
    {
        "id": 38, "category": "Student Life & Safety",
        "question": "Do I need health insurance to study MBBS abroad?",
        "answer": "Yes. Most countries and universities require proof of health insurance as part of the visa and enrollment process. Some universities include basic health insurance in their fees. It is strongly advisable to purchase comprehensive health insurance covering medical treatment, emergency evacuation, and repatriation. Indian insurance companies like HDFC Ergo and Bajaj Allianz offer international student plans."
    },

    # ---------- VISA & TRAVEL ----------
    {
        "id": 39, "category": "Visa & Travel",
        "question": "How do I apply for a student visa for MBBS abroad?",
        "answer": "After receiving your official admission/invitation letter from the university, apply for a student visa at the respective country's embassy/consulate in India. Required documents typically include the admission letter, passport, financial proof, medical certificate, NEET scorecard, photographs, and visa application form. Processing time varies: Russia (2–4 weeks), Philippines (1–2 weeks), Georgia (2–3 weeks)."
    },
    {
        "id": 40, "category": "Visa & Travel",
        "question": "What is an invitation letter for MBBS admission?",
        "answer": "An invitation letter (also called an admission letter or offer letter) is an official document issued by the foreign university confirming your admission. It is required to apply for your student visa. The letter includes your name, course, duration, university details, and reporting date. Universities typically issue this within 2–4 weeks of confirming your admission."
    },
    {
        "id": 41, "category": "Visa & Travel",
        "question": "Do I need to apostille my documents for MBBS abroad?",
        "answer": "Yes, most countries require your educational documents (10th and 12th certificates, birth certificate) to be apostilled by the Ministry of External Affairs (MEA), India. Apostille is a form of document authentication recognised by Hague Convention member countries. Some countries may additionally require embassy attestation (legalisation) of documents."
    },
    {
        "id": 42, "category": "Visa & Travel",
        "question": "Can I work part-time while studying MBBS abroad?",
        "answer": "Part-time work rules vary by country. In the Philippines, student visas allow limited work. In Russia, working on a student visa is technically restricted. In Georgia, students can work part-time. However, MBBS is an extremely demanding course and most advisors discourage part-time work during the program as it can affect academic performance."
    },

    # ---------- AFTER MBBS ----------
    {
        "id": 43, "category": "After MBBS",
        "question": "What can I do after completing MBBS abroad?",
        "answer": "After MBBS abroad you can: 1) Return to India and clear FMGE/NExT to practice 2) Pursue PG (MD/MS) in India after clearing NEET-PG/NExT 3) Pursue PG abroad (USA — USMLE, UK — PLAB, Australia — AMC) 4) Complete a 1-year internship and work as a general physician 5) Pursue research or public health roles. The path depends on your career goals."
    },
    {
        "id": 44, "category": "After MBBS",
        "question": "How do I prepare for FMGE after MBBS abroad?",
        "answer": "Start preparing for FMGE from your 4th year itself by revising Indian-pattern MCQ-based questions alongside your university curriculum. Use coaching apps and platforms like DAMS, Dr Bhatia Medical, Marrow, and PrepLadder. Focus on high-yield subjects: Medicine, Surgery, OB-GYN, Pathology, and Pharmacology. Attempting multiple mock tests is essential."
    },
    {
        "id": 45, "category": "After MBBS",
        "question": "How long does it take to complete internship after MBBS abroad?",
        "answer": "The compulsory rotating internship is 12 months (1 year). In most countries abroad, the internship is conducted at the university's affiliated hospital in the final year of the program. Upon returning to India and clearing FMGE/NExT, you can complete an additional Indian internship if required by the state medical council for registration."
    },
    {
        "id": 46, "category": "After MBBS",
        "question": "Can I pursue MD in the USA after MBBS abroad?",
        "answer": "Yes, but it is a lengthy and competitive process. You must clear all three USMLE steps (Step 1, Step 2 CK, Step 2 CS — currently Step 2 CS is discontinued), secure a residency match through NRMP, and obtain ECFMG certification. The Philippines MBBS is particularly advantageous for the US pathway due to its US-based curriculum and prior BS degree requirement."
    },
    {
        "id": 47, "category": "After MBBS",
        "question": "What is the salary of a doctor in India after MBBS abroad?",
        "answer": "After clearing FMGE/NExT and completing registration, a fresh MBBS graduate can expect ₹50,000–₹1,00,000/month as a junior resident or general physician. With PG specialisation (MD/MS), salaries range from ₹1,50,000–₹3,00,000+/month in private hospitals. Government doctors start at around ₹56,000/month as per 7th pay commission."
    },
]

# ==============================================================
# NLP ENGINE — TF-IDF + COSINE SIMILARITY
# ==============================================================
STOP_WORDS = set(stopwords.words('english'))
SYNONYMS = {
    "cost": "fees",
    "price": "fees",
    "expense": "fees",
    "college": "university",
    "doctor": "mbbs",
    "salary": "income"
}

def preprocess(text):
    tokens = word_tokenize(text.lower())
    tokens = [t for t in tokens if t not in string.punctuation]
    tokens = [t for t in tokens if t not in STOP_WORDS]
    tokens = [SYNONYMS.get(t, t) for t in tokens]
    return ' '.join(tokens)

# Build corpus from questions + answers combined
corpus_raw   = [f["question"] + " " + f["answer"] for f in FAQ_DATA]
corpus_clean = [preprocess(doc) for doc in corpus_raw]

vectorizer = TfidfVectorizer(
    ngram_range=(1, 3),
    stop_words='english',
    max_features=5000
)
tfidf_matrix = vectorizer.fit_transform(corpus_clean)

def find_best_matches(user_query, category_filter="All", top_n=3):
    query_clean = preprocess(user_query)
    query_vec   = vectorizer.transform([query_clean])
    scores      = cosine_similarity(query_vec, tfidf_matrix).flatten()

    indices = range(len(FAQ_DATA))
    if category_filter != "All":
        indices = [i for i, f in enumerate(FAQ_DATA) if f["category"] == category_filter]

    filtered_scores = [(i, scores[i]) for i in indices]
    filtered_scores.sort(key=lambda x: x[1], reverse=True)
    top = filtered_scores[:top_n]

    results = []
    for idx, score in top:
        results.append({
            "faq":   FAQ_DATA[idx],
            "score": round(float(score), 4)
        })
    return results

def confidence_label(score):
    if score > 0.30: return "High"
    if score > 0.10: return "Medium"
    if score > 0.01: return "Low"
    return "None"

# ==============================================================
# FLASK ROUTES
# ==============================================================
@app.route("/")
def index():
    categories = ["All"] + sorted(list(set(f["category"] for f in FAQ_DATA)))
    # Pick meaningful suggestion questions (not greetings)
    suggestion_ids = [1, 6, 13, 27, 43]  # Eligibility, Countries, Fees, Clinical, After MBBS
    suggestions = [f["question"] for f in FAQ_DATA if f["id"] in suggestion_ids]
    return render_template("index.html",
                           categories=categories,
                           suggestions=suggestions,
                           total_faqs=len(FAQ_DATA))

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query", "").strip()
    category = data.get("category", "All")

    if not query:
        return jsonify({"error": "Empty query"}), 400

    matches = find_best_matches(query, category_filter=category, top_n=3)

    # No suitable answer found
    if not matches or matches[0]["score"] < 0.005:
        return jsonify({
            "matched": False,
            "confidence": "None",
            "score": 0,
            "message": (
                "Sorry, I am designed specifically to answer MBBS Abroad related questions. "
                "I currently do not have information about this topic. "
                "Please ask about Eligibility, Admission Process, Countries, "
                "Fees & Scholarships, Curriculum & Duration, Recognition & Licensing, "
                "Student Life & Safety, Visa & Travel, or After MBBS."
            )
        })

    # Best match
    best = matches[0]
    others = matches[1:]

    # Related questions
    same_cat = [
        f for f in FAQ_DATA
        if f["category"] == best["faq"]["category"]
        and f["id"] != best["faq"]["id"]
    ][:3]

    return jsonify({
        "matched": True,
        "confidence": confidence_label(best["score"]),
        "score": best["score"],
        "answer": {
            "id": best["faq"]["id"],
            "category": best["faq"]["category"],
            "question": best["faq"]["question"],
            "answer": best["faq"]["answer"]
        },
        "alternatives": [
            {"question": m["faq"]["question"], "score": m["score"]}
            for m in others if m["score"] > 0.05
        ],
        "related": [
            {"id": f["id"], "question": f["question"]}
            for f in same_cat
        ]
    })

    # Related questions from same category (excluding best match)
    same_cat = [f for f in FAQ_DATA
                if f["category"] == best["faq"]["category"]
                and f["id"] != best["faq"]["id"]][:3]
    return jsonify({
        "matched":    True,
        "confidence": confidence_label(best["score"]),
        "score":      best["score"],
        "answer": {
            "id":       best["faq"]["id"],
            "category": best["faq"]["category"],
            "question": best["faq"]["question"],
            "answer":   best["faq"]["answer"],
        },
        "alternatives": [
            {"question": m["faq"]["question"], "score": m["score"]}
            for m in others if m["score"] > 0.05
        ],
        "related": [
            {"id": f["id"], "question": f["question"]}
            for f in same_cat
        ]
    })

@app.route("/faqs")
def get_faqs():
    category = request.args.get("category", "All")
    search   = request.args.get("search", "").lower()
    result   = FAQ_DATA
    if category != "All":
        result = [f for f in result if f["category"] == category]
    if search:
        result = [f for f in result if search in f["question"].lower() or search in f["answer"].lower()]
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)