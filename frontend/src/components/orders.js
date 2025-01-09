import React, { useState, useEffect } from "react";
import axios from "axios";
import "./orders.css";

const Orders = () => {
    const [orders, setOrders] = useState([]);

    useEffect(() => {
        const fetchOrders = async () => {
            try {
                const response = await axios.get("http://127.0.0.1:5000/orders");
                setOrders(response.data);
            } catch (error) {
                console.error("Error fetching orders:", error);
            }
        };

        fetchOrders();
    }, []);

    return (
        <div className="orders-container">
            <h1>Orders</h1>
            {orders.map((order) => (
                <div key={order.id} className="order-card">
                    <div className="order-header">Order ID: {order.id}</div>
                    <div className="order-type">Type: {order.type}</div>
                    <div className="order-total">Total Price: ${order.total_price.toFixed(2)}</div>
                    <div className="order-items">
                        <h4>Items:</h4>
                        <ul>
                            {order.items.map((item, index) => (
                                <li key={index}>
                                    {item.name} - ${item.price.toFixed(2)} x {item.quantity}
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default Orders;