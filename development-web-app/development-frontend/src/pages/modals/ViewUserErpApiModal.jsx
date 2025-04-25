import React, { useEffect, useState } from "react";
import {
    Box,
    Modal,
    Typography,
    IconButton,
    Grid,
    TextField,
    InputAdornment
} from "@mui/material";
import { Close, Visibility, VisibilityOff } from "@mui/icons-material";
import { fetchUserErpApi } from "../../services/userService";

const disabledFieldStyle = {
    bgcolor: "#f5f5f5",
    "& .MuiInputBase-input.Mui-disabled": {
        WebkitTextFillColor: "#9e9e9e"
    },
    "& .MuiOutlinedInput-notchedOutline": {
        borderColor: "#bdbdbd !important"
    }
};

const ViewUserErpApiModal = ({ open, onClose, user }) => {
    const [erpData, setErpData] = useState(null);
    const [showTokenPassword, setShowTokenPassword] = useState(false);

    useEffect(() => {
        if (user && open) {
            fetchErpApiData(user.id);
        }
    }, [user, open]);

    const fetchErpApiData = async (userId) => {
        try {
            const data = await fetchUserErpApi(userId);
            setErpData(data);
        } catch (err) {
            console.error("Failed to fetch ERP API data:", err);
        }
    };

    /**
     * Toggle the visibility of the token password field
     */
    const handleToggleTokenPassword = () => {
        setShowTokenPassword((prev) => !prev);
    };

    return (
        <Modal open={open} onClose={onClose}>
            <Box
                sx={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                    width: 1100, // Wider modal
                    bgcolor: "background.paper",
                    p: 4,
                    borderRadius: 2,
                    maxHeight: "90vh",
                    overflowY: "auto"
                }}
            >
                {/* "X" button to close */}
                <IconButton
                    onClick={onClose}
                    sx={{ position: "absolute", top: 8, right: 8 }}
                >
                    <Close />
                </IconButton>

                <Typography variant="h6" gutterBottom sx={{mb:2.5}}>
                    ERP API Πληροφορίες ({user.email})
                </Typography>

                {erpData ? (
                    <Grid container spacing={2}>
                        {/* Client Name */}
                        <Grid item xs={12} sm={6}>
                            <TextField label="Επωνυμία Επιχείρησης" value={erpData.client_name || ""} disabled fullWidth sx={disabledFieldStyle} />
                        </Grid>

                        {/* Token Fields */}
                        <Grid item xs={12} sm={6}>
                            <TextField label="Token Όνομα Χρήστη" value={erpData.token_username || ""} disabled fullWidth sx={disabledFieldStyle} />
                        </Grid>

                        <Grid item xs={12} sm={6}>
                            <TextField
                                label="Token Κωδικός"
                                type={showTokenPassword ? "text" : "password"}
                                value={erpData.token_password || ""}
                                disabled
                                fullWidth
                                sx={disabledFieldStyle}
                                InputProps={{
                                    endAdornment: (
                                        <InputAdornment position="end">
                                            <IconButton onClick={handleToggleTokenPassword} edge="end">
                                                {showTokenPassword ? <VisibilityOff /> : <Visibility />}
                                            </IconButton>
                                        </InputAdornment>
                                    ),
                                    readOnly: true
                                }}
                            />
                        </Grid>

                        {/* Divider for visual separation */}
                        <Grid item xs={12}>
                            <Box sx={{ my: 1 }}>
                                {/*<hr style={{ borderColor: "#ccc" }} />*/}
                            </Box>
                        </Grid>

                        {/* LOGIN TOKEN API URL */}
                        <Grid item xs={12} sm={6}>
                            <TextField
                                label="Διεύθυνση API URL Login Token"
                                value={erpData.login_token_url || ""}
                                disabled
                                fullWidth
                                sx={disabledFieldStyle}
                            />
                        </Grid>

                        {/* SKU ORDER API URL */}
                        <Grid item xs={12} sm={6}>
                            <TextField
                                label="Διεύθυνση API URL Παραγγελιών SKU"
                                value={erpData.sku_order_url || ""}
                                disabled
                                fullWidth
                                sx={disabledFieldStyle}
                            />
                        </Grid>

                        {/* INVENTORY PARAMS API URL */}
                        <Grid item xs={12} sm={6}>
                            <TextField
                                label="Διεύθυνση API URL Παραμέτρων Αποθέματος"
                                value={erpData.inventory_params_url || ""}
                                disabled
                                fullWidth
                                sx={disabledFieldStyle}
                            />
                        </Grid>

                        {/* DISTRIBUTION ROUTING API URL */}
                        <Grid item xs={12} sm={6}>
                            <TextField
                                label="Διεύθυνση API URL Δρομολόγησης"
                                value={erpData.distribution_routing_url || ""}
                                disabled
                                fullWidth
                                sx={disabledFieldStyle}
                            />
                        </Grid>

                        {/* SKU ORDER LATEST API URL */}
                        <Grid item xs={12} sm={6}>
                            <TextField
                                label="Διεύθυνση API URL Τελευταίας Παραγγελίας SKU"
                                value={erpData.sku_order_latest_url || ""}
                                disabled
                                fullWidth
                                sx={disabledFieldStyle}
                            />
                        </Grid>

                        {/* INVENTORY PARAMS LATEST API URL */}
                        <Grid item xs={12} sm={6}>
                            <TextField
                                label="Διεύθυνση API URL Πρόσφατων Παραμέτρων Αποθέματος SKU"
                                value={erpData.inventory_params_latest_url || ""}
                                disabled
                                fullWidth
                                sx={disabledFieldStyle}
                            />
                        </Grid>
                    </Grid>
                ) : (
                    <Typography variant="body1" sx={{ mt: 2 }}>
                        Φόρτωση δεδομένων ERP API...
                    </Typography>
                )}
            </Box>
        </Modal>
    );
};

export default ViewUserErpApiModal;
