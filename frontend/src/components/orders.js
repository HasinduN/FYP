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
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);

    useEffect(() => {
        fetchOrders();
    }, []);

    const fetchOrders = async (filter = false) => {
        try {
            setLoading(true);
            let url = "http://127.0.0.1:5000/orders";

            if (filter && startDate && endDate) {
                url += `?start_date=${startDate.toISOString().split("T")[0]}&end_date=${endDate.toISOString().split("T")[0]}`;
            }

            const response = await axios.get(url);
            setOrders(response.data);
        } catch (error) {
            toast.error("Error fetching orders!");
        } finally {
            setLoading(false);
        }
    };

    const clearFilter = () => {
        setStartDate(null);
        setEndDate(null);
        fetchOrders(); // Reload all orders
    };

    return (
        <div className="orders-container">
            <ToastContainer />
            <h1>Orders</h1>

            {/* Date Range Filter */}
            <div className="date-filter">
                <label>Start Date:</label>
                <DatePicker selected={startDate} onChange={(date) => setStartDate(date)} />
                <label>End Date:</label>
                <DatePicker selected={endDate} onChange={(date) => setEndDate(date)} />
                <button onClick={() => fetchOrders(true)}>Filter</button>
                <button onClick={clearFilter} disabled={!startDate && !endDate}>Clear Filter</button>
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
                        </tr>
                    </thead>
                    <tbody>
                        {orders.map((order) => (
                            <tr key={order.id} className={order.status ? "completed-order" : "ongoing-order"}>
                                <td>{order.id}</td>
                                <td>{order.type}</td>
                                <td>${order.total_price.toFixed(2)}</td>
                                <td>{order.status ? "Completed" : "Ongoing"}</td>
                                <td>
                                    <ul>
                                        {order.items.map((item, index) => (
                                            <li key={index}>
                                                {item.name} - ${item.price.toFixed(2)} x {item.quantity}
                                            </li>
                                        ))}
                                    </ul>
                                </td>
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
