import React from "react";
import { useNavigate } from "react-router-dom";
import "./home.css";

const Home = () => {
    const navigate = useNavigate();
    const role = sessionStorage.getItem("role"); // Use sessionStorage instead of localStorage

    const handleLogout = () => {
        sessionStorage.clear();
        navigate("/login");
    };

    return (
        <div className="home-container">
            <h1>Welcome to the POS System</h1>
            <h3>Role: {role ? role.toUpperCase() : "Unknown"}</h3>
            <div className="functions">
                <button onClick={() => navigate("/add-order")}>Add Order</button>
                <button onClick={() => navigate("/menu")}>Menu</button>

                {role === "manager" && (
                    <>
                        <button onClick={() => navigate("/menu-management")}>Menu Management</button>
                        <button onClick={() => navigate("/inventory-management")}>Inventory Management</button>
                        <button onClick={() => navigate("/reports")}>Reports</button>
                        <button onClick={() => navigate("/user-management")}>User Management</button>
                    </>
                )}
            </div>
            <button className="logout-button" onClick={handleLogout}>
                Logout
            </button>
        </div>
    );
};

export default Home;