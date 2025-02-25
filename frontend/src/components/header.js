import React, { useState } from "react";
import { Link } from "react-router-dom";
import logo from "..//assets/logo.jpg";
import "./header.css"; // Import CSS file for styling

const Header = () => {
    const [showReports, setShowReports] = useState(false);

    return (
        <header className="header">
            <div className="logo">
                <img src={logo} alt="Eden Dine Logo" className="logo-img" />    
            </div>
            <nav className="nav">
                <Link to="/add-order">ADD ORDER</Link>
                <Link to="/orders">ORDERS</Link>
                <Link to="/menu-management">MENU</Link>
                <Link to="/inventory-management">INVENTORY</Link>

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
            </nav>
        </header>
    );
};

export default Header;