import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/header";
import AddOrder from "./components/addOrder";
import Orders from "./components/orders";
import Menu from "./components/menu";
import MenuManagement from "./components/menuManagement";
import InventoryManagement from "./components/inventoryManagement";
import SalesReport from "./components/salesReport";
import InventoryReport from "./components/inventoryReport";

const App = () => {
    return (
        <Router>
            <Header />
            <Routes>
                <Route path="/add-order" element={<AddOrder />} />
                <Route path="/orders" element={<Orders />} />
                <Route path="/menu" element={<Menu />} />
                <Route path="/menu-management" element={<MenuManagement />} />
                <Route path="/inventory-management" element={<InventoryManagement />} />
                <Route path="/sales-report" element={<SalesReport />} />
                <Route path="/inventory-report" element={<InventoryReport />} />

                {/* Default Route */}
                <Route path="*" element={<AddOrder />} />
            </Routes>
        </Router>
    );
};

export default App;
