import React from "react";
import { useState } from "react";

export default function UploadResume() {
  const [resume, setResume] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      console.log("Selected file is here");
      setResume(file);
    } else {
      console.log("No file selected");
    }
  };

  const handleUpload = async () => {
    if (!resume) return alert("Please a resume file to upload.");

    setLoading(true);
    const formData = new FormData();
    formData.append("resume", resume);

    try {
      const response = await fetch("http://127.0.0.1:5000/api/upload-resume", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error("Error uploading resume:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <p>Upload resume here</p>
      <input
        type="file"
        id="resume"
        accept=".pdf"
        onChange={handleFileChange}
      />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload"}
      </button>
      {results && (
        <div className="results-card">
          <h2>Results for: someone</h2>
          <p>Match Score: 95</p>
          <ul>
            {results.extracted_skills.map((skill, i) => (
              <li key={i}>{skill}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
