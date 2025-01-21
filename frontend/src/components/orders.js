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
            <div className="orders-list">
                {loading ? (
                    <p>Loading orders...</p>
                ) : orders.length > 0 ? (
                    orders.map((order) => (
                        <div
                            key={order.id}
                            className={`order-card ${
                                order.status ? "completed-order" : "ongoing-order"
                            }`}
                        >
                            <h3>Order ID: {order.id}</h3>
                            <p>Type: {order.type}</p>
                            <p>Total Price: ${order.total_price.toFixed(2)}</p>
                            <p>Status: {order.status ? "Completed" : "Ongoing"}</p>
                            <h4>Items:</h4>
                            <ul>
                                {order.items.map((item, index) => (
                                    <li key={index}>
                                        {item.name} - ${item.price.toFixed(2)} x{" "}
                                        {item.quantity}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))
                ) : (
                    <p>No orders found</p>
                )}
            </div>
        </div>
    );
};

export default Orders;
