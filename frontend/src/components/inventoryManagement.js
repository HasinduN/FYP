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
            const response = await axios.get("http://127.0.0.1:5000/inventory-management");
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
            await axios.post("http://127.0.0.1:5000/inventory-management", newItem);
            toast.success("Inventory item added successfully!");
            setNewItem({ name: "", quantity: "" });
            fetchInventoryItems(); // Refresh inventory list
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
                    <button onClick={addInventoryItem} disabled={loading}>
                        {loading ? "Adding..." : "Add Item"}
                    </button>
                </div>
            </div>

            <div className="inventory-list">
                {loading ? (
                    <p>Loading...</p>
                ) : (
                    <table className="inventory-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Item Name</th>
                                <th>Quantity</th>
                                <th>Added Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {inventoryItems.map((item) => (
                                <tr key={item.id}>
                                    <td>{item.id}</td>
                                    <td>{item.name}</td>
                                    <td>{item.quantity}</td>
                                    <td>{new Date(item.added_date).toLocaleString()}</td> 
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

export default InventoryManagement;
