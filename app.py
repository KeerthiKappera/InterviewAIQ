from fastapi import FastAPI, UploadFile, File, Form
from pypdf import PdfReader
from dotenv import load_dotenv
load_dotenv()
import os
from groq import Groq

client = Groq(api_key = os.getenv("GROQ_API_KEY"))


def calculate_resume_match(resume_text, jd):
    skills = [
    "python", "machine learning", "deep learning", "nlp",
    "rag", "langchain", "faiss", "openai", "llama",
    "mistral", "aws", "azure", "gcp", "pytorch",
    "tensorflow", "sql", "power bi", "data science",
    "genai", "prompt engineering", "api", "docker",
    "kubernetes", "spark", "tableau", "statistics"
]

    resume_text = resume_text.lower()
    jd = jd.lower()

    jd_skills = [skill for skill in skills if skill in jd]
    matched_skills = [skill for skill in jd_skills if skill in resume_text]

    if len(jd_skills) == 0:
        return 65, 0, []

    score = int((len(matched_skills) / len(jd_skills)) * 100)

    print("JD Skills:", jd_skills)
    print("Matched Skills:", matched_skills)
    
    missing_skills = len(jd_skills) - len(matched_skills)
    return score, missing_skills, matched_skills

app = FastAPI()



@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate")
async def generate_questions(
    resume: UploadFile = File(...),
    company: str = Form(...),
    role: str = Form(...),
    jd: str = Form(...)
):
    try:
        reviews = "No company insights available"

        if not jd.strip() or len(jd.strip()) < 50:
            jd = f"""
            Common responsibilities for {role} at {company} include:
            - Problem solving
            - Technical knowledge in role-specific tools
            - Communication and collaboration
            - Project implementation
            - System design and debugging
            """
    
        # Resume PDF read
        reader = PdfReader(resume.file)

        resume_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                resume_text += text

        print("Resume loaded successfully")
        print(resume_text[:1000])

        match_score, missing_skills, matched_skills = calculate_resume_match(resume_text, jd)
        print("Resume Match:", match_score)
        print("Missing Skills:", missing_skills)

        if match_score >= 85:
            recommendation = "Excellent fit. Your profile aligns very strongly with this role."
        elif match_score >= 70:
            recommendation = "Strong fit. Minor skill gaps exist but overall profile is highly suitable."
        elif match_score >= 50:
            recommendation = "Moderate fit. Good foundation, but prepare missing skills before interview."
        else:
            recommendation = "Needs preparation. Significant skill gaps detected for this role."

        review_prompt = f"""
        
        You are a hiring researcher.

        Give realistic interview insights for company: {company}
        Role: {role}

        Use common hiring patterns from tech industry if company-specific details are unavailable.

        Return only:
        - Interview difficulty (out of 10)
        - Number of rounds
        - Common interview focus areas
        - Common repeated questions

        """

        review_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            messages=[
                {"role": "user", "content": review_prompt}
            ]
        )

        reviews = review_response.choices[0].message.content


        # Context build
        context = f"""
        RESUME:
        {resume_text}

        JOB DESCRIPTION:
        {jd}

        COMPANY REVIEWS / INTERVIEW EXPERIENCES:
        {reviews}
        """

        prompt = f"""
        
        You are a senior AI interview expert and hiring manager.
        
        Use company reviews and interview experiences to make questions more realistic.
        Focus on repeated interview patterns if available.

        Your job is to generate highly relevant interview preparation content based on:
        1. Candidate Resume
        2. Job Description
        3. Company Name
        4. Role

        COMPANY: {company}
        ROLE: {role}

        CONTEXT:
        {context}

        Instructions:
        - Analyze candidate strengths from resume.
        - Analyze missing skills from JD.
        - Generate company-specific interview questions.
        - Focus heavily on technical depth.
        - Make questions realistic like actual interviews.
        - Avoid generic questions.
        - Include questions based on candidate projects and experience.
        - Generate questions specific to COMPANY and ROLE.
        - Use JOB DESCRIPTION heavily.
        - If company-specific information is unavailable, use industry-standard interview patterns.
        - Adapt technical depth based on role.

        Return response in EXACT format:

        ==============================
        TECHNICAL QUESTIONS (15)
        ==============================
        1.
        2.
        3.

        ==============================
        BEHAVIORAL QUESTIONS (10)
        ==============================
        1.
        2.
        3.

        ==============================
        SCENARIO BASED QUESTIONS (5)
        ==============================
        1.
        2.
        3.

        ==============================
        CODING QUESTIONS (5)
        ==============================
        1.
        2.
        3.

        ==============================
        PERSONALIZED QUESTIONS FROM RESUME (5)
        ==============================
        1.
        2.
        3.

        ==============================
        IMPORTANT TOPICS TO PREPARE
        ==============================
        - Topic 1
        - Topic 2

        ==============================
        MISSING SKILLS IN RESUME
        ==============================
        - Skill 1
        - Skill 2

        ==============================
        TOP 5 SAMPLE STRONG ANSWERS
        ==============================
        Q1:
        A1:

        Q2:
        A2:
        """
        print("NEW PROMPT VERSION RUNNING")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        question_count = 40
        return {
            "response": response.choices[0].message.content,
            "resume_match": match_score,
            "missing_skills": missing_skills,
            "question_count": question_count,
            "reviews": reviews,
            "recommendation": recommendation,
            "matched_skills": matched_skills,
            "company": company,
            "role": role
        }

    except Exception as e:
        return {
            "error": str(e)
        }