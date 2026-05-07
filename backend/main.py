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

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5000"], 
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type"])

# Initialize the client with your API key
client = genai.Client(api_key="AIzaSyDztGt6ZDIpmj3N-56GDt_CwIstbLwEXGc")


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

    #ML / NLP Model Logic here
    # Example: match_results = my_ml_model.predict(resume_text)
    
    # return jsonify({
    #     "status": "success",
    #     "raw_text_preview": resume_text[:200] 
    #     "extracted_skills": ["Python", "Data Science", "Flask"]
    #     "match_score": 92
    # })

    # return jsonify(resume_text)

    results = requests.get(
    "https://api.openwebninja.com/jsearch/search",
    headers={
      "x-api-key": "ak_gl43m34brq9m9b9vutakbmni61uyt79ot3esad9xz7pmi9z"
    },
    params={
      "query": "software engineer jobs in seattle"
    })
    
    jobs = results.json()['data']

    model = SentenceTransformer('all-MiniLM-L6-v2')

    resume_embedding = model.encode(resume_text, convert_to_tensor=True)

    job_description = jobs[0]['job_description']

    job_embedding = model.encode(job_description, convert_to_tensor=True)

    score = util.cos_sim(resume_embedding, job_embedding).item()

    # 3. Create the Agentic Prompt
    prompt = f"""
    You are a Career Strategist. Analyze the following resume against these target roles: {job_description}.
    
    Resume Text: {resume_text}
    
    Perform a deep-dive comparison between the [RESUME_TEXT] and [JOB_DESCRIPTION]. 

    1. **Match Score & Logic:** Provide a match percentage based on "Essential Requirements" vs. "Nice to Haves." Explain the reasoning.
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