import React from "react";
import { useState } from "react";

export default function UploadResume() {
  const ResumeAnalyzer = () => {
    const [resume, setResume] = useState(null);
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleFileChange = (e) => {
      setResume(e.target.files[0]);
    };

    const handleUpload = async () => {
      if (!resume) return alert("Please a resume file to upload.");

      setLoading(true);
      const formData = new FormData();
      formData.append("resume", resume);

      try {
        const response = await fetch(
          "http://127.0.0.1:5000/api/upload-resume",
          {
            method: "POST",
            body: formData,
          },
        );

        const data = await response.json();
        setResults(data);
      } catch (error) {
        console.error("Error uploading resume:", error);
      } finally {
        setLoading(false);
      }
    };
  };

  return (
    <div>
      <p>Upload resume here</p>
      <input
        type="file"
        id="resume"
        name="resume"
        accept=".pdf"
        onChange={handleFileChange}
      />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload"}
        Upload resume
      </button>

      {results && (
        <div className="results-card">
          <h2>Results for: {results.candidate_name}</h2>
          <p>Match Score: **{results.match_score}%**</p>
          <ul>
            {results.skills.map((skill, i) => (
              <li key={i}>{skill}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
