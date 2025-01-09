import React, { useState, useEffect } from "react";
import axios from "axios";
import "./menuManagement.css";

const MenuManagement = () => {
    const [menuItems, setMenuItems] = useState([]);
    const [newItem, setNewItem] = useState({ name: "", price: "", description: "" });

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

    const addMenuItem = async () => {
        try {
            await axios.post("http://127.0.0.1:5000/menu", newItem);
            setNewItem({ name: "", price: "", description: "" });
            const response = await axios.get("http://127.0.0.1:5000/menu");
            setMenuItems(response.data);
        } catch (error) {
            console.error("Error adding menu item:", error);
        }
    };

    const deleteMenuItem = async (id) => {
        try {
            await axios.delete(`http://127.0.0.1:5000/menu/${id}`);
            const response = await axios.get("http://127.0.0.1:5000/menu");
            setMenuItems(response.data);
        } catch (error) {
            console.error("Error deleting menu item:", error);
        }
    };

    return (
        <div className="menu-management-container">
            <h1>Menu Management</h1>
            <div className="menu-management-form">
                <h3>Add New Menu Item</h3>
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
                    onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                />
                <button onClick={addMenuItem}>Add Item</button>
            </div>
            <div className="menu-list">
                <h3>Existing Menu Items</h3>
                {menuItems.map((item) => (
                    <div key={item.id} className="menu-item">
                        <div>
                            <strong>{item.name}</strong> - ${item.price.toFixed(2)}
                            {item.description && <p>{item.description}</p>}
                        </div>
                        <div>
                            <button className="edit-btn">Edit</button>
                            <button
                                className="delete-btn"
                                onClick={() => deleteMenuItem(item.id)}
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default MenuManagement;