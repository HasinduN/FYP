import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000';

export const getMenuItems = async () => {
    try {
        const response = await axios.get(`${API_URL}/menu`);
        return response.data;
    } catch (error) {
        console.error('Error fetching menu items:', error);
        throw error;
    }
};