from pydoc import text

import pdfplumber
import io
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

import requests
from sentence_transformers import SentenceTransformer, util

from google import genai
import os
import json

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5000"], 
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type"])

# Load API Keys from environmentvariables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPEN_WEB_NINJA_API_KEY = os.getenv("OPEN_WEB_NINJA_API_KEY")
OPEN_WEB_NINJA_API_URL = os.getenv("OPEN_WEB_NINJA_API_URL")

# Initialize the Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


def extract_text_from_pdf(file_stream):
    """Extracts text from a file-like object using pdfplumber."""
    text = ""
    with pdfplumber.open(io.BytesIO(file_stream.read())) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                # Remove URLs and Emails
                text = re.sub(r'\S+@\S+', '', text)
                text = re.sub(r'http\S+|www\S+', '', text)
                
                # Remove special characters but keep '+', '.', and '#' for tech terms
                # This regex removes most symbols but leaves alphanumeric and specific tech chars
                text = re.sub(r'[^a-zA-Z0-9\s+#.]', '', text)

                # Remove extra whitespace
                text = re.sub(r'\s+', ' ', text).strip()

    return text


@app.route('/api/upload-resume', methods=['POST'])
def process_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['resume']
    role = request.form.get('role', '')
    city = request.form.get('city', '')
    
    # 1. Extract the text
    resume_text = extract_text_from_pdf(file)
    
    if not resume_text.strip():
        return jsonify({"error": "Could not extract text from PDF"}), 422

    results = requests.get(
    OPEN_WEB_NINJA_API_URL,
    headers={
      "x-api-key": OPEN_WEB_NINJA_API_KEY
    },
    params={
      "query": "" + role + " jobs in " + city
    })
    
    jobs = results.json()['data']

    model = SentenceTransformer('all-MiniLM-L6-v2')

    resume_embedding = model.encode(resume_text, convert_to_tensor=True)

    
    for i in range(5):
        job_description = jobs[i]['job_description']
        job_title = jobs[i]['job_title']
        job_apply_link = jobs[i]['job_apply_link']
        job_embedding = model.encode(job_description, convert_to_tensor=True)
        score = util.cos_sim(resume_embedding, job_embedding).item()

        # 3. Create the Agentic Prompt
        prompt = f"""
        You are a Career Strategist. Analyze the following resume against these target roles: {job_description}.
    
        Resume Text: {resume_text}
    
        Perform a deep-dive comparison between the [RESUME_TEXT] and [JOB_DESCRIPTION]. 

        1. **Matching Logic:** Provide how the skills and experiences in the resume show matching and qualifications to the job provided based on "Essential Requirements" vs. "Nice to Haves." Explain the reasoning.
        2. **Missing Pillars:** List the top 3-5 critical skills or certifications missing.
        3. **Resume "Reframing" Suggestions:** For every 2 missing skills, suggest one way to rewrite an existing bullet point in the resume to imply that skill or show transferable experience.
        4. **Pivot Strategy:** If the user is missing more than 40% of the requirements, provide a "Bridge Plan"—a list of 3 actionable steps (e.g., a specific type of project or a certification) to make this resume competitive within 30 days.

        ### OUTPUT FORMAT
        Return the analysis in a clean JSON-like structure or Markdown with the following headers: 
        - Analysis Summary
        - Critical Gaps
        - Optimization Recommendations
        - Strategic Pivot Plan
        """

        # 4. Generate Content
        response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    
    return jsonify(response.text)

    # print(round(score * 100, 1)


if __name__ == '__main__':
    app.run(port=5000, debug=True)