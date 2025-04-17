import React, { useState } from "react";
import Login from "./login";
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
                </div>
            </div>

            {activeModal === "login" && <Login closeModal={() => setActiveModal(null)} />}
        </div>
    );
};

export default LandingPage;
