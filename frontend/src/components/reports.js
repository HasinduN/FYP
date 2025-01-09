import React, { useState, useEffect } from "react";
import axios from "axios";
import "./reports.css";

const Reports = () => {
    const [salesReport, setSalesReport] = useState(null);
    const [inventoryReport, setInventoryReport] = useState(null);

    useEffect(() => {
        const fetchSalesReport = async () => {
            try {
                const response = await axios.get("http://127.0.0.1:5000/reports/sales");
                console.log("Sales Report Data:", response.data); // Log the data
                setSalesReport(response.data);
            } catch (error) {
                console.error("Error fetching sales report:", error);
            }
        };
    
        const fetchInventoryReport = async () => {
            try {
                const response = await axios.get("http://127.0.0.1:5000/reports/inventory");
                console.log("Inventory Report Data:", response.data); // Log the data
                setInventoryReport(response.data);
            } catch (error) {
                console.error("Error fetching inventory report:", error);
            }
        };
    
        fetchSalesReport();
        fetchInventoryReport();
    }, []);

    return (
        <div className="reports-container">
            <h1>Reports</h1>

            <h2>Sales Report</h2>
            {salesReport && (
                <div>
                    <p>Total Revenue: ${salesReport.total_revenue.toFixed(2)}</p>
                    <p>Total Orders: {salesReport.total_orders}</p>
                    <h3>Revenue by Order Type:</h3>
                    <ul>
                        {salesReport.revenue_by_type.map((type) => (
                            <li key={type.type}>
                                {type.type}: ${type.revenue.toFixed(2)}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            <h2>Inventory Report</h2>
            {inventoryReport && (
                <div>
                    <table>
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th>Quantity</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {inventoryReport.map((item, index) => (
                                <tr key={index}>
                                    <td>{item.name}</td>
                                    <td>{item.quantity}</td>
                                    <td>{item.status}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default Reports;