import React from "react";
import { NavLink, useNavigate } from "react-router-dom";

const Header = () => {
    const navigate = useNavigate();

    const handleLogout = () => {
        sessionStorage.clear();
        navigate("/login");
    };

    return (
        <header>
            <nav>
                <NavLink to="/add-order">Add Order</NavLink>
                <NavLink to="/orders">Orders</NavLink>
                <NavLink to="/menu-management">Menu Management</NavLink>
                <NavLink to="/inventory-management">Inventory Management</NavLink>
                <NavLink to="/reports">Reports</NavLink>
                <button onClick={handleLogout}>Logout</button>
            </nav>
        </header>
    );
};

export default Header;
