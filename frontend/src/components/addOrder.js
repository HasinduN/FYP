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
    const [currentOrderId, setCurrentOrderId] = useState(null);
    const [kotPrinted, setKotPrinted] = useState(false); // Track if KOT is printed
    const [paymentMethod, setPaymentMethod] = useState(""); // Track payment method
    const [allowReprint, setAllowReprint] = useState(false); // Allow reprinting KOT after changes

    useEffect(() => {
        fetchMenuItems();
        fetchOngoingOrders();
    }, []);

    const fetchMenuItems = async () => {
        try {
            const token = localStorage.getItem("access_token"); // Retrieve stored JWT token
            const response = await axios.get("http://127.0.0.1:5000/menu", {
                headers: { Authorization: `Bearer ${token}` } // Add token to headers
            });
            setMenuItems(response.data);
        } catch (error) {
            toast.error("Error fetching menu items!");
        }
    };

    const fetchOngoingOrders = async () => {
        try {
            const token = localStorage.getItem("access_token");
            const response = await axios.get("http://127.0.0.1:5000/orders/ongoing", {
                headers: {Authorization: `Bearer ${token}`}
            });
            const sortedOrders = response.data.sort(
                (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
            );
            setOngoingOrders(sortedOrders);
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
        setAllowReprint(true); // Allow reprinting KOT after adding a new item
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
            const token = localStorage.getItem("access_token");
            const response = await axios.post("http://127.0.0.1:5000/orders", orderData, {
                headers: { Authorization: `Bearer ${token}` }
            });
            const { order_id } = response.data;
            setCurrentOrderId(order_id);
            toast.success("Order placed successfully!");
            fetchOngoingOrders();
        } catch (error) {
            toast.error("Error placing order!");
        }
    };

    const printKOT = async () => {
        if (!currentOrderId) {
            toast.warn("Please place the order first!");
            return;
        }

        try {
            const token = localStorage.getItem("access_token");
            await axios.post(`http://127.0.0.1:5000/orders/${currentOrderId}/kot`,
                {},
                { headers: { Authorization: `Bearer ${token}` } }
            );
            toast.success("KOT printed successfully!");
            setKotPrinted(true);
            setAllowReprint(false); // Disable reprinting unless a new item is added
        } catch (error) {
            toast.error("Error printing KOT!");
        }
    };

    const processPayment = async () => {
        if (!paymentMethod) {
            toast.warn("Please select a payment method!");
            return;
        }

        try {
            const token = localStorage.getItem("access_token");
            await axios.post(
                `http://127.0.0.1:5000/orders/${currentOrderId}/payment`,
                { payment_method: paymentMethod },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            toast.success("Payment completed! Order is now closed.");
            fetchOngoingOrders();
            resetOrderForm();
        } catch (error) {
            toast.error("Error processing payment!");
        }
    };

    const editOngoingOrder = (order) => {
        setCurrentOrderId(order.id);
        setSelectedItems(
            order.items.map((item) => ({
                id: item.menu_item_id,
                name: item.name,
                price: item.price,
                quantity: item.quantity,
            }))
        );
        setOrderType(order.type);
        setTableNumber(order.table_number || "");
        setTotalPrice(order.total_price);
        setKotPrinted(false); // Allow reprinting after edits
    };

    const completePayment = (order) => {
        editOngoingOrder(order);
        setKotPrinted(true); // Payment section is shown immediately
    };

    const resetOrderForm = () => {
        setSelectedItems([]);
        setOrderType("Takeaway");
        setTableNumber("");
        setTotalPrice(0);
        setCurrentOrderId(null);
        setKotPrinted(false);
        setPaymentMethod("");
        setAllowReprint(false);
    };

    return (
        <div className="add-order-container">
            <ToastContainer />
            {/* Menu Section */}
            <div className="menu-section">
                <h2>MENU ITEMS</h2>
                <div className="menu-list">
                    {menuItems.map((item) => (
                        <div key={item.id} className="menu-item-card">
                            <p>
                                {item.name} - {item.price.toFixed(2)}
                            </p>
                            <div className="menu-item-buttons">
                                <button onClick={() => addItem(item)}>ADD</button>
                                <button onClick={() => removeItem(item)}>REMOVE</button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Order Summary Section */}
            <div className="order-summary-section">
                <h2>{currentOrderId ? "EDIT ORDER" : "CREATE ORDER"}</h2>
                <div>
                    <label>ORDER TYPE:</label>
                    <select
                        value={orderType}
                        onChange={(e) => setOrderType(e.target.value)}
                        disabled={!!currentOrderId}
                    >
                        <option value="Takeaway">TAKEAWAY</option>
                        <option value="Dine-In">DINE IN</option>
                    </select>
                </div>
                {orderType === "Dine-In" && (
                    <div>
                        <label>TABLE NUMBER:</label>
                        <input
                            type="number"
                            value={tableNumber}
                            onChange={(e) => setTableNumber(e.target.value)}
                            disabled={!!currentOrderId}
                        />
                    </div>
                )}
                <h3>ORDER SUMMARY</h3>
                <ul>
                    {selectedItems.map((item) => (
                        <li key={item.id}>
                            {item.name} - {item.price.toFixed(2)} x {item.quantity}
                        </li>
                    ))}
                </ul>
                <p>TOTAL: {totalPrice.toFixed(2)}</p>
                {!currentOrderId && <button onClick={placeOrder}>PLACE ORDER</button>}
                <button
                    onClick={printKOT}
                    disabled={!allowReprint && (kotPrinted || !currentOrderId)}
                >
                    PRINT KOT
                </button>

                {/* Payment Section */}
                {kotPrinted && (
                    <div className="payment-section">
                        <h3>PAYMENT</h3>
                        <label>
                            PAYMENT METHOD:
                            <select
                                value={paymentMethod}
                                onChange={(e) => setPaymentMethod(e.target.value)}
                            >
                                <option value="">SELECT</option>
                                <option value="cash">CASH</option>
                                <option value="card">CARD</option>
                            </select>
                        </label>
                        <button onClick={processPayment}>COMPLETE PAYMENT</button>
                    </div>
                )}
            </div>

            {/* Ongoing Orders Section */}
            <div className="ongoing-orders-section">
                <h2>ONGOING ORDERS</h2>
                <div className="ongoing-orders-list">
                    {ongoingOrders.length === 0 ? (
                        <p>NO ONGOING ORDERS</p>
                    ) : (
                        ongoingOrders.map((order) => (
                            <div key={order.id} className="ongoing-order-card">
                                <p>ORDER ID: {order.id}</p>
                                <p>TYPE: {order.type}</p>
                                <p>TOTAL: {order.total_price.toFixed(2)}</p>
                                <div className="ongoing-order-actions">
                                    <button onClick={() => editOngoingOrder(order)}>
                                        EDIT
                                    </button>
                                    <button onClick={() => completePayment(order)}>
                                        COMPLETE PAYMENT
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default AddOrder;