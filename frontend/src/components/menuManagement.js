import React, { useState, useEffect } from "react";
import axios from "axios";
import "./menuManagement.css";

const categories = ["Fried Rice", "Noodles", "Kottu", "Cheese Kottu", "Nasigoreng", "Side Dishes", "Beverages", "Deserts"];

const MenuManagement = () => {
    const [menuItems, setMenuItems] = useState([]);
    const [ongoingOrderItems, setOngoingOrderItems] = useState([]); // Track items in ongoing orders
    const [newItem, setNewItem] = useState({ name: "", price: "", description: "", category: "" });
    const [editingItem, setEditingItem] = useState(null);

    // Fetch menu items and ongoing orders
    useEffect(() => {
        fetchMenuItems();
        fetchOngoingOrderItems();
    }, []);

    // Fetch menu items
    const fetchMenuItems = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:5000/menu");
            const menuArray = Object.values(response.data).flat();
            console.log("Fetched menu items:", menuArray);
            setMenuItems(menuArray);
        } catch (error) {
            console.error("Error fetching menu items:", error);
        }
    };

    // Fetch ongoing orders to prevent deletion of active items
    const fetchOngoingOrderItems = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:5000/orders/ongoing");
            const orderItems = response.data.flatMap(order => order.items.map(item => item.menu_item_id));
            setOngoingOrderItems(orderItems);
        } catch (error) {
            console.error("Error fetching ongoing orders:", error);
        }
    };

    // Check if a menu item is in an ongoing order
    const isItemInOngoingOrder = (id) => ongoingOrderItems.includes(id);

    // Add a new menu item
    const addMenuItem = async () => {
        if (!newItem.name || !newItem.price || !newItem.category) {
            alert("Name, Price, and Category are required.");
            return;
        }

        try {
            await axios.post("http://127.0.0.1:5000/menu", {
                name: newItem.name,
                price: parseFloat(newItem.price),
                description: newItem.description || "",
                category: newItem.category,
            });
            setNewItem({ name: "", price: "", description: "", category: "" });
            fetchMenuItems();
        } catch (error) {
            console.error("Error adding menu item:", error);
            alert("Failed to add menu item.");
        }
    };

    // Update an existing menu item
    const updateMenuItem = async () => {
        if (!editingItem.name || !editingItem.price || !editingItem.category) {
            alert("Name, Price, and Category are required.");
            return;
        }

        try {
            await axios.put(`http://127.0.0.1:5000/menu/${editingItem.id}`, {
                name: editingItem.name,
                price: parseFloat(editingItem.price),
                description: editingItem.description || "",
                category: editingItem.category,
            });

            alert("Menu item updated successfully!");
            setEditingItem(null); // Close edit form
            fetchMenuItems(); // Refresh menu list
        } catch (error) {
            console.error("Error updating menu item:", error);
            alert("Failed to update menu item.");
        }
    };

    // Delete a menu item
    const deleteMenuItem = async (id) => {
        if (isItemInOngoingOrder(id)) {
            alert("This item cannot be deleted because it is part of an ongoing order.");
            return;
        }

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
            alert(error.response?.data?.error || "Error: Unable to delete the menu item.");
        }
    };

    return (
        <div className="menu-management-container">
            <h1>MENU MANAGEMENT</h1>

            {/* Add New Menu Item Form */}
            <div className="menu-management-form">
                <input type="text" placeholder="Name" value={newItem.name} onChange={(e) => setNewItem({ ...newItem, name: e.target.value })} />
                <input type="number" placeholder="Price" value={newItem.price} onChange={(e) => setNewItem({ ...newItem, price: e.target.value })} />
                <input type="text" placeholder="Description" value={newItem.description} onChange={(e) => setNewItem({ ...newItem, description: e.target.value })} />
                <select value={newItem.category} onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}>
                    <option value="">Select Category</option>
                    {categories.map((cat) => (
                        <option key={cat} value={cat}>{cat}</option>
                    ))}
                </select>
                <button onClick={addMenuItem}>Add Item</button>
            </div>

            {/* Edit Menu Item Form */}
            {editingItem && (
                <div className="edit-form">
                    <h2>Edit Menu Item</h2>
                    <input type="text" placeholder="Name" value={editingItem.name} onChange={(e) => setEditingItem({ ...editingItem, name: e.target.value })} />
                    <input type="number" placeholder="Price" value={editingItem.price} onChange={(e) => setEditingItem({ ...editingItem, price: e.target.value })} />
                    <input type="text" placeholder="Description" value={editingItem.description} onChange={(e) => setEditingItem({ ...editingItem, description: e.target.value })} />
                    <select value={editingItem.category} onChange={(e) => setEditingItem({ ...editingItem, category: e.target.value })}>
                        <option value="">Select Category</option>
                        {categories.map((cat) => (
                            <option key={cat} value={cat}>{cat}</option>
                        ))}
                    </select>
                    <button onClick={updateMenuItem}>Update Item</button>
                    <button onClick={() => setEditingItem(null)} className="cancel-btn">Cancel</button>
                </div>
            )}

            {/* Menu Items Table */}
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
                                    <button className="edit-btn" onClick={() => setEditingItem(item)}>Edit</button>
                                    <button
                                        className="delete-btn"
                                        onClick={() => deleteMenuItem(item.id)}
                                        disabled={isItemInOngoingOrder(item.id)}
                                        style={{
                                            backgroundColor: isItemInOngoingOrder(item.id) ? "gray" : "red",
                                            cursor: isItemInOngoingOrder(item.id) ? "not-allowed" : "pointer"
                                        }}
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
