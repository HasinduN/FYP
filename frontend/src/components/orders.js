import React, { useState, useEffect } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import "./orders.css";

const Orders = () => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(false);
    const [dateRange, setDateRange] = useState([null, null]); // Stores start & end date
    const [startDate, endDate] = dateRange; // Destructure start and end date

    useEffect(() => {
        fetchOrders();
    }, []);

    const fetchOrders = async () => {
        try {
            setLoading(true);
            let url = "http://127.0.0.1:5000/orders";

            if (startDate && endDate) {
                url += `?start_date=${startDate.toISOString().split("T")[0]}&end_date=${endDate.toISOString().split("T")[0]}`;
            }

            const response = await axios.get(url);
            const sortedOrders = response.data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)); // Sort orders by timestamp (latest first)
            setOrders(sortedOrders);
        } catch (error) {
            toast.error("Error fetching orders!");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="orders-container">
            <ToastContainer />
            <h1>ORDERS</h1>

            {/* Date Range Filter with Single Calendar */}
            <div className="date-filter">
                <label>Select Date Range:</label>
                <DatePicker
                    selectsRange={true} // Enables range selection
                    startDate={startDate}
                    endDate={endDate}
                    onChange={(update) => setDateRange(update)}
                    showClearButton={false} // Removes blue cross mark
                    placeholderText="Select date range"
                />
                <button onClick={fetchOrders}>Filter</button>
            </div>

            {loading ? (
                <p>Loading orders...</p>
            ) : orders.length > 0 ? (
                <table className="orders-table">
                    <thead>
                        <tr>
                            <th>Order ID</th>
                            <th>Type</th>
                            <th>Total Price</th>
                            <th>Status</th>
                            <th>Items</th>
                            <th>Placed At</th>
                        </tr>
                    </thead>
                    <tbody>
                        {orders.map((order) => (
                            <tr
                                key={order.id}
                                className={order.status ? "completed-order" : "ongoing-order"}
                            >
                                <td>{order.id}</td>
                                <td>{order.type}</td>
                                <td>{order.total_price.toFixed(2)}</td>
                                <td>{order.status ? "Completed" : "Ongoing"}</td>
                                <td>
                                    <ul>
                                        {order.items.map((item, index) => (
                                            <li key={index}>
                                                {item.name} - {item.price.toFixed(2)} x {item.quantity}
                                            </li>
                                        ))}
                                    </ul>
                                </td>
                                <td>{new Date(order.timestamp).toLocaleString()}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>No orders found</p>
            )}
        </div>
    );
};

export default Orders;