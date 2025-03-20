import React, { useState, useContext } from "react";
import { AuthContext } from "../context/authContext";
import axios from "axios";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./editProfileModal.css";

const EditProfileModal = ({ onClose }) => {
    const { user, fetchUser } = useContext(AuthContext);
    const [username, setUsername] = useState(user?.username || "");
    const [password, setPassword] = useState("");

    const handleSave = async () => {
        try {
            const token = localStorage.getItem("token");
            const response = await axios.put(
                "http://127.0.0.1:5000/auth/update-profile",
                { username, password },
                { headers: { Authorization: `Bearer ${token}` } }
            );
    
            if (response.status === 200) {
                toast.success("Profile updated successfully!");
                onClose(); // Close the modal after success
            } else {
                toast.error("Failed to update profile.");
            }
        } catch (error) {
            console.error("Error updating profile:", error);
            toast.error("Failed to update profile.");
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h2>Edit Profile</h2>
                <label>Username</label>
                <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />

                <label>New Password</label>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />

                <div className="modal-actions">
                    <button onClick={handleSave}>Save</button>
                    <button onClick={onClose}>Cancel</button>
                </div>
            </div>
        </div>
    );
};

export default EditProfileModal;
