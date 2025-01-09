import React, { useState, useEffect } from "react";
import axios from "axios";
import "./addOrder.css";

const AddOrder = () => {
    const [orderType, setOrderType] = useState("Takeaway");
    const [menuItems, setMenuItems] = useState([]);
    const [selectedItems, setSelectedItems] = useState([]);
    const [tableNumber, setTableNumber] = useState("");
    const [totalPrice, setTotalPrice] = useState(0);

    useEffect(() => {
        const fetchMenuItems = async () => {
            try {
                const response = await axios.get("http://127.0.0.1:5000/menu");
                setMenuItems(response.data);
            } catch (error) {
                console.error("Error fetching menu items:", error);
            }
        };
        fetchMenuItems();
    }, []);

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

    const handleSubmit = async (e) => {
        e.preventDefault();
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
            alert("Order placed successfully!");
            setSelectedItems([]);
            setTotalPrice(0);
        } catch (error) {
            console.error("Error placing order:", error);
        }
    };

    return (
        <div className="add-order-container">
            <div className="menu-sidebar">
                <h2>Menu Items</h2>
                {menuItems.map((item) => (
                    <div key={item.id} className="menu-item">
                        <span>{item.name} - ${item.price.toFixed(2)}</span>
                        <button onClick={() => addItem(item)}>Add</button>
                    </div>
                ))}
            </div>
            <div className="order-form">
                <h2>Create Order</h2>
                <form onSubmit={handleSubmit}>
                    <label>
                        Order Type:
                        <select value={orderType} onChange={(e) => setOrderType(e.target.value)}>
                            <option value="Takeaway">Takeaway</option>
                            <option value="Dine-In">Dine-In</option>
                        </select>
                    </label>
                    <br />
                    {orderType === "Dine-In" && (
                        <label>
                            Table Number:
                            <input
                                type="number"
                                value={tableNumber}
                                onChange={(e) => setTableNumber(e.target.value)}
                                required
                            />
                        </label>
                    )}
                    <div className="order-summary">
                        <h3>Order Summary</h3>
                        <ul>
                            {selectedItems.map((item, index) => (
                                <li key={index}>
                                    {item.name} - ${item.price.toFixed(2)} x {item.quantity}
                                </li>
                            ))}
                        </ul>
                        <div className="total-price">Total: ${totalPrice.toFixed(2)}</div>
                    </div>
                    <button type="submit">Place Order</button>
                </form>
            </div>
        </div>
    );
};

export default AddOrder;