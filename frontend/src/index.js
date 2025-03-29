import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router } from "react-router-dom"; // ✅ Correct usage
import "./index.css";
import App from "./App";
import reportWebVitals from "./reportWebVitals";
import { AuthProvider } from "./context/authContext";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <Router> {/* ✅ ONLY ONE Router */}
    <AuthProvider>
      <App />
    </AuthProvider>
  </Router>
);

reportWebVitals();
