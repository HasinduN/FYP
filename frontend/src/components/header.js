import React, { useState, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/authContext";
import logo from "../assets/logo.jpg";
import "./header.css";

const Header = () => {
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();
    const [showReports, setShowReports] = useState(false);

    const handleLogout = async () => {
        await logout();
        navigate("/login");
    };

    return (
        <header className="header">
            <div className="logo">
                <img src={logo} alt="Eden Dine Logo" className="logo-img" />
            </div>
            <nav className="nav">
                <Link to="/add-order">ADD ORDER</Link>
                <Link to="/orders">ORDERS</Link>

                {/* Only show menu management to admins */}
                {user?.role === "admin" && <Link to="/menu-management">MENU</Link>}

                {/* Only admins & managers can access inventory */}
                {(user?.role === "admin" || user?.role === "manager") && (
                    <Link to="/inventory-management">INVENTORY</Link>
                )}

                <div className="reports-dropdown">
                    <button className="reports-button" onClick={() => setShowReports(!showReports)}>
                        REPORTS
                    </button>
                    {showReports && (
                        <div className="reports-menu">
                            <Link to="/sales-report">SALES REPORT</Link>
                            <Link to="/inventory-report">INVENTORY REPORT</Link>
                        </div>
                    )}
                </div>

                <button className="logout-btn" onClick={handleLogout}>LOGOUT</button>
            </nav>
        </header>
    );
};

export default Header;
