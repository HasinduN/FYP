import React from "react";
import { useNavigate } from "react-router-dom";
import "./home.css";

const Home = () => {
    const navigate = useNavigate();
    const role = localStorage.getItem("role");

    const handleLogout = () => {
        localStorage.clear(); // Clear user data
        navigate("/login");  // Redirect to login page
    };

    return (
        <div className="home-container">
            <h1>Welcome to the POS System</h1>
            <h3>Role: {role}</h3>
            <div className="functions">
                {/* Common functions */}
                <button onClick={() => navigate("/add-order")}>Add Order</button>
                <button onClick={() => navigate("/menu")}>Menu</button>

                {/* Manager-only functions */}
                {role === "manager" && (
                    <>
                        <button onClick={() => navigate("/menu-management")}>
                            Menu Management
                        </button>
                        <button onClick={() => navigate("/inventory-management")}>
                            Inventory Management
                        </button>
                        <button onClick={() => navigate("/reports")}>Reports</button>
                        <button onClick={() => navigate("/user-management")}>
                            User Management
                        </button>
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