import {FAILED_LOGIN_EL} from "../utils/constants.js";
import axios from "axios";

/**
 * Creates an Axios instance with a base URL (need a separate one from api.js due Login).
 * The base URL is retrieved from environment variables.
 */
const authAPI = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
});

/**
 * Authenticates the user by sending a POST request with email and password.
 *
 * @param {string} email - The user's email address.
 * @param {string} password - The user's password.
 * @returns {Promise<Object>} - The response data from the login request.
 * @throws {Object|Error} - Throws an error if the login request fails.
 */
export const login = async (email, password) => {
    try {
        // Send a POST request to authenticate the user
        const response = await authAPI.post('api/user/login/', {email, password});
        // Store tokens and user data in localStorage
        localStorage.setItem("accessToken", response.data.access);
        localStorage.setItem("refreshToken", response.data.refresh);
        localStorage.setItem("userId", response.data.user.id);
        localStorage.setItem("userEmail", response.data.user.email);
        localStorage.setItem("userRole", response.data.user.role);
        localStorage.setItem("loginAt", response.data.user.login_at);
        localStorage.setItem("privileges", response.data.user.privilege_names);
        localStorage.setItem("userIsActive", response.data.user.is_active);
        // Return the data from the response
        return response.data;
    } catch (error) {
        // If an error response is received, throw the error data; otherwise, throw a generic error
        throw error.response ? error.response.data : new Error(FAILED_LOGIN_EL);
    }
};

/**
 * Logs out the user by clearing tokens and user info.
 */
export const logout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("userRole");
    localStorage.removeItem("privileges");
};
