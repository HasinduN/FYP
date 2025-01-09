import React, { createContext, useState } from 'react';

const AppContext = createContext();

const AppProvider = ({ children }) => {
    const [menuItems, setMenuItems] = useState([]);
    const [sales, setSales] = useState([]);

    return (
        <AppContext.Provider value={{ menuItems, setMenuItems, sales, setSales }}>
            {children}
        </AppContext.Provider>
    );
};

export { AppContext, AppProvider };