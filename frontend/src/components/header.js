import React from "react";
import { Link } from "react-router-dom";
import "./header.css";

const Header = () => {
    return (
        <header className="header">
            <Link to="/" className="header-logo">
                POS System
            </Link>
            <nav className="nav-links">
                <Link to="/menu">Menu</Link>
                <Link to="/menu-management">Menu Management</Link>
                <Link to="/orders">Orders</Link>
                <Link to="/orders/add">Add Order</Link>
                <Link to="/reports">Reports</Link>
            </nav>
        </header>
    );
};

export default Header;