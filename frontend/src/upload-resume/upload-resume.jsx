import React from "react";
import { useState } from "react";
import "./upload-resume.css";

export default function UploadResume() {
  const [resume, setResume] = useState(null);
  const [role, setRole] = useState("");
  const [city, setCity] = useState("");
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
    if (!role) return alert("Please enter a preferred job title");
    if (!city) return alert("Please enter a preferred city");

    setLoading(true);
    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("role", role);
    formData.append("city", city);
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

  const scoreBadgeClass = (score) => {
    if (score >= 80) return "score-badge s-high";
    if (score >= 60) return "score-badge s-mid";
    return "score-badge s-low";
  };

  return (
    // Wrap your component's outer div:
    <div className="app-wrapper">
      {/* Header */}
      <div className="dashboard-header">
        <h1>
          Find Your <span>Perfect Match</span>
        </h1>
        <p>Upload your résumé · pick a role & city · we do the rest</p>
      </div>

      {/* Form card */}
      <div className="upload-card">
        <div className="field-group">
          <div className="field-label">
            <span className="label-num">1</span> Résumé
          </div>
          <div className="file-drop-zone">
            <input
              type="file"
              id="resume"
              accept=".pdf"
              onChange={handleFileChange}
            />
            <span className="file-drop-icon">📄</span>
            <div className="file-drop-text">
              Drop your PDF here or <strong>browse</strong>
            </div>
            {resume && (
              <div className="file-selected-badge">✓ {resume.name}</div>
            )}
          </div>
        </div>

        <div className="fields-row">
          <div className="field-group">
            <div className="field-label">
              <span className="label-num">2</span> Preferred Role
            </div>
            <input
              className="text-input"
              type="text"
              placeholder="Software Engineer"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            />
          </div>
          <div className="field-group">
            <div className="field-label">
              <span className="label-num">3</span> Preferred City
            </div>
            <input
              className="text-input"
              type="text"
              placeholder="Seattle"
              value={city}
              onChange={(e) => setCity(e.target.value)}
            />
          </div>
        </div>

        <button
          className="submit-btn"
          onClick={handleUpload}
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner"></span> Analysing…
            </>
          ) : (
            "Start Matching"
          )}
        </button>
      </div>

      {/* Results */}
      {results && (
        <div>
          <div className="section-divider">
            <span>Results</span>
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: "12px",
              marginBottom: "24px",
            }}
          >
            <div>
              <h2 className="results-heading">
                Here are what we found for you
              </h2>
              <p className="results-subheading">
                {role} &nbsp;·&nbsp; {city} &nbsp;·&nbsp; {results.length}{" "}
                matches
              </p>
            </div>
          </div>

          {results.map((result) => (
            <div className="result-card" key={result.id}>
              {/* Title + match score badge */}
              <div className="result-card-header">
                <div className="result-job-title">{result.job_title}</div>
                <div className="match-badge">
                  {result.matching_score}% Match
                </div>
              </div>

              {/* Date + apply link */}
              <div className="result-meta">
                <div className="result-meta-item">
                  <i className="ti ti-calendar" aria-hidden="true" />
                  {new Date(
                    result.job_posted_at_datetime_utc,
                  ).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  })}
                </div>
              </div>

              <a
                className="result-link"
                href={result.job_apply_link}
                target="_blank"
                rel="noreferrer"
              >
                <i className="ti ti-external-link" aria-hidden="true" />
                {result.job_apply_link}
              </a>

              <div className={scoreBadgeClass(result.matching_score)}>
                {result.matching_score}% Match
              </div>

              {/* Analysis */}
              <div className="result-analysis">{result.analysis}</div>

              {/* Critical Gaps */}
              <div className="result-analysis" style={{ marginTop: "12px" }}>
                <strong
                  style={{
                    color: "#eaedf5",
                    fontSize: "0.78rem",
                    letterSpacing: "0.06em",
                    textTransform: "uppercase",
                  }}
                >
                  Critical Gaps
                </strong>
                <p style={{ marginTop: "6px" }}>{result.critical_gaps}</p>
              </div>

              {/* Optimization Recommendations */}
              <div
                className="result-analysis"
                style={{ borderTop: "none", paddingTop: "0" }}
              >
                <strong
                  style={{
                    color: "#eaedf5",
                    fontSize: "0.78rem",
                    letterSpacing: "0.06em",
                    textTransform: "uppercase",
                  }}
                >
                  Optimization Recommendations
                </strong>
                <p style={{ marginTop: "6px" }}>
                  {result.optimization_recommendations}
                </p>
              </div>

              {/* Strategic Pivot Plan */}
              <div
                className="result-analysis"
                style={{ borderTop: "none", paddingTop: "0" }}
              >
                <strong
                  style={{
                    color: "#eaedf5",
                    fontSize: "0.78rem",
                    letterSpacing: "0.06em",
                    textTransform: "uppercase",
                  }}
                >
                  Strategic Pivot Plan
                </strong>
                <p style={{ marginTop: "6px" }}>
                  {result.strategic_pivot_plan}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
