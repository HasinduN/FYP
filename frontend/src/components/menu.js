import React, { useState, useEffect } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./menu.css";

const Menu = () => {
    const [menuItems, setMenuItems] = useState([]);
    const [newItem, setNewItem] = useState({ name: "", price: "", description: "" });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchMenuItems();
    }, []);

    const fetchMenuItems = async () => {
        try {
            setLoading(true);
            const response = await axios.get("http://127.0.0.1:5000/menu");
            setMenuItems(response.data);
        } catch (error) {
            toast.error("Error fetching menu items!");
        } finally {
            setLoading(false);
        }
    };

    const addMenuItem = async () => {
        if (!newItem.name || !newItem.price) {
            toast.warn("Name and Price are required!");
            return;
        }
        try {
            setLoading(true);
            await axios.post("http://127.0.0.1:5000/menu", newItem);
            toast.success("Menu item added successfully!");
            setNewItem({ name: "", price: "", description: "" });
            fetchMenuItems();
        } catch (error) {
            toast.error("Error adding menu item!");
        } finally {
            setLoading(false);
        }
    };

    const deleteMenuItem = async (id) => {
        if (!window.confirm("Are you sure you want to delete this item?")) {
            return;
        }
        try {
            setLoading(true);
            await axios.delete(`http://127.0.0.1:5000/menu/${id}`);
            toast.success("Menu item deleted successfully!");
            fetchMenuItems();
        } catch (error) {
            toast.error("Error deleting menu item!");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="menu-container">
            <ToastContainer />
            <div className="menu-header">
                <h1>Menu Management</h1>
                <div className="add-item-form">
                    <input
                        type="text"
                        placeholder="Name"
                        value={newItem.name}
                        onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                    />
                    <input
                        type="number"
                        placeholder="Price"
                        value={newItem.price}
                        onChange={(e) => setNewItem({ ...newItem, price: e.target.value })}
                    />
                    <input
                        type="text"
                        placeholder="Description"
                        value={newItem.description}
                        onChange={(e) =>
                            setNewItem({ ...newItem, description: e.target.value })
                        }
                    />
                    <button onClick={addMenuItem}>Add Item</button>
                </div>
            </div>
            <div className="menu-list">
                {loading ? (
                    <p>Loading...</p>
                ) : (
                    menuItems.map((item) => (
                        <div key={item.id} className="menu-item-card">
                            <p>
                                <strong>{item.name}</strong> - ${item.price.toFixed(2)}
                            </p>
                            <p>{item.description}</p>
                            <button
                                className="delete-btn"
                                onClick={() => deleteMenuItem(item.id)}
                            >
                                Delete
                            </button>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default Menu;
