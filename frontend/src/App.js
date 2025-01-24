import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./components/login";
import UserManagement from "./components/userManagement";
import Home from "./components/home";
import AddOrder from "./components/addOrder";
import Orders from "./components/orders";
import Menu from "./components/menu";
import MenuManagement from "./components/menuManagement";
import InventoryManagement from "./components/inventoryManagement";
import Reports from "./components/reports";

const App = () => {
    const isAuthenticated = sessionStorage.getItem("username");
    const role = sessionStorage.getItem("role");

    return (
        <Router>
            <Routes>
                {/* Login Route */}
                <Route path="/login" element={<Login />} />

                {isAuthenticated && role === "manager" && (
                    <Route path="/user-management" element={<UserManagement />} />
                )}

                {/* Protected Routes */}
                {isAuthenticated ? (
                    <>
                        {/* Home Route */}
                        <Route path="/home" element={<Home />} />

                        {/* Common Routes (for both Manager and Cashier) */}
                        <Route path="/add-order" element={<AddOrder />} />
                        <Route path="/orders" element={<Orders />} />
                        <Route path="/menu" element={<Menu />} />

                        {/* Manager-Only Routes */}
                        {role === "manager" && (
                            <>
                                <Route path="/menu-management" element={<MenuManagement />} />
                                <Route path="/inventory-management" element={<InventoryManagement />} />
                                <Route path="/reports" element={<Reports />} />
                            </>
                        )}
                    </>
                ) : (
                    // Redirect unauthorized users to login
                    <Route path="*" element={<Navigate to="/login" />} />
                )}
            </Routes>
        </Router>
    );
};

export default App;