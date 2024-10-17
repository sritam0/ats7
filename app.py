import os
import io
import requests
import streamlit as st
from dotenv import load_dotenv
import PyPDF2
import fitz


# Load environment variables
load_dotenv()

def get_gemini_response(input_text, pdf_text, prompt):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "API key is missing. Make sure it's set in the .env file."}
    
    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        "contents": [
            {
                "parts": [
                    {"text": input_text},
                    {"text": pdf_text},
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(f"{url}?key={api_key}", headers=headers, json=data)

    if response.status_code == 200:
        return response.json()  # Return the JSON response
    else:
        return {"error": response.text}  # Handle errors

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            pdf_bytes = uploaded_file.read()
            with io.BytesIO(pdf_bytes) as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            st.error(f"Error processing PDF: {e}")
            return None
    else:
        raise FileNotFoundError("No file uploaded")

def display_gemini_response(response):
    if "error" in response:
        st.error(response["error"])
    else:
        content = response['candidates'][0]['content']['parts'][0]['text']
        st.write("**Response Content:**")
        st.write(content)

# Main function to handle job description validation and process the resume
def handle_job_description_and_resume(input_text, pdf_text, prompt, submit_button):
    if not input_text:
        st.error("Please provide a job description before submitting.")
        return

    if submit_button:
        if uploaded_file is not None:
            pdf_text = input_pdf_setup(uploaded_file)
            if pdf_text:
                response = get_gemini_response(input_text, pdf_text, prompt)
                st.subheader("The Response is")
                display_gemini_response(response)
            else:
                st.error("Error extracting text from PDF.")
        else:
            st.write("Please upload the resume.")

# Streamlit App
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Input for job description
input_text = st.text_area("Job Description: ", key="input")

# File uploader for resume (PDF)
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

# Buttons to submit
submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage Match")

# Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description.
Please share your professional evaluation on whether the candidate's profile aligns with the role.
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
Your task is to evaluate the resume against the provided job description.
Give me the percentage of match if the resume matches the job description. First, the output should come as a percentage,
then keywords missing, and last, final thoughts.
"""

# Check for 'Tell Me About the Resume' button submission
if submit1:
    handle_job_description_and_resume(input_text, uploaded_file, input_prompt1, submit1)

# Check for 'Percentage Match' button submission
elif submit3:
    handle_job_description_and_resume(input_text, uploaded_file, input_prompt3, submit3)