import React, { useState, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/authContext";
import logo from "../assets/logo.jpg";
import EditProfileModal from "../components/editProfileModal";
import Register from "../components/register";
import "./sidebar.css";

const Sidebar = () => {
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();
    const [showEditModal, setShowEditModal] = useState(false);
    const [showRegisterModal, setShowRegisterModal] = useState(false);
    const [showReports, setShowReports] = useState(false);

    const handleLogout = async () => {
        await logout();
        navigate("/login");
    };

    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <img src={logo} alt="Eden Dine Logo" />
            </div>

            <div className="user-info">
                <p className="username">{user?.username}</p>
                <p className="user-role">{user?.role}</p>
            </div>

            <nav className="nav">
                {(user?.role === "admin" || user?.role === "manager" || user?.role === "waiter" || user?.role === "cashier") && (
                    <Link to="/add-order">ADD ORDER</Link>
                )}
                {(user?.role === "admin" || user?.role === "manager" || user?.role === "head cheff" || user?.role === "cashier" || user?.role === "cheff") && (
                    <Link to="/orders">ORDERS</Link>
                )}
                {user?.role === "admin" && <Link to="/menu-management">MENU</Link>}
                {(user?.role === "admin" || user?.role === "manager" || user?.role === "head cheff") && (
                    <Link to="/inventory-management">INVENTORY</Link>
                )}

                {(user?.role !== "waiter") && (
                    <div className="reports-dropdown">
                        <button className="reports-button" onClick={() => setShowReports(!showReports)}>
                            REPORTS
                        </button>
                        {showReports && (
                            <div className="reports-menu">
                                {(user?.role === "admin" || user?.role === "manager" || user?.role === "cashier") && (
                                    <Link to="/sales-report">SALES REPORT</Link>
                                )}
                                {(user?.role === "admin" || user?.role === "manager" || user?.role === "head cheff") && (
                                    <Link to="/inventory-report">INVENTORY REPORT</Link>
                                )}
                            </div>
                        )}
                    </div>
                )}

                {(user?.role === "admin" || user?.role === "manager" || user?.role === "head cheff") && (
                    <Link to="/predictions">PREDICTIONS</Link>
                )}
            </nav>

            <div className="sidebar-bottom">
                {(user?.role === "admin") && (
                    <button className="register-btn" onClick={() => setShowRegisterModal(true)}>REGISTER</button>
                )}
                <button className="edit-profile-btn" onClick={() => setShowEditModal(true)}>EDIT PROFILE</button>
                <button className="logout-btn" onClick={handleLogout}>LOGOUT</button>
            </div>

            {showEditModal && <EditProfileModal onClose={() => setShowEditModal(false)} />}
            {showRegisterModal && <Register closeModal={() => setShowRegisterModal(false)} />}
        </aside>
    );
};

export default Sidebar;
