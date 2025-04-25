import api from "./api.js";
import {FAILED_DEMAND_FORECASTING_EL, FAILED_FETCH_SKU_ORDER_PREDICTIONS_EL} from "../utils/constants.js";
import {withRetry} from "../utils/shared.js";

/**
 * Demand Forecasting Service
 * This service handles API calls related to SKU order quantity inference.
 */

/**
 * Fetches demand forecasting data for a given SKU number.
 *
 * @param {number} skuNumber - The SKU number for which demand forecasting is required.
 * @param {number} userId - The user ID making the request.
 * @returns {Promise<Object>} - The response containing prediction input and output data.
 * @throws {Object|Error} - Throws an error if the request fails.
 */
export const run_inference = async (skuNumber, userId) => {
    try {
        const response = await withRetry(() =>
            api.post("api/run_inference/", {sku_number: skuNumber, user_id: userId})
        );
        return response.data; // Contains merged_sku_metric & sku_order_quantity_prediction
    } catch (error) {
        console.error("Error fetching demand forecasting data:", error);
        throw error.response ? error.response.data : new Error(FAILED_DEMAND_FORECASTING_EL);
    }
};

/**
 * Fetches all SKU order quantity predictions for a specific user.
 *
 * @param {number} userId - The ID of the user to retrieve predictions for.
 * @returns {Promise<Array>} - An array of SKU order quantity predictions.
 * @throws {Object|Error} - Throws an error if the request fails.
 */
export const fetchAllSkuOrderQuantityPredictions = async (userId) => {
    try {
        // Example URL: /api/get_all_sku_order_quantity_predictions?user_id=2
        const response = await api.get(`/api/get_all_sku_order_quantity_predictions/`, {
            params: { user_id: userId }
        });
        return response.data; // Array of predictions
    } catch (error) {
        console.error("Error fetching SKU order quantity predictions:", error);
        throw error.response ? error.response.data : new Error(FAILED_FETCH_SKU_ORDER_PREDICTIONS_EL);
    }
};