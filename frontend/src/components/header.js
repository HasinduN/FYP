import React from "react";
import { Link } from "react-router-dom";
import "./header.css";

const Header = () => {
    return (
        <header className="header">
            <Link to="/" className="header-logo">
                EDEN DINE
            </Link>
            <nav className="nav-links">
                <Link to="/orders/add">ADD ORDER</Link>
                <Link to="/menu">MENU</Link>
                <Link to="/orders">ORDERS</Link>
                <Link to="/reports">REPORTS</Link>
                <Link to="/menu-management">MENU MANAGEMENT</Link>
                <Link to="/inventory-management">INVENTORY MANAGEMENT</Link>
            </nav>
        </header>
    );
};

export default Header;