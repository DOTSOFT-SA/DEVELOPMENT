import React, { useState, useEffect } from "react";
import {
    Box,
    Modal,
    Typography,
    TextField,
    Checkbox,
    FormControlLabel,
    Button,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Grid,
    InputAdornment,
    IconButton
} from "@mui/material";
import { Visibility, VisibilityOff, Close } from "@mui/icons-material";
import { createUser, fetchAllUsers, createOrUpdateUserErpApi } from "../../services/userService";
import { PRIVILEGES, ROLES } from "../../utils/enums";
import { SUCCESS_CREATE_USER_BUT_FAILED_CREATE_USER_ERP_API } from "../../utils/constants";

/**
 * A list of all possible privileges for the user, displayed as checkboxes.
 */
const ALL_PRIVILEGES = Object.values(PRIVILEGES).filter(
    (priv) => priv !== PRIVILEGES.ADMIN_PRIVILEGE
);

const AddUserModal = ({ open, onClose, onUserCreated }) => {
    // Basic user fields
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [role] = useState(ROLES.USER); // Locked to "ΧΡΗΣΤΗΣ"
    const [privileges, setPrivileges] = useState([]);

    // Show/hide password
    const [showPassword, setShowPassword] = useState(false);

    // ERP API fields (all mandatory)
    const [clientName, setClientName] = useState("");
    const [loginTokenUrl, setLoginTokenUrl] = useState("");
    const [skuOrderUrl, setSkuOrderUrl] = useState("");
    const [inventoryParamsUrl, setInventoryParamsUrl] = useState("");
    const [distributionRoutingUrl, setDistributionRoutingUrl] = useState("");
    const [skuOrderLatestUrl, setSkuOrderLatestUrl] = useState("");
    const [inventoryParamsLatestUrl, setInventoryParamsLatestUrl] = useState("");
    const [tokenUsername, setTokenUsername] = useState("");
    const [tokenPassword, setTokenPassword] = useState("");

    /**
     * States to track whether each mandatory field is empty.
     * If true, the field is highlighted in red and shows a helper text.
     */
    const [fieldErrors, setFieldErrors] = useState({
        email: false,
        password: false,
        clientName: false,
        loginTokenUrl: false,
        skuOrderUrl: false,
        inventoryParamsUrl: false,
        distributionRoutingUrl: false,
        skuOrderLatestUrl: false,
        inventoryParamsLatestUrl: false,
        tokenUsername: false,
        tokenPassword: false
    });

    /**
     * Toggles the password visibility for the 'password' field.
     */
    const handleTogglePassword = () => {
        setShowPassword((prev) => !prev);
    };

    /**
     * Toggles a privilege in the 'privileges' array.
     */
    const handlePrivilegeChange = (priv) => {
        if (privileges.includes(priv)) {
            setPrivileges(privileges.filter((p) => p !== priv));
        } else {
            setPrivileges([...privileges, priv]);
        }
    };

    /* privilege-based enable / disable */
    const hasDemandForecasting = privileges.includes(PRIVILEGES.DEMAND_FORECASTING);
    const hasInventoryOptimization = privileges.includes(PRIVILEGES.INVENTORY_OPTIMIZATION);
    const hasRouting = privileges.includes(PRIVILEGES.ROUTING);

    const disableSkuOrder = !(hasDemandForecasting || hasInventoryOptimization);
    const disableSkuOrderLatest = disableSkuOrder;
    const disableInventoryParams = !hasInventoryOptimization;
    const disableInventoryParamsLatest = !hasInventoryOptimization;
    const disableDistributionRouting = !hasRouting;

    /* clear disabled values */
    useEffect(() => {
        if (disableSkuOrder) setSkuOrderUrl("");
        if (disableSkuOrderLatest) setSkuOrderLatestUrl("");
        if (disableInventoryParams) setInventoryParamsUrl("");
        if (disableInventoryParamsLatest) setInventoryParamsLatestUrl("");
        if (disableDistributionRouting) setDistributionRoutingUrl("");
    }, [
        disableSkuOrder,
        disableSkuOrderLatest,
        disableInventoryParams,
        disableInventoryParamsLatest,
        disableDistributionRouting
    ]);

    /**
     * Checks each mandatory field. If empty, mark its error as true.
     * Returns true if any field is missing, false otherwise.
     */
    const checkMandatoryFields = () => {
        const newFieldErrors = {
            email: !email.trim(),
            password: !password.trim(),
            clientName: !clientName.trim(),
            loginTokenUrl: !loginTokenUrl.trim(),
            skuOrderUrl: disableSkuOrder ? false : !skuOrderUrl.trim(),
            inventoryParamsUrl: disableInventoryParams ? false : !inventoryParamsUrl.trim(),
            distributionRoutingUrl: disableDistributionRouting ? false : !distributionRoutingUrl.trim(),
            skuOrderLatestUrl: disableSkuOrderLatest ? false : !skuOrderLatestUrl.trim(),
            inventoryParamsLatestUrl: disableInventoryParamsLatest ? false : !inventoryParamsLatestUrl.trim(),
            tokenUsername: !tokenUsername.trim(),
            tokenPassword: !tokenPassword.trim()
        };

        setFieldErrors(newFieldErrors);

        // Return true if at least one field has an error (i.e. is missing or empty)
        return Object.values(newFieldErrors).some((val) => val === true);
    };

    /**
     * Creates the user, then re-fetches all users to find new user ID,
     * then creates/updates ERP API details. Notifies on success/failure.
     */
    const handleCreate = async () => {
        // Check mandatory fields; if any missing, highlight + block submission
        const missingFields = checkMandatoryFields();
        if (missingFields) {
            onUserCreated(false);
            return;
        }

        // Basic user object
        const newUser = {
            email,
            password,
            role, // locked to "ΧΡΗΣΤΗΣ"
            privilege_names: privileges
        };

        try {
            // Create the user
            await createUser(newUser);

            // Re-fetch users to find newly created user
            const allUsers = await fetchAllUsers();
            const createdUser = allUsers.find((u) => u.email === email);
            if (!createdUser) {
                onUserCreated(false);
                return;
            }

            // Create/Update ERP API details
            const erpPayload = {
                user_id: createdUser.id,
                client_name: clientName,
                login_token_url: loginTokenUrl,
                sku_order_url: skuOrderUrl || null,
                inventory_params_url: inventoryParamsUrl || null,
                distribution_routing_url: distributionRoutingUrl || null,
                sku_order_latest_url: skuOrderLatestUrl || null,
                inventory_params_latest_url: inventoryParamsLatestUrl || null,
                token_username: tokenUsername,
                token_password: tokenPassword
            };

            try {
                await createOrUpdateUserErpApi(erpPayload);
                onUserCreated(true);
            } catch {
                onUserCreated(false, SUCCESS_CREATE_USER_BUT_FAILED_CREATE_USER_ERP_API);
                onClose();
            }

            onClose();
        } catch {
            onUserCreated(false);
        }
    };

    return (
        <Modal open={open} onClose={onClose}>
            <Box
                sx={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                    width: 900,
                    bgcolor: "background.paper",
                    p: 4,
                    borderRadius: 2,
                    maxHeight: "93vh",
                    overflowY: "auto"
                }}
            >
                {/* "X" button at top-right to close */}
                <IconButton
                    onClick={onClose}
                    sx={{ position: "absolute", top: 8, right: 8 }}
                >
                    <Close />
                </IconButton>

                <Typography variant="h6" gutterBottom>
                    <b> Δημιουργία Νέου Χρήστη </b>
                </Typography>

                <Typography
                    variant="subtitle1"
                    sx={{
                        mb: 2,
                        borderBottom: "1px solid rgba(0, 0, 0, 0.2)",
                        display: "inline-block",
                        pb: 0
                    }}
                >
                    Εισάγετε τα στοιχεία σύνδεσης του χρήστη:
                </Typography>

                <Grid container spacing={2}>
                    {/* Email */}
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required
                            label="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            fullWidth
                            error={fieldErrors.email}
                            helperText={fieldErrors.email ? "Υποχρεωτικό πεδίο" : ""}
                        />
                    </Grid>

                    {/* Password with eye icon */}
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required
                            label="Κωδικός"
                            type={showPassword ? "text" : "password"}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            fullWidth
                            error={fieldErrors.password}
                            helperText={fieldErrors.password ? "Υποχρεωτικό πεδίο" : ""}
                            InputProps={{
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <IconButton onClick={handleTogglePassword} edge="end">
                                            {showPassword ? <VisibilityOff /> : <Visibility />}
                                        </IconButton>
                                    </InputAdornment>
                                )
                            }}
                        />
                    </Grid>

                    {/* Role dropdown - locked to ΧΡΗΣΤΗΣ */}
                    <Grid item xs={12} sm={6}>
                        <FormControl fullWidth>
                            <InputLabel id="role-label" sx={{ color: "#9e9e9e" }}>
                                Ρόλος
                            </InputLabel>
                            <Select
                                labelId="role-label"
                                label="Ρόλος"
                                value={role}
                                disabled
                                sx={{
                                    bgcolor: "#f5f5f5",
                                    color: "#9e9e9e",
                                    "& .MuiOutlinedInput-notchedOutline": {
                                        borderColor: "#bdbdbd !important"
                                    }
                                }}
                            >
                                <MenuItem value={ROLES.USER}>{ROLES.USER}</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>

                    {/* Privileges */}
                    <Grid item xs={12}>

                        <Typography
                            variant="subtitle1"
                            sx={{
                                mt: 2,
                                borderBottom: "1px solid rgba(0, 0, 0, 0.2)",
                                display: "inline-block",
                                pb: 0
                            }}
                        >
                            Επιλέξτε τις λειτουργίες που θα έχει πρόσβαση ο χρήστης:
                        </Typography>
                        <Grid>
                            {ALL_PRIVILEGES.map((priv) => (
                                <FormControlLabel
                                    key={priv}
                                    control={
                                        <Checkbox
                                            checked={privileges.includes(priv)}
                                            onChange={() => handlePrivilegeChange(priv)}
                                        />
                                    }
                                    label={priv}
                                />
                            ))}
                        </Grid>
                    </Grid>

                    {/* ERP API heading */}
                    <Grid item xs={12}>
                        <Typography
                            variant="subtitle1"
                            sx={{
                                mt: 1,
                                borderBottom: "1px solid rgba(0, 0, 0, 0.2)",
                                display: "inline-block",
                                pb: 0
                            }}
                        >
                            Εισάγετε τα API URLs για τη σύνδεση του ERP με την Πλατφόρμα Development:
                        </Typography>
                    </Grid>

                    {/* ERP API fields — Group 1: Top three fields */}
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required
                            label="Επωνυμία Επιχείρησης"
                            value={clientName}
                            onChange={(e) => setClientName(e.target.value)}
                            fullWidth
                            error={fieldErrors.clientName}
                            helperText={fieldErrors.clientName ? "Υποχρεωτικό πεδίο" : ""}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required
                            label="Token Όνομα Χρήστη"
                            value={tokenUsername}
                            onChange={(e) => setTokenUsername(e.target.value)}
                            fullWidth
                            error={fieldErrors.tokenUsername}
                            helperText={fieldErrors.tokenUsername ? "Υποχρεωτικό πεδίο" : ""}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required
                            label="Token Κωδικός"
                            type="password"
                            value={tokenPassword}
                            onChange={(e) => setTokenPassword(e.target.value)}
                            fullWidth
                            error={fieldErrors.tokenPassword}
                            helperText={fieldErrors.tokenPassword ? "Υποχρεωτικό πεδίο" : ""}
                        />
                    </Grid>

                    {/* Divider for grouping */}
                    <Grid item xs={12}>
                        <Box sx={{ my: 0 }}></Box>
                    </Grid>

                    {/* ERP API fields — Group 2: Remaining fields */}
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required
                            label="Διεύθυνση API URL Login Token"
                            placeholder="http://localhost:7000/auth/login-token"
                            value={loginTokenUrl}
                            onChange={(e) => setLoginTokenUrl(e.target.value)}
                            fullWidth
                            error={fieldErrors.loginTokenUrl}
                            helperText={fieldErrors.loginTokenUrl ? "Υποχρεωτικό πεδίο" : ""}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required={!disableSkuOrder}
                            disabled={disableSkuOrder}
                            label="Διεύθυνση API URL Παραγγελιών SKU"
                            placeholder="http://localhost:7000/api/sku_order_development"
                            value={skuOrderUrl}
                            onChange={(e) => setSkuOrderUrl(e.target.value)}
                            fullWidth
                            error={fieldErrors.skuOrderUrl}
                            helperText={fieldErrors.skuOrderUrl && !disableSkuOrder ? "Υποχρεωτικό πεδίο" : ""}
                            sx={{
                                "& .MuiInputBase-root.Mui-disabled": {
                                    backgroundColor: "#f0f0f0"
                                }
                            }}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required={!disableInventoryParams}
                            disabled={disableInventoryParams}
                            label="Διεύθυνση API URL Παραμέτρων Αποθέματος"
                            placeholder="http://localhost:7000/api/inventory_params_development"
                            value={inventoryParamsUrl}
                            onChange={(e) => setInventoryParamsUrl(e.target.value)}
                            fullWidth
                            error={fieldErrors.inventoryParamsUrl}
                            helperText={fieldErrors.inventoryParamsUrl && !disableInventoryParams ? "Υποχρεωτικό πεδίο" : ""}
                            sx={{
                                "& .MuiInputBase-root.Mui-disabled": {
                                    backgroundColor: "#f0f0f0"
                                }
                            }}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required={!disableDistributionRouting}
                            disabled={disableDistributionRouting}
                            label="Διεύθυνση API URL Δρομολόγησης"
                            placeholder="http://localhost:7000/api/distribution_routing_data"
                            value={distributionRoutingUrl}
                            onChange={(e) => setDistributionRoutingUrl(e.target.value)}
                            fullWidth
                            error={fieldErrors.distributionRoutingUrl}
                            helperText={fieldErrors.distributionRoutingUrl && !disableDistributionRouting ? "Υποχρεωτικό πεδίο" : ""}
                            sx={{
                                "& .MuiInputBase-root.Mui-disabled": {
                                    backgroundColor: "#f0f0f0"
                                }
                            }}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required={!disableSkuOrderLatest}
                            disabled={disableSkuOrderLatest}
                            label="Διεύθυνση API URL Τελευταίας Παραγγελίας SKU"
                            placeholder="http://localhost:7000/api/sku_order_latest"
                            value={skuOrderLatestUrl}
                            onChange={(e) => setSkuOrderLatestUrl(e.target.value)}
                            fullWidth
                            error={fieldErrors.skuOrderLatestUrl}
                            helperText={fieldErrors.skuOrderLatestUrl && !disableSkuOrderLatest ? "Υποχρεωτικό πεδίο" : ""}
                            sx={{
                                "& .MuiInputBase-root.Mui-disabled": {
                                    backgroundColor: "#f0f0f0"
                                }
                            }}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required={!disableInventoryParamsLatest}
                            disabled={disableInventoryParamsLatest}
                            label="Διεύθυνση API URL Πρόσφατων Παραμέτρων Αποθέματος SKU"
                            placeholder="http://localhost:7000/api/get_inventory_params_development_latest"
                            value={inventoryParamsLatestUrl}
                            onChange={(e) => setInventoryParamsLatestUrl(e.target.value)}
                            fullWidth
                            error={fieldErrors.inventoryParamsLatestUrl}
                            helperText={fieldErrors.inventoryParamsLatestUrl && !disableInventoryParamsLatest ? "Υποχρεωτικό πεδίο" : ""}
                            sx={{
                                "& .MuiInputBase-root.Mui-disabled": {
                                    backgroundColor: "#f0f0f0"
                                }
                            }}
                        />
                    </Grid>
                    {/* Buttons row */}
                    <Grid item xs={10} sx={{ display: "flex", gap: 2 }}>
                        <Button variant="contained" onClick={handleCreate}>
                            ΑΠΟΘΗΚΕΥΣΗ
                        </Button>
                        <Button variant="outlined" onClick={onClose}>
                            ΑΚΥΡΩΣΗ
                        </Button>
                    </Grid>
                </Grid>
            </Box>
        </Modal>
    );
};

export default AddUserModal;
