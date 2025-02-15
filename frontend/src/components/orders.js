import React, { useState, useEffect } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./orders.css";

const Orders = () => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchOrders();
    }, []);

    const fetchOrders = async () => {
        try {
            setLoading(true);
            const response = await axios.get("http://127.0.0.1:5000/orders");
            setOrders(response.data);
        } catch (error) {
            toast.error("Error fetching orders!");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="orders-container">
            <ToastContainer />
            <h1>Orders</h1>

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
                            <tr
                                key={order.id}
                                className={order.status ? "completed-order" : "ongoing-order"}
                            >
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