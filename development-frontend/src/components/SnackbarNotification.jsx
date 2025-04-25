import React from "react";
import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";

/**
 * Snackbar Notification Component for displaying success or error messages.
 * @param {boolean} open - Controls visibility of the snackbar.
 * @param {function} onClose - Function to handle closing of the snackbar.
 * @param {string} message - Message to display in the snackbar.
 * @param {string} severity - Type of alert: "success" or "error".
 */
const SnackbarNotification = ({ open, onClose, message, severity }) => {
    return (
        <Snackbar open={open} autoHideDuration={6000} onClose={onClose}>
            <MuiAlert onClose={onClose} severity={severity} variant="filled">
                {message}
            </MuiAlert>
        </Snackbar>
    );
};

export default SnackbarNotification;
