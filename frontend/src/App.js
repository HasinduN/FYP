import React, { useContext, useEffect } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthContext } from "./context/authContext";

import LandingPage from "./components/landingPage";
import AddOrder from "./components/addOrder";
import Orders from "./components/orders";
import MenuManagement from "./components/menuManagement";
import InventoryManagement from "./components/inventoryManagement";
import SalesReport from "./components/salesReport";
import InventoryReport from "./components/inventoryReport";
import Sidebar from "./components/sidebar";

const ProtectedRoute = ({ element, allowedRoles }) => {
    const { user } = useContext(AuthContext);
    const role = localStorage.getItem("role");

    if (!user) {
        return <Navigate to="/" />;
    }

    if (!allowedRoles.includes(role)) {
        return <Navigate to="/unauthorized" />;
    }

    return element;
};

const App = () => {
    const { user } = useContext(AuthContext);
    const location = useLocation();
    const isLandingPage = location.pathname === "/";

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/";
        }
    }, []);

    return (
        <div className={`app-container ${isLandingPage ? "no-sidebar" : ""}`}>
            {!isLandingPage && user && <Sidebar />}

            <div className={`main-content ${isLandingPage ? "full-width" : ""}`}>
                <Routes>
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/add-order" element={<ProtectedRoute element={<AddOrder />} allowedRoles={["admin", "manager", "cashier", "waiter"]} />} />
                    <Route path="/orders" element={<ProtectedRoute element={<Orders />} allowedRoles={["admin", "manager", "cashier", "head cheff", "cheff"]} />} />
                    <Route path="/menu-management" element={<ProtectedRoute element={<MenuManagement />} allowedRoles={["admin"]} />} />
                    <Route path="/inventory-management" element={<ProtectedRoute element={<InventoryManagement />} allowedRoles={["admin", "manager", "head cheff"]} />} />
                    <Route path="/sales-report" element={<ProtectedRoute element={<SalesReport />} allowedRoles={["admin", "manager", "cashier"]} />} />
                    <Route path="/inventory-report" element={<ProtectedRoute element={<InventoryReport />} allowedRoles={["admin", "manager", "head cheff"]} />} />
                    <Route path="*" element={<Navigate to="/" />} />
                </Routes>
            </div>
        </div>
    );
};

export default App;
