import api from "./api.js";

/**
 * Function to call the distribution optimization API.
 * @param {number} userId - The user ID for the optimization.
 * @returns {Promise<Object>} - The response data from the API containing the optimization result.
 */
export const runDistributionOptimization = async (userId) => {
    try {
        const response = await api.post(`/api/run_distribution_optimization/`, {
            user_id: userId,
        });

        // Return the response data which contains the optimization results
        return response.data;
    } catch (error) {
        console.error("Error during distribution optimization:", error);
        throw error.response ? error.response.data : new Error("Αποτυχία στην βελτιστοποίηση διανομής.");
    }
};

/**
 * Function to fetch all distribution optimizations for a given user ID.
 * @param {number} userId - The user ID for which distribution optimizations should be retrieved.
 * @returns {Promise<Object[]>} - A promise that resolves to the list of distribution optimizations.
 */
export const fetchAllDistributionOptimizations = async (userId) => {
    try {
        const response = await api.get(`/api/get_all_distribution_optimizations/`, {
            params: { user_id: userId }
        });
        // Return the response data containing the list of distribution optimizations
        return response.data;
    } catch (error) {
        console.error("Error fetching all distribution optimizations:", error);
        throw error.response ? error.response.data : new Error("Αποτυχία φόρτωσης δεδομένων βελτιστοποίησης διανομής.");
    }
};
