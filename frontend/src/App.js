import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Header from "./components/header";
import Menu from "./components/menu";
import MenuManagement from "./components/menuManagement";
import Orders from "./components/orders";
import AddOrder from "./components/addOrder";
import Reports from "./components/reports";
import InventoryManagement from "./components/inventoryManagement";

function App() {
    return (
        <Router>
            <Header />
            <Routes>
                <Route path="/orders/add" element={<AddOrder />} />
                <Route path="/menu" element={<Menu />} />
                <Route path="/orders" element={<Orders />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/menu-management" element={<MenuManagement />} />
                <Route path="/inventory-management" element={<InventoryManagement />} />
            </Routes>
        </Router>
    );
}

export default App;