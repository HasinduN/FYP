import React from "react";
import { Link } from "react-router-dom";
import "./header.css"; // Import CSS file for styling

const Header = () => {
    return (
        <header className="header">
            <div className="logo">
                <h2>EDEN DINE</h2>
            </div>
            <nav className="nav">
                <Link to="/add-order">Add Order</Link>
                <Link to="/orders">Orders</Link>
                <Link to="/menu">Menu</Link>
                <Link to="/menu-management">Menu Management</Link>
                <Link to="/inventory-management">Inventory Management</Link>
                <Link to="/reports">Reports</Link>
            </nav>
        </header>
    );
};

export default Header;