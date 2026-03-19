import { useState } from "react";
import { Routes, Route } from "react-router";
import "./App.css";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<h1>AI Career</h1>} />
    </Routes>
  );
}
