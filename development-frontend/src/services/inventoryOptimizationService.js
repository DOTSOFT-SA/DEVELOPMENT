import api from "./api";
import {FAILED_FETCH_INVENTORY_OPTIMIZATIONS_EL, FAILED_INVENTORY_OPTIMIZATION_EL} from "../utils/constants";
import {withRetry} from "../utils/shared.js";

/**
 * Runs an inventory optimization request.
 * If inventory_params is omitted or null, it will still process.
 *
 * @param {number} sku_number - The SKU number to optimize.
 * @param {number} user_id - The user's ID.
 * @param {Object} [inventory_params] - Optional inventory parameters for customization.
 * @returns {Promise<Object>} - The response containing inventory_params and inventory_optimization fields.
 * @throws {Object|Error} - Throws an error if the request fails.
 */
export const runInventoryOptimization = async (sku_number, user_id, inventory_params = null) => {
    try {
        const response = await withRetry(() =>
            api.post("/api/run_inventory_optimization/", {
                sku_number,
                user_id,
                inventory_params,
            })
        );
        return response.data; // { inventory_params: {...}, inventory_optimization: {...} }
    } catch (error) {
        console.error("Error running inventory optimization:", error);
        throw error.response
            ? error.response.data
            : new Error(FAILED_INVENTORY_OPTIMIZATION_EL);
    }
};

/**
 * Fetches all inventory optimization records for a given user.
 *
 * @param {number} userId - The ID of the user to retrieve optimization records for.
 * @returns {Promise<Array>} - An array of inventory optimization records.
 * @throws {Object|Error} - Throws an error if the request fails.
 */
export const fetchAllInventoryOptimizations = async (userId) => {
    try {
        const response = await api.get("/api/get_all_inventory_optimizations/", {
            params: {user_id: userId}
        });
        return response.data; // array of optimization records
    } catch (error) {
        console.error("Error fetching inventory optimizations:", error);
        throw error.response
            ? error.response.data
            : new Error(FAILED_FETCH_INVENTORY_OPTIMIZATIONS_EL);
    }
};

/**
 * Fetches the inventory parameters for a given SKU.
 *
 * @param {number} sku_number - The SKU number.
 * @param {number} user_id - The user's ID.
 * @returns {Promise<Object>} - The inventory parameters.
 */
export const fetchSkuInventoryParams = async (sku_number, user_id) => {
    try {
        const response = await withRetry(() =>
            api.post("/api/get_sku_inventory_params/", {
                sku_number,
                user_id
            })
        );
        return response.data;
    } catch (error) {
        console.error("Error fetching SKU inventory params:", error);
        throw error.response ? error.response.data : new Error("Failed to fetch inventory parameters");
    }
};
