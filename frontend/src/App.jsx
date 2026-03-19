import { useState } from "react";
import { Routes, Route } from "react-router";
import "./App.css";
import Home from "./home/home";
import UploadResume from "./upload-resume/upload-resume";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/resume" element={<UploadResume />} />
    </Routes>
  );
}
