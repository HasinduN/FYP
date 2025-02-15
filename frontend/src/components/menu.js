import React, { useState, useEffect } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./menu.css";

const Menu = () => {
    const [menuItems, setMenuItems] = useState([]);
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

    return (
        <div className="menu-container">
            <ToastContainer />
            <h1>Menu</h1>
            {loading ? (
                <p>Loading...</p>
            ) : (
                <table className="menu-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Price</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        {menuItems.map((item) => (
                            <tr key={item.id}>
                                <td>{item.id}</td>
                                <td>{item.name}</td>
                                <td>${item.price.toFixed(2)}</td>
                                <td>{item.description || "No description"}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default Menu;