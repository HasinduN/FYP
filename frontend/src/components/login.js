import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./login.css";

const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post("http://127.0.0.1:5000/login", {
                username,
                password,
            });
    
            if (response.data.username && response.data.role) {
                sessionStorage.setItem("username", response.data.username);
                sessionStorage.setItem("role", response.data.role);
    
                // Redirect to respective home page based on role
                if (response.data.role === "manager") {
                    navigate("/home");
                } else if (response.data.role === "cashier") {
                    navigate("/home");
                } else {
                    navigate("/login");  // Fallback to login if something goes wrong
                }
            } else {
                setError("Invalid response from server");
            }
        } catch (error) {
            setError("Invalid username or password. Please try again.");
        }
    };
    

    return (
        <div className="login-container">
            <h1>Login</h1>
            {error && <p className="error">{error}</p>}
            <form onSubmit={handleLogin}>
                <div className="form-group">
                    <label>Username:</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Password:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">Login</button>
            </form>
        </div>
    );
};

export default Login;