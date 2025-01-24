import React, { useState, useEffect } from "react";
import axios from "axios";
import "./userManagement.css";

const UserManagement = () => {
    const [users, setUsers] = useState([]);
    const [newUser, setNewUser] = useState({ username: "", password: "", role: "cashier" });

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:5000/users");
            setUsers(response.data);
        } catch (error) {
            alert("Error fetching users");
        }
    };

    const addUser = async () => {
        try {
            await axios.post("http://127.0.0.1:5000/users", newUser);
            alert("User added successfully!");
            fetchUsers();
            setNewUser({ username: "", password: "", role: "cashier" });
        } catch (error) {
            alert(error.response?.data?.error || "Error adding user");
        }
    };

    const deleteUser = async (id) => {
        try {
            await axios.delete(`http://127.0.0.1:5000/users/${id}`);
            alert("User deleted successfully!");
            fetchUsers();
        } catch (error) {
            alert("Error deleting user");
        }
    };

    return (
        <div className="user-management-container">
            <h1>User Management</h1>
            <div className="user-form">
                <h3>Add New User</h3>
                <input
                    type="text"
                    placeholder="Username"
                    value={newUser.username}
                    onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={newUser.password}
                    onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                />
                <select
                    value={newUser.role}
                    onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                >
                    <option value="cashier">Cashier</option>
                    <option value="manager">Manager</option>
                </select>
                <button onClick={addUser}>Add User</button>
            </div>
            <div className="user-list">
                <h3>Existing Users</h3>
                {users.map((user) => (
                    <div key={user.id} className="user-card">
                        <p>
                            <strong>Username:</strong> {user.username}
                        </p>
                        <p>
                            <strong>Role:</strong> {user.role}
                        </p>
                        <button onClick={() => deleteUser(user.id)}>Delete</button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default UserManagement;