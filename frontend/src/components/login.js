import React, { useState, useContext } from "react";
import { AuthContext } from "../context/authContext";
import "./authModal.css";

const Login = ({ closeModal }) => {
    const { login } = useContext(AuthContext);
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const handleLogin = async (e) => {
        e.preventDefault();
        setError("");

        try {
            await login(username, password);
            closeModal();
        } catch (err) {
            setError("Invalid credentials. Please try again.");
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h2>Login</h2>
                {error && <p className="error">{error}</p>}
                <form onSubmit={handleLogin}>
                    <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
                    <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                    <button type="submit">Login</button>
                </form>
                <button className="close-btn" onClick={closeModal}>Close</button>
            </div>
        </div>
    );
};

export default Login;
