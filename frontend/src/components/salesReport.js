import React, { useEffect, useState } from "react";
import axios from "axios";
import { Bar, Pie, Line } from "react-chartjs-2";
import Chart from "chart.js/auto";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import "./salesReport.css";

const API_BASE_URL = "http://127.0.0.1:5000";
const SALES_REPORT_ENDPOINT = `${API_BASE_URL}/sales-report`;
const PREDICT_SALES_ENDPOINT = `${API_BASE_URL}/predict-sales`;

const SalesReport = () => {
    const [reportData, setReportData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [predictedSalesLoading, setPredictedSalesLoading] = useState(false);
    const [selectedDate, setSelectedDate] = useState(new Date());
    const [predictedSales, setPredictedSales] = useState([]);

    useEffect(() => {
        fetchSalesReport();
        fetchPredictedSales();
    }, []);

    const fetchSalesReport = async () => {
        try {
            setLoading(true);
            setError(null);
            const formattedDate = formatDate(selectedDate);
            const response = await axios.get(`${SALES_REPORT_ENDPOINT}?date=${formattedDate}`);
            setReportData(response.data);
        } catch (error) {
            console.error("Error fetching sales report:", error);
            setError("Failed to load sales report.");
        } finally {
            setLoading(false);
        }
    };

    const fetchPredictedSales = async () => {
        try {
            setPredictedSalesLoading(true);
            const response = await axios.get(PREDICT_SALES_ENDPOINT);
            setPredictedSales(formatPredictedSales(response.data)); // Convert format before setting state
        } catch (error) {
            console.error("Error fetching predicted sales:", error);
            setPredictedSales([]);
        } finally {
            setPredictedSalesLoading(false);
        }
    };

    const formatPredictedSales = (data) => {
        const salesMap = {};
        const uniqueDates = [...new Set(data.map((item) => item.date))].sort();

        data.forEach(({ date, item_name, predicted_sales }) => {
            if (!salesMap[item_name]) {
                salesMap[item_name] = {};
            }
            salesMap[item_name][date] = predicted_sales;
        });

        return { salesMap, uniqueDates };
    };

    const downloadCSV = () => {
        if (!reportData?.daily_item_sales?.length) {
            alert("No sales data available for this date.");
            return;
        }

        let csvContent = "data:text/csv;charset=utf-8,Item Name,Quantity Sold,Total Revenue\n";
        reportData.daily_item_sales.forEach((row) => {
            csvContent += `${escapeCSVValue(row.item_name)},${row.total_sold},${row.total_revenue}\n`;
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `Sales_Report_${formatDate(selectedDate)}.csv`);
        document.body.appendChild(link);
        link.click();
    };

    const formatDate = (date) => date.toISOString().split("T")[0];
    const escapeCSVValue = (value) => `"${value.replace(/"/g, '""')}"`;

    if (loading) return <p>Loading Sales Report...</p>;
    if (error) return <p style={{ color: "red" }}>{error}</p>;

    return (
        <div className="sales-report-container">
            <h1>Sales Report</h1>

            {/* Date Selector */}
            <div className="date-picker-container">
                <label>Select Date: </label>
                <DatePicker selected={selectedDate} onChange={(date) => setSelectedDate(date)} />
                <button onClick={downloadCSV}>Download CSV</button>
            </div>

            {/* Predicted Sales */}
            <h2>Predicted Sales for the Next 3 Days</h2>
            {predictedSalesLoading ? (
                <p>Loading predicted sales...</p>
            ) : predictedSales?.uniqueDates?.length > 0 ? (
                <table className="predicted-sales-table">
                    <thead>
                        <tr>
                            <th>Item Name</th>
                            {predictedSales.uniqueDates.map((date, index) => (
                                <th key={index}>{date}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {Object.entries(predictedSales.salesMap).map(([item, sales], rowIndex) => (
                            <tr key={rowIndex}>
                                <td>{item}</td>
                                {predictedSales.uniqueDates.map((date, colIndex) => (
                                    <td key={colIndex}>{sales[date] ?? "-"}</td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>No predicted sales data available.</p>
            )}

            {/* Daily Sales Report */}
            <h2>Items Sold on {selectedDate.toDateString()}</h2>
            {reportData?.daily_item_sales?.length > 0 ? (
                <table className="sales-table">
                    <thead>
                        <tr>
                            <th>Item Name</th>
                            <th>Quantity Sold</th>
                            <th>Total Revenue</th>
                        </tr>
                    </thead>
                    <tbody>
                        {reportData.daily_item_sales.map((row, index) => (
                            <tr key={index}>
                                <td>{row.item_name}</td>
                                <td>{row.total_sold}</td>
                                <td>{row.total_revenue}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>No sales data available for this date.</p>
            )}

            {/* Sales Trend Line Chart */}
            <h2>Sales Trends (Last 7 Days)</h2>
            <div className="chart-container">
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
                    options={{ maintainAspectRatio: false, responsive: true }}
                />
            </div>

            {/* Sales by Order Type */}
            <h2>Sales by Order Type</h2>
            <div className="chart-container">
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
                    options={{ maintainAspectRatio: false, responsive: true }}
                />
            </div>
        </div>
    );
};

export default SalesReport;
