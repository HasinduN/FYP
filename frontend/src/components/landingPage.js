import React, { useState } from "react";
import Login from "./login";
import Register from "./register";
import "./landingPage.css";

const LandingPage = () => {
    const [activeModal, setActiveModal] = useState(null); // Track active modal

    return (
        <div className="landing-container">
            <div className="overlay"></div>
            <div className="content">
                <h1>WELCOME</h1>

                <div className="button-group">
                    <button className="primary-btn" onClick={() => setActiveModal("login")}>
                        Login
                    </button>
                    <button className="secondary-btn" onClick={() => setActiveModal("register")}>
                        Register
                    </button>
                </div>
            </div>

            {/* Conditional Rendering of Modals */}
            {activeModal === "login" && <Login closeModal={() => setActiveModal(null)} />}
            {activeModal === "register" && <Register closeModal={() => setActiveModal(null)} />}
        </div>
    );
};

export default LandingPage;
