import React, { useContext, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthContext } from "./context/authContext";
import LandingPage from "./components/landingPage";
import AddOrder from "./components/addOrder";
import Orders from "./components/orders";
import MenuManagement from "./components/menuManagement";
import InventoryManagement from "./components/inventoryManagement";
import SalesReport from "./components/salesReport";
import InventoryReport from "./components/inventoryReport";
import Header from "./components/header";

const ProtectedRoute = ({ element, allowedRoles }) => {
    const { user } = useContext(AuthContext);
    const role = localStorage.getItem("role");

    if (!user) {
        return <Navigate to="/login" />;
    }

    if (!allowedRoles.includes(role)) {
        return <Navigate to="/unauthorized" />;
    }

    return element;
};

const App = () => {
    const { user } = useContext(AuthContext);

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/"; // Redirect to landing page on refresh
        }
    }, []);

    return (
        <>
            {user && <Header />}
            <Routes>
                <Route path="/" element={<LandingPage />} />

                {/* Role-based Access Control */}
                <Route path="/add-order" element={<ProtectedRoute element={<AddOrder />} allowedRoles={["admin", "cashier"]} />} />
                <Route path="/orders" element={<ProtectedRoute element={<Orders />} allowedRoles={["admin", "manager", "cashier"]} />} />
                <Route path="/menu-management" element={<ProtectedRoute element={<MenuManagement />} allowedRoles={["admin"]} />} />
                <Route path="/inventory-management" element={<ProtectedRoute element={<InventoryManagement />} allowedRoles={["admin", "manager"]} />} />
                <Route path="/sales-report" element={<ProtectedRoute element={<SalesReport />} allowedRoles={["admin", "manager"]} />} />
                <Route path="/inventory-report" element={<ProtectedRoute element={<InventoryReport />} allowedRoles={["admin", "manager"]} />} />

                {/* Default Route */}
                <Route path="*" element={<Navigate to="/" />} />
            </Routes>
        </>
    );
};

export default App;
