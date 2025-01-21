import React, { useState, useEffect } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./addOrder.css";

const AddOrder = () => {
    const [menuItems, setMenuItems] = useState([]);
    const [selectedItems, setSelectedItems] = useState([]);
    const [orderType, setOrderType] = useState("Takeaway");
    const [tableNumber, setTableNumber] = useState("");
    const [totalPrice, setTotalPrice] = useState(0);
    const [ongoingOrders, setOngoingOrders] = useState([]);

    // Fetch menu items and ongoing orders when the component loads
    useEffect(() => {
        fetchMenuItems();
        fetchOngoingOrders();
    }, []);

    const fetchMenuItems = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:5000/menu");
            setMenuItems(response.data);
        } catch (error) {
            toast.error("Error fetching menu items!");
        }
    };

    const fetchOngoingOrders = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:5000/orders/ongoing");
            setOngoingOrders(response.data);
        } catch (error) {
            toast.error("Error fetching ongoing orders!");
        }
    };

    const addItem = (menuItem) => {
        const existingItem = selectedItems.find((item) => item.id === menuItem.id);
        if (existingItem) {
            setSelectedItems(
                selectedItems.map((item) =>
                    item.id === menuItem.id
                        ? { ...item, quantity: item.quantity + 1 }
                        : item
                )
            );
        } else {
            setSelectedItems([...selectedItems, { ...menuItem, quantity: 1 }]);
        }
        setTotalPrice(totalPrice + menuItem.price);
    };

    const removeItem = (menuItem) => {
        const existingItem = selectedItems.find((item) => item.id === menuItem.id);
        if (existingItem) {
            if (existingItem.quantity === 1) {
                setSelectedItems(selectedItems.filter((item) => item.id !== menuItem.id));
            } else {
                setSelectedItems(
                    selectedItems.map((item) =>
                        item.id === menuItem.id
                            ? { ...item, quantity: item.quantity - 1 }
                            : item
                    )
                );
            }
            setTotalPrice(totalPrice - menuItem.price);
        }
    };

    const placeOrder = async () => {
        if (selectedItems.length === 0) {
            toast.warn("Please add items to the order!");
            return;
        }

        const orderData = {
            type: orderType,
            table_number: orderType === "Dine-In" ? tableNumber : null,
            items: selectedItems.map((item) => ({
                menu_item_id: item.id,
                quantity: item.quantity,
            })),
        };

        try {
            await axios.post("http://127.0.0.1:5000/orders", orderData);
            toast.success("Order placed successfully!");
            fetchOngoingOrders(); // Refresh ongoing orders
            resetOrderForm();
        } catch (error) {
            toast.error("Error placing order!");
        }
    };

    const resetOrderForm = () => {
        setSelectedItems([]);
        setOrderType("Takeaway");
        setTableNumber("");
        setTotalPrice(0);
    };

    return (
        <div className="add-order-container">
            <ToastContainer />
            {/* Menu Section */}
            <div className="menu-section">
                <h2>Menu Items</h2>
                <div className="menu-list">
                    {menuItems.map((item) => (
                        <div key={item.id} className="menu-item-card">
                            <p>
                                {item.name} - ${item.price.toFixed(2)}
                            </p>
                            <div className="menu-item-buttons">
                                <button onClick={() => addItem(item)}>Add</button>
                                <button onClick={() => removeItem(item)}>Remove</button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Order Summary Section */}
            <div className="order-summary-section">
                <h2>Create Order</h2>
                <div>
                    <label>Order Type:</label>
                    <select
                        value={orderType}
                        onChange={(e) => setOrderType(e.target.value)}
                    >
                        <option value="Takeaway">Takeaway</option>
                        <option value="Dine-In">Dine-In</option>
                    </select>
                </div>
                {orderType === "Dine-In" && (
                    <div>
                        <label>Table Number:</label>
                        <input
                            type="number"
                            value={tableNumber}
                            onChange={(e) => setTableNumber(e.target.value)}
                        />
                    </div>
                )}
                <h3>Order Summary</h3>
                <ul>
                    {selectedItems.map((item) => (
                        <li key={item.id}>
                            {item.name} - ${item.price.toFixed(2)} x {item.quantity}
                        </li>
                    ))}
                </ul>
                <p>Total: ${totalPrice.toFixed(2)}</p>
                <button onClick={placeOrder}>Place Order</button>
            </div>

            {/* Ongoing Orders Section */}
            <div className="ongoing-orders-section">
                <h2>Ongoing Orders</h2>
                <div className="ongoing-orders-list">
                    {ongoingOrders.length === 0 ? (
                        <p>No ongoing orders.</p>
                    ) : (
                        ongoingOrders.map((order) => (
                            <div key={order.id} className="ongoing-order-card">
                                <p>Order ID: {order.id}</p>
                                <p>Type: {order.type}</p>
                                <p>Total: ${order.total_price.toFixed(2)}</p>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default AddOrder;
