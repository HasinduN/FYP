import React, { useState, useEffect } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./reports.css";

const Reports = () => {
    const [salesReport, setSalesReport] = useState(null);
    const [inventoryReport, setInventoryReport] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchReports();
    }, []);

    const fetchReports = async () => {
        try {
            setLoading(true);
            const salesResponse = await axios.get("http://127.0.0.1:5000/reports/sales");
            setSalesReport(salesResponse.data);

            const inventoryResponse = await axios.get(
                "http://127.0.0.1:5000/reports/inventory"
            );
            setInventoryReport(inventoryResponse.data);
        } catch (error) {
            toast.error("Error fetching reports!");
        } finally {
            setLoading(false);
        }
    };

    const downloadReport = (type) => {
        const url =
            type === "sales"
                ? "http://127.0.0.1:5000/reports/sales/download"
                : "http://127.0.0.1:5000/reports/inventory/download";
        window.open(url, "_blank");
    };

    return (
        <div className="reports-container">
            <ToastContainer />
            <header className="header">
                <h1>Reports</h1>
            </header>
            <div className="report-section">
                {loading ? (
                    <p>Loading reports...</p>
                ) : (
                    <>
                        <div className="report-card">
                            <h2>Sales Report</h2>
                            {salesReport && (
                                <>
                                    <p>Total Revenue: ${salesReport.total_revenue.toFixed(2)}</p>
                                    <p>Total Orders: {salesReport.total_orders}</p>
                                    <h4>Revenue by Type:</h4>
                                    <ul>
                                        {salesReport.revenue_by_type.map((type, index) => (
                                            <li key={index}>
                                                {type.type}: ${type.revenue.toFixed(2)}
                                            </li>
                                        ))}
                                    </ul>
                                    <button
                                        onClick={() => downloadReport("sales")}
                                        className="download-btn"
                                    >
                                        Download Sales Report
                                    </button>
                                </>
                            )}
                        </div>

                        <div className="report-card">
                            <h2>Inventory Report</h2>
                            {inventoryReport && (
                                <>
                                    <ul>
                                        {inventoryReport.map((item, index) => (
                                            <li key={index}>
                                                {item.name}: {item.quantity} units (
                                                {item.status})
                                            </li>
                                        ))}
                                    </ul>
                                    <button
                                        onClick={() => downloadReport("inventory")}
                                        className="download-btn"
                                    >
                                        Download Inventory Report
                                    </button>
                                </>
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default Reports;
