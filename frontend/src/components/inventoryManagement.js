import React, { useState, useEffect } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./inventoryManagement.css";

const InventoryManagement = () => {
    const [inventoryItems, setInventoryItems] = useState([]);
    const [newItem, setNewItem] = useState({ name: "", quantity: "" });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchInventoryItems();
    }, []);

    const fetchInventoryItems = async () => {
        try {
            setLoading(true);
            const response = await axios.get("http://127.0.0.1:5000/inventory");
            setInventoryItems(response.data);
        } catch (error) {
            toast.error("Error fetching inventory items!");
        } finally {
            setLoading(false);
        }
    };

    const addInventoryItem = async () => {
        if (!newItem.name || !newItem.quantity) {
            toast.warn("Name and Quantity are required!");
            return;
        }
        try {
            setLoading(true);
            await axios.post("http://127.0.0.1:5000/inventory", newItem);
            toast.success("Inventory item added successfully!");
            setNewItem({ name: "", quantity: "" });
            fetchInventoryItems();
        } catch (error) {
            toast.error("Error adding inventory item!");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="inventory-container">
            <ToastContainer />
            <div className="inventory-header">
                <h1>Inventory Management</h1>
                <div className="add-item-form">
                    <input
                        type="text"
                        placeholder="Name"
                        value={newItem.name}
                        onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                    />
                    <input
                        type="number"
                        placeholder="Quantity"
                        value={newItem.quantity}
                        onChange={(e) =>
                            setNewItem({ ...newItem, quantity: parseInt(e.target.value) })
                        }
                    />
                    <button onClick={addInventoryItem}>Add Item</button>
                </div>
            </div>
            <div className="inventory-list">
                {loading ? (
                    <p>Loading...</p>
                ) : (
                    inventoryItems.map((item) => (
                        <div key={item.id} className="inventory-item-card">
                            <p>
                                <strong>{item.name}</strong> - {item.quantity} units
                            </p>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default InventoryManagement;
