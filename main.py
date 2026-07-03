import os

resume_path = "data/resume"
jd_path = "data/jd"
review_path = "data/reviews"

print("Project setup successful!")
from langchain_community.document_loaders import PyPDFLoader

resume_file = "data/resume/Keerthi_Kappera_RESUME.pdf"
loader = PyPDFLoader(resume_file)
documents = loader.load()

print(documents)

with open("data/jd/accellorjd.txt", "r", encoding = "utf-8") as f:
    jd_text = f.read()
print("JD loaded")
print(jd_text[:300])

with open("data/reviews/accellorreviews.txt", "r", encoding="utf-8") as f:
    reviews_text = f.read()
print("Reviews loaded")
print(reviews_text[:300])

resume_text = documents[0].page_content
all_text = resume_text + "\n" + jd_text + "\n" + reviews_text
print("Combined text length:", len(all_text))

from langchain_text_splitters import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap = 100
)
chunks = text_splitter.split_text(all_text)
print("Total chunks:", len(chunks))
print(chunks[0])

from langchain_community.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
)
print("Embeddings loaded successfully")

from langchain_community.vectorstores import FAISS
vectorstore = FAISS.from_texts(chunks,embeddings)
print("Vector DB created successfully")

query = "What skills are required for AI Developer role?"

results = vectorstore.similarity_search(query,k=3)
for i, result in enumerate(results):
    print(f"\nResult {i+1}:")
    print(result.page_content[:500])

from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"))

query = "What interview questions can I expect for Accellor AI Developer role?"

results = vectorstore.similarity_search(query, k=3)
context = "\n\n".join([doc.page_content for doc in results])

prompt = f"""
You are a senior AI interview expert and hiring manager.

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