import React, { useState, useEffect } from "react";
import axios from "axios";
import { saveAs } from "file-saver";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { Line } from "react-chartjs-2";
import {
    Chart as ChartJS,
    LineElement,
    CategoryScale,
    LinearScale,
    PointElement,
    Tooltip,
    Legend
} from "chart.js";
import "./salesReport.css";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

const SalesReport = () => {
    const [salesData, setSalesData] = useState({
        daily_item_sales: [],
        daily_sales: [],
        order_type_sales: [],
        sales_trends: [],
        top_items: [],
        order_details: []
    });
    const [loading, setLoading] = useState(false);
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);

    useEffect(() => {
        fetchSalesReport();
    }, []);

    const fetchSalesReport = async () => {
        try {
            setLoading(true);
            let url = "http://127.0.0.1:5000/sales-report";

            if (startDate && endDate) {
                const start = startDate.toISOString().split("T")[0];
                const end = endDate.toISOString().split("T")[0];
                url += `?start_date=${start}&end_date=${end}`;
            }

            const response = await axios.get(url);
            setSalesData(response.data || {});
        } catch (error) {
            console.error("Error fetching sales report:", error);
        } finally {
            setLoading(false);
        }
    };

    const downloadReport = () => {
        const csvContent = [
            ["Item Name", "Total Sold", "Total Revenue"],
            ...salesData.daily_item_sales.map((sale) => [
                sale.item_name, sale.total_sold, sale.total_revenue
            ])
        ]
            .map((row) => row.join(","))
            .join("\n");

        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        saveAs(blob, "SalesReport.csv");
    };

    const downloadOrderSummary = () => {
        const csvContent = [
          ["Order ID", "Date", "Total Sale"],
          ...salesData.order_details.map(order => [
            `"${order.order_id}"`,
            `"${order.date}"`,
            `"${order.total_sale?.toFixed(2)}"`
          ])
        ]
          .map(row => row.join(","))
          .join("\n");
      
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        saveAs(blob, "OrderSummary.csv");
      };      

    const dailySales = salesData?.daily_sales?.[0] || {};

    const chartData = {
        labels: salesData.sales_trends.map(trend => trend.date),
        datasets: [
            {
                label: "Sales (Last 7 Days)",
                data: salesData.sales_trends.map(trend => trend.sales_amount),
                fill: false,
                borderColor: "rgba(75,192,192,1)",
                tension: 0.1,
            }
        ]
    };

    return (
        <div className="sales-container">
            <h1>SALES REPORT</h1>

            <div className="datepicker-wrapper">
                <DatePicker
                    selectsRange={true}
                    startDate={startDate}
                    endDate={endDate}
                    onChange={(dates) => {
                        const [start, end] = dates;
                        setStartDate(start);
                        setEndDate(end);
                    }}
                    showClearButton={false}
                    placeholderText="Select date range"
                    maxDate={new Date()}
                    dateFormat="yyyy-MM-dd"
                />
                <button onClick={fetchSalesReport} className="filter-btn">Filter</button>
            </div>

            {loading ? (
                <p>Loading sales data...</p>
            ) : (
                <>
                    <h2>Overall Sales</h2>
                    {dailySales?.total_sales ? (
                        <div className="summary">
                            <p><strong>Total Sales:</strong> {dailySales.total_sales}</p>
                            <p><strong>Total Orders:</strong> {dailySales.total_orders}</p>
                            <p><strong>Avg Order Value:</strong> {dailySales.avg_order_value?.toFixed(2)}</p>
                        </div>
                    ) : (
                        <p>No sales recorded.</p>
                    )}

                    <div className="head">
                        <h2>Orders Summary</h2>
                        <button className="download-btn" onClick={downloadOrderSummary}>Download Report</button>
                    </div>
                    <div className="table-wrapper">
                        {Array.isArray(salesData.order_details) && salesData.order_details.length > 0 ? (
                            <table className="sales-table">
                                <thead>
                                    <tr>
                                        <th>Order ID</th>
                                        <th>Date</th>
                                        <th>Total Sale</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {salesData.order_details.map((order, index) => (
                                        <tr key={index}>
                                            <td>{order.order_id}</td>
                                            <td>{order.date}</td>
                                            <td>{order.total_sale?.toFixed(2)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : (
                            <p>No orders found for the selected range.</p>
                        )}
                    </div>
                    <div className="head">
                        <h2>Item-wise Sales</h2>
                        <button className="download-btn" onClick={downloadReport}>Download Report</button>
                    </div>
                    <div className="table-wrapper">
                        {Array.isArray(salesData.daily_item_sales) && salesData.daily_item_sales.length > 0 ? (
                            <table className="sales-table">
                                <thead>
                                    <tr>
                                        <th>Item Name</th>
                                        <th>Total Sold</th>
                                        <th>Total Revenue</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {salesData.daily_item_sales.map((sale, index) => (
                                        <tr key={index}>
                                            <td>{sale.item_name}</td>
                                            <td>{sale.total_sold}</td>
                                            <td>{sale.total_revenue.toFixed(2)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : (
                            <p>No item-wise sales data available.</p>
                        )}
                    </div>

                    <h2>Sales Trend</h2>
                    {salesData.sales_trends.length > 0 ? (
                        <div className="chart-container">
                            <Line data={chartData} />
                        </div>
                    ) : (
                        <p>No sales trend data available.</p>
                    )}
                </>
            )}
        </div>
    );
};

export default SalesReport;
