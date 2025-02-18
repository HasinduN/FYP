import React, { useState, useEffect } from "react";
import axios from "axios";
import "./inventoryReport.css";

const InventoryReport = () => {
    const [inventory, setInventory] = useState([]);
    const [lowStock, setLowStock] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchInventoryReport();
    }, []);

    const fetchInventoryReport = async () => {
        try {
            setLoading(true);
            const response = await axios.get("http://127.0.0.1:5000/inventory-report");
            setInventory(response.data.current_stock);
            setLowStock(response.data.low_stock_alerts);
        } catch (error) {
            console.error("Error fetching inventory report:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="inventory-container">
            <h1>Inventory Report</h1>

            {loading ? (
                <p>Loading inventory data...</p>
            ) : (
                <>
                    <h2>Current Stock Levels</h2>
                    <table className="inventory-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Item Name</th>
                                <th>Quantity</th>
                            </tr>
                        </thead>
                        <tbody>
                            {inventory.map((item) => (
                                <tr key={item.id}>
                                    <td>{item.id}</td>
                                    <td>{item.name}</td>
                                    <td>{item.quantity}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    <h2>Low Stock Alerts</h2>
                    {lowStock.length > 0 ? (
                        <table className="inventory-table low-stock">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Item Name</th>
                                    <th>Quantity</th>
                                </tr>
                            </thead>
                            <tbody>
                                {lowStock.map((item) => (
                                    <tr key={item.id}>
                                        <td>{item.id}</td>
                                        <td>{item.name}</td>
                                        <td>{item.quantity}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <p>No low stock alerts.</p>
                    )}
                </>
            )}
        </div>
    );
};

export default InventoryReport;