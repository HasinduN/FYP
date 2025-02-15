import React, { useState, useEffect } from "react";
import axios from "axios";
import "./menuManagement.css";

const MenuManagement = () => {
    const [menuItems, setMenuItems] = useState([]);
    const [newItem, setNewItem] = useState({ name: "", price: "", description: "" });

    // Function to fetch menu items
    const fetchMenuItems = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:5000/menu");
            setMenuItems(response.data);
        } catch (error) {
            console.error("Error fetching menu items:", error);
        }
    };

    // Fetch menu items when the component loads
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
                price: parseFloat(newItem.price), // Ensure price is a number
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
            const response = await fetch(`http://127.0.0.1:5000/menu/${id}`, {
                method: "DELETE",
            });

            if (response.ok) {
                alert("Menu item deleted successfully!");
                fetchMenuItems(); // Refresh the menu list
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.error}`);
            }
        } catch (error) {
            console.error("Error deleting menu item:", error);
            alert("Failed to delete menu item.");
        }
    };

    return (
        <div className="menu-management-container">
            <h1>Menu Management</h1>
            
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

            {/* Table Displaying Menu Items */}
            <h3>Existing Menu Items</h3>
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
                                <td>${item.price.toFixed(2)}</td>
                                <td>{item.description || "No description"}</td>
                                <td>
                                    <button className="edit-btn">Edit</button>
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