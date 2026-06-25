import pdfplumber
import pandas as pd
from sentence_transformers import SentenceTransformer 
from sklearn.metrics.pairwise import cosine_similarity 
import streamlit as st
import spacy

st.title("AI Resume Screener")

jd = st.text_area("Paste Job Description")

uploaded_files = st.file_uploader(
    "Upload Resumes",
    accept_multiple_files=True
)

def extract_resume_text(pdf_file):
    text = ""

    with pdfplumber.open(pdf_file) as pdf: 
        for page in pdf.pages: 
            text += page.extract_text() or "" 

    return text

skills = [
    "python",
    "sql",
    "java",
    "aws",
    "docker",
    "machine learning",
    "react",
    "javascript",
    "pandas",
    "numpy"
]

def extract_skills(text): 
    text = text.lower() 

    found = []

    for skill in skills:
        if skill in text:
            found.append(skill)

    return found

def score_resume(candidate_skills, jd_skills): 

    matched = set(candidate_skills) & set(jd_skills)

    score = len(matched) / len(jd_skills) * 100 

    return round(score, 2) 

nlp = spacy.load("en_core_web_sm")

def extract_name(text):
    doc = nlp(text)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text

    return "Unknown"

model = SentenceTransformer(
    "all-MiniLM-L6-v2"           #A pre-defined model name
)

if st.button("Analyze"):
    st.write("Ranking candidates...")

    resumes = []

    if uploaded_files:
        for file in uploaded_files: 
            resumes.append({      
                "filename": file.name,
                "text": extract_resume_text(file) 
            })                                    


    jd_skills = extract_skills(jd or "")

    
    for i in resumes:
        i["CandidateName"] = extract_name(i["text"])
        i["skills"] = extract_skills(i["text"])                                              
        i["rule_score"] = score_resume(i["skills"], jd_skills)

    jd_embedding = model.encode(jd or "")

    for i in resumes:
        resume_embedding = model.encode(i["text"])

        sim_score = cosine_similarity(
            [resume_embedding],
            [jd_embedding]
            )[0][0]

        i["semantic_score"] = sim_score

    for i in resumes:
        i["final_score"] = 0.5 * i["rule_score"] + 50 * i["semantic_score"]

    results = []

    for i in resumes:
        results.append({
            "Candidate Name": i["CandidateName"],
            "Skills": ", ".join(i.get("skills", [])),
            "Rule Score (%)": i.get("rule_score", 0),
            "Semantic Score": round(i.get("semantic_score", 0), 4) * 100,
            "Final Score": round(i.get("final_score", 0), 2)
        })

    df = pd.DataFrame(results)
    df = df.sort_values(by="Final Score", ascending=False)

    st.dataframe(df)

    st.subheader("🏆 Ranked Candidates")
    
    sorted_resumes = sorted(resumes, key=lambda x: x.get("final_score", 0), reverse=True)
    for i in sorted_resumes:
        st.write(i["CandidateName"], round(i.get("final_score", 0), 2))
