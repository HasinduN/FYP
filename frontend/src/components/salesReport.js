import React, { useEffect, useState } from "react";
import axios from "axios";
import { Bar, Pie, Line } from "react-chartjs-2";
import Chart from "chart.js/auto";
import "./salesReport.css";

const SalesReport = () => {
    const [reportData, setReportData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios.get("http://127.0.0.1:5000/sales-report")
            .then((response) => {
                setReportData(response.data);
                setLoading(false);
            })
            .catch((error) => {
                console.error("Error fetching sales report:", error);
                setError("Failed to load sales report.");
                setLoading(false);
            });
    }, []);

    if (loading) return <p>Loading Sales Report...</p>;
    if (error) return <p style={{ color: "red" }}>{error}</p>;

    const formatCurrency = (amount) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "LKR" }).format(amount);

    return (
        <div style={{ padding: "20px" }}>
            <h1>Sales Report</h1>

            {/* Daily Sales Table */}
            <h2>Daily Sales Summary</h2>
            <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: "20px" }}>
                <thead>
                    <tr style={{ background: "#f4f4f4" }}>
                        <th>Date</th>
                        <th>Total Sales</th>
                        <th>Total Orders</th>
                        <th>Avg Order Value</th>
                    </tr>
                </thead>
                <tbody>
                    {reportData?.daily_sales?.map((row, index) => (
                        <tr key={index}>
                            <td>{row.date}</td>
                            <td>{formatCurrency(row.total_sales)}</td>
                            <td>{row.total_orders}</td>
                            <td>{formatCurrency(row.avg_order_value)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* Top-Selling Items */}
            <h2>Top-Selling Items</h2>
            <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: "20px" }}>
                <thead>
                    <tr style={{ background: "#f4f4f4" }}>
                        <th>Item Name</th>
                        <th>Total Sold</th>
                        <th>Revenue Generated</th>
                    </tr>
                </thead>
                <tbody>
                    {reportData?.top_items?.map((row, index) => (
                        <tr key={index}>
                            <td>{row.item_name}</td>
                            <td>{row.total_sold}</td>
                            <td>{formatCurrency(row.revenue_generated)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* Sales Trend Line Chart */}
            <h2>Sales Trends (Last 7 Days)</h2>
            <div style={{ width: "100%", height: "300px" }}>
                <Line
                    data={{
                        labels: reportData?.sales_trends?.map((row) => row.date),
                        datasets: [
                            {
                                label: "Sales Amount (Rs.)",
                                data: reportData?.sales_trends?.map((row) => row.sales_amount),
                                backgroundColor: "rgba(54, 162, 235, 0.5)",
                                borderColor: "rgba(54, 162, 235, 1)",
                            },
                        ],
                    }}
                    options={{ maintainAspectRatio: false }}
                />
            </div>

            {/* Sales by Order Type */}
            <h2>Sales by Order Type</h2>
            <div style={{ width: "300px", height: "300px" }}>
                <Pie
                    data={{
                        labels: reportData?.order_type_sales?.map((row) => row.order_type),
                        datasets: [
                            {
                                data: reportData?.order_type_sales?.map((row) => row.total_sales),
                                backgroundColor: ["#ff6384", "#36a2eb", "#ffce56"],
                            },
                        ],
                    }}
                    options={{ maintainAspectRatio: false }}
                />
            </div>

            {/* Payment Method Breakdown
            {reportData?.payment_method_sales && (
                <>
                    <h2>Payment Method Breakdown</h2>
                    <div style={{ width: "300px", height: "300px" }}>
                        <Pie
                            data={{
                                labels: reportData.payment_method_sales.map((row) => row.payment_method),
                                datasets: [
                                    {
                                        data: reportData.payment_method_sales.map((row) => row.total_sales),
                                        backgroundColor: ["#ff6384", "#36a2eb", "#ffce56", "#4bc0c0"],
                                    },
                                ],
                            }}
                            options={{ maintainAspectRatio: false }}
                        />
                    </div>
                </>
            )} */}
        </div>
    );
};

export default SalesReport;