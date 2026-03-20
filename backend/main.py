import pdfplumber
import io
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5000"], 
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type"])

def extract_text_from_pdf(file_stream):
    """Extracts text from a file-like object using pdfplumber."""
    text = ""
    with pdfplumber.open(io.BytesIO(file_stream.read())) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

@app.route('/api/upload-resume', methods=['POST'])
def process_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['resume']
    
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

    return jsonify(resume_text)

if __name__ == '__main__':
    app.run(port=5000, debug=True)