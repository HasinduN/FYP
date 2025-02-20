import React, { useState, useEffect } from "react";
import axios from "axios";
import "./inventoryReport.css";

const InventoryReport = () => {
    const [lowStock, setLowStock] = useState([]);
    const [stockAdditions, setStockAdditions] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchInventoryReport();
    }, []);

    const fetchInventoryReport = async () => {
        try {
            setLoading(true);
            const response = await axios.get("http://127.0.0.1:5000/inventory-report");
            setLowStock(response.data.low_stock_alerts);
            setStockAdditions(response.data.stock_additions);
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
                    {/* Recent Stock Additions */}
                    <h2>Inventory Report</h2>
                    {stockAdditions.length > 0 ? (
                        <table className="inventory-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Item Name</th>
                                    <th>Added Quantity</th>
                                    <th>Unit</th>
                                    <th>Added Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {stockAdditions.map((log) => (
                                    <tr key={log.id}>
                                        <td>{log.id}</td>
                                        <td>{log.item_name}</td>
                                        <td>{log.added_quantity}</td>
                                        <td>{log.unit}</td>
                                        <td>{new Date(log.added_date).toLocaleString()}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <p>No recent stock additions.</p>
                    )}

                    {/* Low Stock Alerts */}
                    <h2>Low Stock Alerts</h2>
                    {lowStock.length > 0 ? (
                        <table className="inventory-table low-stock">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Item Name</th>
                                    <th>Quantity</th>
                                    <th>Unit</th>
                                </tr>
                            </thead>
                            <tbody>
                                {lowStock.map((item) => (
                                    <tr key={item.id}>
                                        <td>{item.id}</td>
                                        <td>{item.name}</td>
                                        <td>{item.quantity}</td>
                                        <td>{item.unit}</td>
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
