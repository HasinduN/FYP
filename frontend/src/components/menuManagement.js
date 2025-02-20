import React, { useState, useEffect } from "react";
import axios from "axios";
import "./menuManagement.css";

const MenuManagement = () => {
    const [menuItems, setMenuItems] = useState([]);
    const [newItem, setNewItem] = useState({ name: "", price: "", description: "" });
    const [editingItem, setEditingItem] = useState(null); // Track item being edited

    // Function to fetch menu items
    const fetchMenuItems = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:5000/menu");
            setMenuItems(response.data);
        } catch (error) {
            console.error("Error fetching menu items:", error);
        }
    };

    useEffect(() => {
        fetchMenuItems();
    }, []);

    // Function to add a new menu item
    const addMenuItem = async () => {
        if (!newItem.name || !newItem.price) {
            alert("Name and Price are required.");
            return;
        }

        try {
            await axios.post("http://127.0.0.1:5000/menu", {
                name: newItem.name,
                price: parseFloat(newItem.price),
                description: newItem.description || "",
            });
            setNewItem({ name: "", price: "", description: "" });
            fetchMenuItems();
        } catch (error) {
            console.error("Error adding menu item:", error);
            alert("Failed to add menu item.");
        }
    };

    // Function to delete a menu item
    const deleteMenuItem = async (id) => {
        if (!window.confirm("Are you sure you want to delete this item?")) {
            return;
        }

        try {
            const response = await axios.delete(`http://127.0.0.1:5000/menu/${id}`);

            if (response.status === 200) {
                alert("Menu item deleted successfully!");
                fetchMenuItems();
            } else {
                alert("Failed to delete menu item.");
            }
        } catch (error) {
            console.error("Error deleting menu item:", error);
            alert("Error: Menu item might be in an active order and cannot be deleted.");
        }
    };

    // Function to handle editing
    const editMenuItem = async () => {
        if (!editingItem.name || !editingItem.price) {
            alert("Name and Price are required.");
            return;
        }

        try {
            await axios.put(`http://127.0.0.1:5000/menu/${editingItem.id}`, {
                name: editingItem.name,
                price: parseFloat(editingItem.price),
                description: editingItem.description || "",
            });
            setEditingItem(null);
            fetchMenuItems();
        } catch (error) {
            console.error("Error updating menu item:", error);
            alert("Failed to update menu item.");
        }
    };

    return (
        <div className="menu-management-container">
            <h1>MENU</h1>

            {/* Add New Menu Item Form */}
            <div className="menu-management-form">
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

            {/* Edit Menu Item Form */}
            {editingItem && (
                <div className="edit-menu-form">
                    <h3>Edit Menu Item</h3>
                    <input
                        type="text"
                        value={editingItem.name}
                        onChange={(e) => setEditingItem({ ...editingItem, name: e.target.value })}
                    />
                    <input
                        type="number"
                        value={editingItem.price}
                        onChange={(e) => setEditingItem({ ...editingItem, price: e.target.value })}
                    />
                    <input
                        type="text"
                        value={editingItem.description}
                        onChange={(e) => setEditingItem({ ...editingItem, description: e.target.value })}
                    />
                    <button onClick={editMenuItem}>Update</button>
                    <button onClick={() => setEditingItem(null)}>Cancel</button>
                </div>
            )}

            {menuItems.length > 0 ? (
                <table className="menu-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Price</th>
                            <th>Description</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {menuItems.map((item) => (
                            <tr key={item.id}>
                                <td>{item.id}</td>
                                <td>{item.name}</td>
                                <td>{item.price.toFixed(2)}</td>
                                <td>{item.description || "No description"}</td>
                                <td>
                                    <button
                                        className="edit-btn"
                                        onClick={() => setEditingItem(item)}
                                    >
                                        Edit
                                    </button>
                                    <button
                                        className="delete-btn"
                                        onClick={() => deleteMenuItem(item.id)}
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>No menu items available.</p>
            )}
        </div>
    );
};

export default MenuManagement;