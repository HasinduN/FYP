import { createContext, useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const navigate = useNavigate();

    const fetchUser = async () => {
        const token = localStorage.getItem("token");
        if (!token) {
            navigate("/"); // Redirect to landing page if no token found
            return null;
        }

        try {
            const res = await axios.get("http://127.0.0.1:5000/auth/me", {
                headers: { Authorization: `Bearer ${token}` },
            });

            setUser(res.data);
            return res.data;
        } catch (error) {
            console.error("❌ Failed to fetch user:", error);
            logout(); // Log out if fetching user fails
            return null;
        }
    };

    const login = async (username, password) => {
        try {
            const res = await axios.post("http://127.0.0.1:5000/auth/login", { username, password });

            localStorage.setItem("token", res.data.token);
            localStorage.setItem("role", res.data.role);
            axios.defaults.headers.common["Authorization"] = `Bearer ${res.data.token}`;

            const userData = await fetchUser();
            if (userData) {
                navigate("/add-order"); // Redirect after successful login
            }
        } catch (error) {
            console.error("Login failed:", error);
        }
    };

    const logout = async () => {
        try {
            const token = localStorage.getItem("token");
            if (token) {
                await axios.post("http://127.0.0.1:5000/auth/logout", {}, {
                    headers: { Authorization: `Bearer ${token}` },
                });
            }
        } catch (error) {
            console.error("Logout failed:", error);
        }

        localStorage.removeItem("token");
        localStorage.removeItem("role");
        setUser(null);
        navigate("/");
    };

    useEffect(() => {
        fetchUser();
    }, []);

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
