import api from "./api.js";
import {
    FAILED_CHANGE_USER_PASSWORD_EL,
    FAILED_CREATE,
    FAILED_FETCH_USER_ERP_API_EL,
    FAILED_FETCH_USERS_EL,
    FAILED_UPDATE
} from "../utils/constants";

/**
 * Fetches all users with role 'USER'. Accessible only to admins.
 * @returns {Promise<Array>} - A list of user objects.
 */
export const fetchAllUsers = async () => {
    try {
        const response = await api.get("/api/user/get_all_users/");
        // Sort so that the newest user (based on created_at) appears first
        const sorted = response.data.sort((a, b) =>
            new Date(b.created_at) - new Date(a.created_at)
        );
        return sorted;
    } catch (error) {
        console.error("Error fetching users:", error);
        throw error.response ? error.response.data : new Error(FAILED_FETCH_USERS_EL);
    }
};

/**
 * Creates (registers) a new user with the given data.
 *
 * @param {Object} userData - { email, password, role, privilege_names: [] }
 * @returns {Promise<Object>} - The response data from the API (e.g., { message: ... })
 */
export const createUser = async (userData) => {
    try {
        const response = await api.post("/api/user/register/", userData);
        return response.data; // { message: '...' }
    } catch (error) {
        console.error("Error creating user:", error);
        throw error.response ? error.response.data : new Error(FAILED_CREATE);
    }
};

/**
 * Updates a user's details.
 *
 * @param {Object} userData - { email, password?, role, privilege_names: [] }
 * @returns {Promise<Object>} - { message, updated_user }
 */
export const updateUser = async (userData) => {
    try {
        const response = await api.post("/api/user/update_user/", userData);
        return response.data; // { message, updated_user }
    } catch (error) {
        console.error("Error updating user:", error);
        throw error.response ? error.response.data : new Error("Αποτυχία ενημέρωσης χρήστη.");
    }
};

/**
 * Creates or updates a user's ERP API configuration.
 * Endpoint: POST /api/user/create_or_update_user_erp_api
 *
 * @param {Object} erpData
 * @returns {Promise<Object>} - The response data (e.g. { message: '...' })
 */
export const createOrUpdateUserErpApi = async (erpData) => {
    try {
        const response = await api.post("/api/user/create_or_update_user_erp_api/", erpData);
        return response.data; // { message: '...' }
    } catch (error) {
        console.error("Error updating user ERP API:", error);
        throw error.response ? error.response.data : new Error(FAILED_UPDATE);
    }
};

/**
 * Fetches the ERP API configuration for a given user.
 * @param {number} userId - The ID of the user whose ERP API details are needed.
 * @returns {Promise<Object>} - The ERP API config data (e.g. { client_name, login_token_url, ... }).
 */
export const fetchUserErpApi = async (userId) => {
    try {
        const response = await api.get("/api/user/get_user_erp_api/", {
            params: {user_id: userId},
        });
        return response.data;
    } catch (error) {
        console.error(FAILED_FETCH_USER_ERP_API_EL, error);
        throw error.response
            ? error.response.data
            : new Error(FAILED_FETCH_USER_ERP_API_EL);
    }
};

/**
 * Sends a request to change the password of the currently authenticated user.
 *
 * @param {Object} data                - The request payload containing user credentials.
 * @param {string} data.email          - The user's email address.
 * @param {string} data.oldPassword    - The current password of the user.
 * @param {string} data.newPassword    - The new password to be set.
 * @returns {Promise<Object>}          - A response object containing a success message from the backend.
 * @throws {Error|Object}              - Throws a backend error response or a generic error if the request fails.
 */
export const changePassword = async (data) => {
    try {
        const response = await api.post("/api/user/change_password/", data);
        return response.data;
    } catch (error) {
        console.error("Error changing password:", error);
        throw error.response ? error.response.data : new Error(FAILED_CHANGE_USER_PASSWORD_EL);
    }
};

/**
 * Sends a request to change a user's password by an admin.
 * @param {Object} data - An object containing:
 *    - email: the target user's email,
 *    - new_password: the new password,
 *    - role: the admin role (should be "ΔΙΑΧΕΙΡΙΣΤΗΣ"),
 *    - code: the confirmation code.
 * @returns {Promise<Object>} The API response.
 * @throws Will throw an error if the request fails.
 */
export const changePasswordByAdmin = async (data) => {
    try {
        const response = await api.post("/api/user/change_password_by_admin/", data);
        return response.data;
    } catch (error) {
        console.error("Error changing user password by admin:", error);
        throw error.response ? error.response.data : new Error(FAILED_CHANGE_USER_PASSWORD_EL);
    }
};