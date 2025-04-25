import React, { useState, useEffect } from "react";
import {
    Box,
    Modal,
    Typography,
    TextField,
    Checkbox,
    FormControlLabel,
    Button,
    Grid,
    IconButton,
    InputAdornment
} from "@mui/material";
import { Close, Visibility, VisibilityOff } from "@mui/icons-material";
import {
    updateUser,
    fetchUserErpApi,
    createOrUpdateUserErpApi
} from "../../services/userService";
import { FAILED_UPDATE } from "../../utils/constants";
import { PRIVILEGES, ROLES } from "../../utils/enums";

/**
 * A list of all possible privileges for the user, displayed as checkboxes (excluding ADMIN_PRIVILEGE).
 */
const ALL_PRIVILEGES = Object.values(PRIVILEGES).filter(
    (p) => p !== PRIVILEGES.ADMIN_PRIVILEGE
);


const UserEditModal = ({ open, onClose, user, onUserUpdated }) => {
    // Basic user states
    const [email, setEmail] = useState(user.email);
    const [isActive, setIsActive] = useState(user.is_active);
    const [privileges, setPrivileges] = useState([...user.privilege_names]);

    /* Role is locked to the original value */
    const [role] = useState(user.role);

    // ERP API fields
    const [clientName, setClientName] = useState("");
    const [loginTokenUrl, setLoginTokenUrl] = useState("");
    const [skuOrderUrl, setSkuOrderUrl] = useState("");
    const [inventoryParamsUrl, setInventoryParamsUrl] = useState("");
    const [distributionRoutingUrl, setDistributionRoutingUrl] = useState("");
    const [skuOrderLatestUrl, setSkuOrderLatestUrl] = useState("");
    const [inventoryParamsLatestUrl, setInventoryParamsLatestUrl] = useState("");
    const [tokenUsername, setTokenUsername] = useState("");
    const [tokenPassword, setTokenPassword] = useState("");

    /* Show/hide the token password */
    const [showTokenPassword, setShowTokenPassword] = useState(false);

    /* Track which mandatory fields are missing */
    const [fieldErrors, setFieldErrors] = useState({
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
     * Toggles a privilege in the privileges array.
     */
    const handlePrivilegeChange = (priv) => {
        if (privileges.includes(priv)) {
            setPrivileges(privileges.filter((p) => p !== priv));
        } else {
            setPrivileges([...privileges, priv]);
        }
    };

    /**
     * Toggles the token password field between hidden/unhidden.
     */
    const handleToggleTokenPassword = () => setShowTokenPassword((prev) => !prev);

    /**
     * Field-enable / disable rules based on privileges.
     */
    const hasDemandForecasting = privileges.includes(PRIVILEGES.DEMAND_FORECASTING);
    const hasInventoryOpt      = privileges.includes(PRIVILEGES.INVENTORY_OPTIMIZATION);
    const hasRouting           = privileges.includes(PRIVILEGES.ROUTING);
    /* Token URL is always enabled; the rest follow the matrix */
    const disableSkuOrder            = !(hasDemandForecasting);
    const disableSkuOrderLatest      = !(hasDemandForecasting);
    const disableInventoryParams     = !(hasInventoryOpt);
    const disableInventoryParamsLast = !(hasInventoryOpt);
    const disableDistributionRouting = !(hasRouting);
    /* A small grey background for disabled inputs */
    const disabledSx = {
        "& .MuiInputBase-root.Mui-disabled": { backgroundColor: "#f0f0f0" }
    };

    /**
     * Checks if mandatory ERP fields are filled; highlights in red if missing.
     * Returns true if any field is missing => block submission.
     */
    const checkMandatoryFields = () => {
        const newFieldErrors = {
            clientName: !clientName.trim(),
            loginTokenUrl: !loginTokenUrl.trim(),
            skuOrderUrl: disableSkuOrder ? false : !skuOrderUrl.trim(),
            inventoryParamsUrl: disableInventoryParams ? false : !inventoryParamsUrl.trim(),
            distributionRoutingUrl: disableDistributionRouting ? false : !distributionRoutingUrl.trim(),
            skuOrderLatestUrl: disableSkuOrderLatest ? false : !skuOrderLatestUrl.trim(),
            inventoryParamsLatestUrl: disableInventoryParamsLast ? false : !inventoryParamsLatestUrl.trim(),
            tokenUsername: !tokenUsername.trim(),
            tokenPassword: !tokenPassword.trim()
        };
        setFieldErrors(newFieldErrors);

        return Object.values(newFieldErrors).some(Boolean);
    };

    /**
     * Saves the updated user data + ERP details.
     * If missing fields => do not call onUserUpdated => modal remains open.
     */
    const handleSave = async () => {
        // 1) Check mandatory ERP fields
        if (checkMandatoryFields()) return;

        // 2) Build updated user object
        const updatedUser = {
            id: user.id,
            email,
            role,
            is_active: isActive,
            // Force date fields to null so backend doesn't overwrite them
            created_at: null,
            updated_at: null,
            login_at: null,
            privilege_names: privileges
        };

        try {
            // 3) Update the user
            const resp = await updateUser(updatedUser);
            // resp => { message, updated_user }
            const updatedUserFromResp = resp.updated_user;

            // 4) Create/Update ERP API details - Build ERP payload (leave disabled fields null) */
            const erpPayload = {
                user_id: updatedUserFromResp.id,
                client_name: clientName,
                login_token_url: loginTokenUrl,
                sku_order_url: disableSkuOrder ? null : skuOrderUrl,
                inventory_params_url: disableInventoryParams ? null : inventoryParamsUrl,
                distribution_routing_url: disableDistributionRouting ? null : distributionRoutingUrl,
                sku_order_latest_url: disableSkuOrderLatest ? null : skuOrderLatestUrl,
                inventory_params_latest_url: disableInventoryParamsLast ? null : inventoryParamsLatestUrl,
                token_username: tokenUsername,
                token_password: tokenPassword
            };
            await createOrUpdateUserErpApi(erpPayload);

            // 5) If everything succeeds => call onUserUpdated(..., true) => parent can close modal
            onUserUpdated(updatedUserFromResp, true);
        } catch (error) {
            console.error(FAILED_UPDATE, error);
            // If the update fails => notify parent => parent typically shows error & closes
            onUserUpdated(user, false);
        }
    };

    /**
     * Fetches existing ERP data on mount/open, storing in local states for editing.
     */
    useEffect(() => {
        const loadErpData = async () => {
            try {
                const data = await fetchUserErpApi(user.id);
                setClientName(data.client_name || "");
                setLoginTokenUrl(data.login_token_url || "");
                setSkuOrderUrl(data.sku_order_url || "");
                setInventoryParamsUrl(data.inventory_params_url || "");
                setDistributionRoutingUrl(data.distribution_routing_url || "");
                setSkuOrderLatestUrl(data.sku_order_latest_url || "");
                setInventoryParamsLatestUrl(data.inventory_params_latest_url || "");
                setTokenUsername(data.token_username || "");
                setTokenPassword(data.token_password || "");
            } catch (err) {
                // If user has no ERP record, fields remain empty
                console.warn("No existing ERP data or fetch error:", err);
            }
        };
        if (open && user?.id) {
            loadErpData();
        }
    }, [open, user]);

    return (
        <Modal open={open} onClose={onClose}>
            <Box
                sx={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                    width: 1100,
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

                <Typography variant="h6" gutterBottom>
                    <b>Επεξεργασία Χρήστη</b>
                </Typography>

                {/* User info heading */}
                <Grid item xs={12}>
                    <Typography
                        variant="subtitle1"
                        sx={{
                            mb: 2,
                            borderBottom: "1px solid rgba(0, 0, 0, 0.2)",
                            display: "inline-block",
                            pb: 0
                        }}
                    >
                        Στοιχεία Χρήστη:
                    </Typography>
                </Grid>


                <Grid container spacing={2}>
                    {/* Email field */}
                    <Grid item xs={12} sm={6}>
                        <TextField
                            label="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            fullWidth
                        />
                    </Grid>

                    {/* isActive checkbox */}
                    <Grid item xs={12} sm={6}>
                        <FormControlLabel
                            control={
                                <Checkbox
                                    checked={isActive}
                                    onChange={(e) => setIsActive(e.target.checked)}
                                />
                            }
                            label="Ενεργός"
                            sx={{ mt: 1 }}
                        />
                    </Grid>

                    {/* Privileges checkboxes */}
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
                            Λειτουργίες:
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
                                mt: 2,
                                borderBottom: "1px solid rgba(0, 0, 0, 0.2)",
                                display: "inline-block",
                                pb: 0
                            }}
                        >
                            Ρυθμίσεις ERP API:
                        </Typography>
                    </Grid>

                    {/* Client name field */}
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required
                            label="Επωνυμία Επιχείρησης"
                            value={clientName}
                            onChange={(e) => setClientName(e.target.value)}
                            fullWidth
                            error={fieldErrors.clientName}
                            helperText={fieldErrors.clientName ? "Υποχρεωτικό πεδίο" : ""}
                            sx={{ mt: 1 }}
                        />
                    </Grid>

                    {/* Token Username field */}
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required
                            label="Token Όνομα Χρήστη"
                            value={tokenUsername}
                            onChange={(e) => setTokenUsername(e.target.value)}
                            fullWidth
                            error={fieldErrors.tokenUsername}
                            helperText={fieldErrors.tokenUsername ? "Υποχρεωτικό πεδίο" : ""}
                            sx={{ mt: 1 }}
                        />
                    </Grid>

                    {/* Token Password field (with eye icon) */}
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required
                            label="Token Κωδικός"
                            type={showTokenPassword ? "text" : "password"}
                            value={tokenPassword}
                            onChange={(e) => setTokenPassword(e.target.value)}
                            fullWidth
                            error={fieldErrors.tokenPassword}
                            helperText={fieldErrors.tokenPassword ? "Υποχρεωτικό πεδίο" : ""}
                            InputProps={{
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <IconButton
                                            onClick={handleToggleTokenPassword}
                                            edge="end"
                                        >
                                            {showTokenPassword ? <VisibilityOff /> : <Visibility />}
                                        </IconButton>
                                    </InputAdornment>
                                )
                            }}
                        />
                    </Grid>

                    {/* Divider for visual separation */}
                    <Grid item xs={12}>
                        <Box sx={{ my: 1 }} />
                    </Grid>

                    {/* LOGIN TOKEN API URL */}
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required
                            label="Διεύθυνση API URL Login Token"
                            value={loginTokenUrl}
                            onChange={(e) => setLoginTokenUrl(e.target.value)}
                            fullWidth
                            error={fieldErrors.loginTokenUrl}
                            helperText={fieldErrors.loginTokenUrl ? "Υποχρεωτικό πεδίο" : ""}
                        />
                    </Grid>

                    {/* SKU ORDER API URL */}
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required={!disableSkuOrder}
                            disabled={disableSkuOrder}
                            label="Διεύθυνση API URL Παραγγελιών SKU"
                            value={skuOrderUrl}
                            onChange={(e) => setSkuOrderUrl(e.target.value)}
                            fullWidth
                            error={fieldErrors.skuOrderUrl}
                            helperText={
                                fieldErrors.skuOrderUrl && !disableSkuOrder
                                    ? "Υποχρεωτικό πεδίο"
                                    : ""
                            }
                            sx={disableSkuOrder ? disabledSx : {}}
                        />
                    </Grid>

                    {/* INVENTORY PARAMS API URL */}
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required={!disableInventoryParams}
                            disabled={disableInventoryParams}
                            label="Διεύθυνση API URL Παραμέτρων Αποθέματος"
                            value={inventoryParamsUrl}
                            onChange={(e) => setInventoryParamsUrl(e.target.value)}
                            fullWidth
                            error={fieldErrors.inventoryParamsUrl}
                            helperText={
                                fieldErrors.inventoryParamsUrl && !disableInventoryParams
                                    ? "Υποχρεωτικό πεδίο"
                                    : ""
                            }
                            sx={disableInventoryParams ? disabledSx : {}}
                        />
                    </Grid>

                    {/* DISTRIBUTION ROUTING API URL */}
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required={!disableDistributionRouting}
                            disabled={disableDistributionRouting}
                            label="Διεύθυνση API URL Δρομολόγησης"
                            value={distributionRoutingUrl}
                            onChange={(e) => setDistributionRoutingUrl(e.target.value)}
                            fullWidth
                            error={fieldErrors.distributionRoutingUrl}
                            helperText={
                                fieldErrors.distributionRoutingUrl && !disableDistributionRouting
                                    ? "Υποχρεωτικό πεδίο"
                                    : ""
                            }
                            sx={disableDistributionRouting ? disabledSx : {}}
                        />
                    </Grid>

                    {/* SKU ORDER LATEST API URL */}
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required={!disableSkuOrderLatest}
                            disabled={disableSkuOrderLatest}
                            label="Διεύθυνση API URL Τελευταίας Παραγγελίας SKU"
                            value={skuOrderLatestUrl}
                            onChange={(e) => setSkuOrderLatestUrl(e.target.value)}
                            fullWidth
                            error={fieldErrors.skuOrderLatestUrl}
                            helperText={
                                fieldErrors.skuOrderLatestUrl && !disableSkuOrderLatest
                                    ? "Υποχρεωτικό πεδίο"
                                    : ""
                            }
                            sx={disableSkuOrderLatest ? disabledSx : {}}
                        />
                    </Grid>

                    {/* INVENTORY PARAMS LATEST API URL */}
                    <Grid item xs={12} sm={6}>
                        <TextField
                            required={!disableInventoryParamsLast}
                            disabled={disableInventoryParamsLast}
                            label="Διεύθυνση API URL Πρόσφατων Παραμέτρων Αποθέματος SKU"
                            value={inventoryParamsLatestUrl}
                            onChange={(e) => setInventoryParamsLatestUrl(e.target.value)}
                            fullWidth
                            error={fieldErrors.inventoryParamsLatestUrl}
                            helperText={
                                fieldErrors.inventoryParamsLatestUrl && !disableInventoryParamsLast
                                    ? "Υποχρεωτικό πεδίο"
                                    : ""
                            }
                            sx={disableInventoryParamsLast ? disabledSx : {}}
                        />
                    </Grid>

                    {/* Buttons row */}
                    <Grid item xs={12} sx={{ display: "flex", gap: 2, mt: 3 }}>
                        <Button variant="contained" onClick={handleSave}>
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

export default UserEditModal;
