import React, { useState, useEffect } from "react";
import axios from "axios";
import "./menu.css";

const Menu = () => {
    const [menuItems, setMenuItems] = useState([]);

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

    return (
        <div className="menu-container">
            <h1>Menu</h1>
            {menuItems.map((item) => (
                <div key={item.id} className="menu-item">
                    <h3>{item.name}</h3>
                    <p>Price: ${item.price.toFixed(2)}</p>
                    {item.description && <p>{item.description}</p>}
                </div>
            ))}
        </div>
    );
};

export default Menu;