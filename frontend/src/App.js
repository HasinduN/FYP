import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Header from "./components/header";
import Menu from "./components/menu";
import MenuManagement from "./components/menuManagement";
import Orders from "./components/orders";
import AddOrder from "./components/addOrder";

function App() {
    return (
        <Router>
            <Header />
            <Routes>
                <Route path="/menu" element={<Menu />} />
                <Route path="/menu-management" element={<MenuManagement />} />
                <Route path="/orders" element={<Orders />} />
                <Route path="/orders/add" element={<AddOrder />} />
            </Routes>
        </Router>
    );
}

export default App;