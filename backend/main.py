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

# Define the schema to match your exact requirements
response_schema = {
    "type": "OBJECT",
    "properties": {
        "Matching Score": {"type": "NUMBER"},
        "Analysis": {"type": "STRING"},
        "Critical Gaps": {"type": "ARRAY", "items": {"type": "STRING"}},
        "Optimization Recommendations": {"type": "ARRAY", "items": {"type": "STRING"}},
        "Strategic Pivot Plan": {"type": "STRING"}
    },
    "required": [
        "Matching Score", 
        "Analysis", 
        "Critical Gaps", 
        "Optimization Recommendations", 
        "Strategic Pivot Plan"
    ]
}


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
      "query": "" + role + " jobs in " + city,
      "job_requirements": "under_3_years_experience"
    })
    
    jobs = results.json()['data']

    # model = SentenceTransformer('all-MiniLM-L6-v2')

    # resume_embedding = model.encode(resume_text, convert_to_tensor=True)

    results_analysis = []

    
    for i in range(5):
        job_description = jobs[i]['job_description']
        job_title = jobs[i]['job_title']
        job_apply_link = jobs[i]['job_apply_link']
        job_posted_at_datetime_utc = jobs[i]['job_posted_at_datetime_utc']
        # job_embedding = model.encode(job_description, convert_to_tensor=True)
        # score = util.cos_sim(resume_embedding, job_embedding).item()

        # 3. Create the Agentic Prompt
        prompt = f"""
        Act as a Career Strategist. Analyze the following resume text against the user's references.
        Focus on transferable skills and provide a candid reality check.

        Resume Text: {resume_text}
        Target Roles: {job_description}

        Provide a deep-dive analysis including specific technical gaps and a pivot plan 
        if the candidate is not a direct match.
        """

        # 4. Generate Content
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config={
            "response_mime_type": "application/json",
            "response_schema": response_schema
            }, 
            contents=prompt)

        raw_text = response.text.replace("```json", "").replace("", "").strip()

        try:
            # 2. Convert the string into a temporary dictionary
            ai_data = json.loads(raw_text)
    
            # 3. Append to your results_analysis list
            results_analysis.append({
                "id": i,
                "job_title": job_title,
                "job_apply_link": job_apply_link,
                "job_posted_at_datetime_utc": job_posted_at_datetime_utc,
                # Use .get() to prevent crashes if the AI slightly changes a key name
                "matching_score": ai_data.get("Matching Score"),
                "analysis": ai_data.get("Analysis"),
                "critical_gaps": ai_data.get("Critical Gaps"),
                "optimization_recommendations": ai_data.get("Optimization Recommendations"),
                "strategic_pivot_plan": ai_data.get("Strategic Pivot Plan")
            })

        except json.JSONDecodeError as e:
            print(f"Error parsing AI response for job {i}: {e}")
            # Optional: Append a dictionary with error info so the loop continues
            results_analysis.append({
                "id": i,
                "job_title": job_title,
                "error": "Could not parse AI analysis"
            })

    #     results_analysis.append({
    #         "id": i,
    #         "job_title": job_title,
    #         "job_apply_link": job_apply_link,
    #         "job_posted_at_datetime_utc": job_posted_at_datetime_utc,
    #         "matching_score": response.value["Matching Score"],
    #         "analysis": response.value["Analysis"],
    #         "critical_gaps": response.value["Critical Gaps"],
    #         "optimization_recommendations": response.value["Optimization Recommendations"],
    #         "strategic_pivot_plan": response.value["Strategic Pivot Plan"]
    #     }
    # )
    return jsonify(results_analysis)
        
if __name__ == '__main__':
    app.run(port=5000, debug=True)