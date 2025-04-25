import React from "react";
import { Box, CircularProgress, Typography } from "@mui/material";

/**
 * Loader component that matches the loading screen from ProtectedRoute.jsx
 * @param {boolean} open - Controls the visibility of the loader.
 */
const Loader = ({ open }) => {
    if (!open) return null; // Ensures it only renders when needed

    return (
        <Box
            sx={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                height: "100vh",
                width: "100vw",
                position: "fixed",
                top: 0,
                left: 0,
                backgroundColor: "rgba(255, 255, 255, 0.6)", // Transparent white background
                zIndex: 1300, // Ensures it appears above all content
            }}
        >
            <CircularProgress size={80} sx={{ color: "#1976D2" }} />
            <Typography variant="h6" sx={{ mt: 2, color: "black" }}>
                Loading...
            </Typography>
        </Box>
    );
};

export default Loader;
