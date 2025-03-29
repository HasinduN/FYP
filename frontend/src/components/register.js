import React, { useState, useContext } from "react";
import axios from "axios";
import { AuthContext } from "../context/authContext";
import "./authModal.css";

const Register = ({ closeModal }) => {
    const { user } = useContext(AuthContext);
    const [formData, setFormData] = useState({
        username: "",
        email: "",
        password: "",
        role: "cashier",
    });
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setError("");
        setSuccess("");

        try {
            const token = localStorage.getItem("token"); // Get auth token
    
            if (!token) {
                setError("Authentication failed. Please log in again.");
                return;
            }
    
            await axios.post("http://127.0.0.1:5000/auth/register", formData, {
                headers: { Authorization: `Bearer ${token}` }, // Send token in request
            });
    
            setSuccess("Registration successful!");
        } catch (err) {
            setError(err.response?.data?.msg || "An error occurred.");
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h2>Register</h2>
                {error && <p className="error">{error}</p>}
                {success && <p className="success">{success}</p>}
                <form onSubmit={handleRegister}>
                    <input type="text" name="username" placeholder="Username" onChange={handleChange} required />
                    <input type="email" name="email" placeholder="Email" onChange={handleChange} required />
                    <input type="password" name="password" placeholder="Password" onChange={handleChange} required />
                    <select name="role" onChange={handleChange}>
                        <option value="cashier">Cashier</option>
                        <option value="head cheff">Head Cheff</option>
                        <option value="cheff">Cheff</option>
                        <option value="waiter">Waiter</option>
                        <option value="manager">Manager</option>
                        <option value="admin">Admin</option>
                    </select>
                    <button type="submit">Register</button>
                </form>
                <button className="close-btn" onClick={closeModal}>Close</button>
            </div>
        </div>
    );
};

export default Register;
