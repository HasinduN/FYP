import React, { useState, useEffect } from "react";
import axios from "axios";
import { saveAs } from "file-saver";
import "./inventoryReport.css";

const InventoryReport = () => {
    const [lowStock, setLowStock] = useState([]);
    const [stockUpdates, setStockUpdates] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchInventoryReport();
    }, []);

    const fetchInventoryReport = async () => {
        try {
            setLoading(true);
            const response = await axios.get("http://127.0.0.1:5000/inventory-report");
            setLowStock(response.data.low_stock_alerts || []);
            setStockUpdates(response.data.stock_updates || []);
        } catch (error) {
            console.error("Error fetching inventory report:", error);
        } finally {
            setLoading(false);
        }
    };

    const downloadReport = () => {
        const csvContent = [
            ["Item ID", "Item Name", "Quantity", "Unit", "Updated Date"],
            ...(Array.isArray(stockUpdates) ? stockUpdates.map((item) => [
                item.id,
                item.item_name,
                item.added_quantity,
                item.unit,
                new Date(item.added_date).toLocaleString()
            ]) : [])
        ]
        .map((row) => row.join(","))
        .join("\n");

        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        saveAs(blob, "InventoryReport.csv");
    };

    return (
        <div className="inventory-container">
            <h1>INVENTORY REPORT</h1>

            {loading ? (
                <p>Loading inventory data...</p>
            ) : (
                <>
                    <div className="head">
                        <h2>Recent Stock Updates</h2>
                        <button className="download-btn" onClick={downloadReport}>Download CSV</button>
                    </div>

                    {stockUpdates.length > 0 ? (
                        <div className="table-wrapper">
                            <table className="inventory-table">
                                <thead>
                                    <tr>
                                        <th>Item ID</th>
                                        <th>Item Name</th>
                                        <th>Quantity</th>
                                        <th>Unit</th>
                                        <th>Updated Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {stockUpdates.map((item) => (
                                        <tr key={item.id}>
                                            <td>{item.id}</td>
                                            <td>{item.item_name}</td>
                                            <td>{item.added_quantity}</td>
                                            <td>{item.unit}</td>
                                            <td>{new Date(item.added_date).toLocaleString()}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <p>No recent stock updates.</p>
                    )}

                    <div className="head">
                    <h2>Low Stock Alerts</h2>
                    </div>
                    {lowStock.length > 0 ? (
                        <div className="table-wrapper">
                            <table className="inventory-table low-stock">
                                <thead>
                                    <tr>
                                        <th>Item ID</th>
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
                        </div>
                    ) : (
                        <p>No low stock alerts.</p>
                    )}
                </>
            )}
        </div>
    );
};

export default InventoryReport;
