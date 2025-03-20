import React, { useState, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/authContext";
import logo from "../assets/logo.jpg";
import userIcon from "../assets/user.jpg";
import EditProfileModal from "../components/editProfileModal";
import "./header.css";

const Header = () => {
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();
    const [showProfileDropdown, setShowProfileDropdown] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [showReports, setShowReports] = useState(false);

    const toggleProfileDropdown = () => {
        setShowProfileDropdown(!showProfileDropdown);
    };

    const openEditModal = () => {
        setShowEditModal(true);
        setShowProfileDropdown(false);
    };

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

                <div className="user-profile">
                    <img src={userIcon} alt="User" className="user-icon" onClick={toggleProfileDropdown} />
                    {showProfileDropdown && (
                        <div className="profile-dropdown">
                            <p className="profile-info">{user?.username}</p>
                            <p className="profile-role">{user?.role}</p>
                            <button className="edit-profile-btn" onClick={openEditModal}>Edit Profile</button>
                            <button className="logout-btn" onClick={logout}>Logout</button>
                        </div>
                    )}
                </div>

            </nav>

            {/* Edit Profile Modal */}
            {showEditModal && <EditProfileModal onClose={() => setShowEditModal(false)} />}

        </header>
    );
};

export default Header;
