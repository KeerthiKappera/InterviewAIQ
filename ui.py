import streamlit as st
import requests

st.set_page_config(page_title="AI Interview Prep", layout="wide")


st.title("🚀 AI Interview Preparation Assistant")
st.markdown("Upload Resume + Paste JD + Get Personalized Interview Questions")

resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
company = st.text_input("Company Name")
role = st.text_input("Role")
jd = st.text_area("Paste Job Description", height=250)

if st.button("Generate Interview Prep"):

    if resume is None:
        st.error("Please upload resume")
    elif not company.strip() or not role.strip() or not jd.strip():        
        st.error("Please fill all fields")
    else:
        files = {
            "resume": (resume.name, resume, "application/pdf")
        }

        data = {
            "company": company,
            "role": role,
            "jd": jd
        }
        progress = st.progress(0)
        try:
            with st.spinner("Reading Resume... Matching JD... Analyzing Company Patterns..."):
                progress.progress(25)
                response = requests.post(
                    "http://127.0.0.1:8000/generate",
                    files=files,
                    data=data
                )
                progress.progress(75)

            #st.write("Status Code:", response.status_code)
            #st.write("Raw Response:", response.text)

            result = response.json()

            if response.status_code == 200:
                if "error" in result:
                    st.error(result["error"])
                elif "response" in result:
                    progress.progress(100)
                    progress.empty()
                    st.success("Interview Prep Generated Successfully!")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Resume Match", f'{result["resume_match"]}%')

                    with col2:
                        st.metric("Missing Skills", result["missing_skills"])

                    with col3:
                        st.metric("Questions", result["question_count"])

                    st.markdown("### Top Matched Skills")

                    skills_text = " | ".join([skill.upper() for skill in result["matched_skills"]])
                    st.info(skills_text)

                    st.subheader("Final Recommendation")

                    if result["resume_match"] >= 85:
                        st.success(result["recommendation"])
                    elif result["resume_match"] >= 70:
                        st.info(result["recommendation"])
                    else:
                        st.warning(result["recommendation"])

                    st.markdown("### Match Analysis")
                    st.write("Resume Match Score")
                    st.progress(result["resume_match"] / 100)

                    st.write("Preparation Readiness")
                    readiness_score = min(result["resume_match"] + 10, 100)
                    st.progress(readiness_score / 100)

                    if result.get("reviews"):
                        with st.expander("Company Interview Insights"):
                            st.write(result["reviews"])

                    report = result["response"]

                    report = report.replace("TECHNICAL QUESTIONS", "🔹 TECHNICAL QUESTIONS")
                    report = report.replace("BEHAVIORAL QUESTIONS", "🔹 BEHAVIORAL QUESTIONS")
                    report = report.replace("SCENARIO BASED QUESTIONS", "🔹 SCENARIO BASED QUESTIONS")
                    report = report.replace("CODING QUESTIONS", "🔹 CODING QUESTIONS")
                    report = report.replace("PERSONALIZED QUESTIONS FROM RESUME", "🔹 PERSONALIZED QUESTIONS FROM RESUME")
                    report = report.replace("IMPORTANT TOPICS TO PREPARE", "🔥 IMPORTANT TOPICS TO PREPARE")
                    report = report.replace("MISSING SKILLS IN RESUME", "⚠️ MISSING SKILLS IN RESUME")
                    report = report.replace("TOP 5 SAMPLE STRONG ANSWERS", "✅ TOP 5 SAMPLE STRONG ANSWERS")

                    with st.expander("View Full Report", expanded=True):
                        st.markdown(report)
                        
                    st.download_button(
                        label="Download Report",
                        data=result["response"],
                        file_name=f"{company.replace(' ','_')}_{role.replace(' ','_')}_InterviewPrep.txt",
                        mime="text/plain"
                    )
                    
                else:
                    st.error(f"No response key found. Got: {result}")
            else:
                st.error(f"Backend error: {result}")

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")

