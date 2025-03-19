import { useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/authContext";

const Logout = () => {
    const { logout } = useContext(AuthContext);
    const navigate = useNavigate();

    useEffect(() => {
        const handleLogout = async () => {
            await logout();
            navigate("/login"); // Handle navigation separately
        };

        handleLogout();
    }, [logout, navigate]);

    return <h2>Logging out...</h2>;
};

export default Logout;
