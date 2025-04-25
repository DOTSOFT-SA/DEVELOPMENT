import * as React from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import {
    AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemIcon, ListItemText, Divider, IconButton, Menu, MenuItem, Box
} from "@mui/material";
import HomeIcon from "@mui/icons-material/Home";
import AssessmentIcon from "@mui/icons-material/Assessment";
import InventoryIcon from "@mui/icons-material/Warehouse";
import SupervisedUserCircleIcon from "@mui/icons-material/SupervisedUserCircle";
import DirectionsIcon from "@mui/icons-material/Navigation";
import AccountCircle from "@mui/icons-material/AccountCircle";
import { PRIVILEGES } from "../utils/enums";
import { logout } from "../services/authService.js";
import SnackbarNotification from "../components/SnackbarNotification";
import ChangePasswordModal from "./modals/ChangePasswordModal";

// Import the images
import developmentLogo from "../assets/DEVELOPMENT_logo.png";
import {ADMIN_DASHBOARD_TITLE, USER_DASHBOARD_TITLE} from "../utils/constants.js";

const drawerWidth = 240;

function Dashboard() {
    const [anchorEl, setAnchorEl] = React.useState(null);  // For the account menu
    const navigate = useNavigate();
    const userEmail = localStorage.getItem("userEmail");
    const userPrivileges = localStorage.getItem("privileges")?.split(",");
    const [changePasswordOpen, setChangePasswordOpen] = React.useState(false);
    const [snackbarOpen, setSnackbarOpen] = React.useState(false);
    const [snackbarMessage, setSnackbarMessage] = React.useState("");
    const [snackbarSeverity, setSnackbarSeverity] = React.useState("success");

    // Function to check if the user has a privilege (checks in enums.js)
    const hasPrivilege = (privilege) => userPrivileges?.includes(privilege);

    // Function to handle account menu
    const handleMenu = (event) => setAnchorEl(event.currentTarget);
    const handleCloseMenu = () => setAnchorEl(null);

    // Logout handler
    const handleLogout = () => {
        logout();
        navigate("/");
    };

    const handleOpenChangePassword = () => {
        setAnchorEl(null); // close the account menu
        setChangePasswordOpen(true);
    };
    const handleCloseChangePassword = () => {
        setChangePasswordOpen(false);
    };

    /**
     * Called by the ChangePasswordModal upon success/failure.
     * Shows a Snackbar in the Dashboard.
     * @param {boolean} success - true if password changed successfully
     * @param {string} message - the success or error message
     */
    const handleChangePasswordResult = (success, message) => {
        setSnackbarMessage(message);
        setSnackbarSeverity(success ? "success" : "error");
        setSnackbarOpen(true);
    };

    return (
        <Box sx={{ display: "flex" }}>
            {/* Top AppBar */}
            <AppBar
                position="fixed"
                sx={{ width: `calc(100% - ${drawerWidth}px)`, ml: `${drawerWidth}px`, backgroundColor: "#1976D2" }}
            >
                <Toolbar>
                    <Typography variant="h6" sx={{ flexGrow: 1 }}>
                        DEVELOPMENT - {localStorage.getItem("userRole") === "ΔΙΑΧΕΙΡΙΣΤΗΣ" ? ADMIN_DASHBOARD_TITLE : USER_DASHBOARD_TITLE}
                    </Typography>
                    {/* Show current user's email */}
                    <Typography variant="body1" sx={{ mr: 1 }}>
                        {userEmail}
                    </Typography>
                    {/* Account menu icon */}
                    <IconButton size="large" edge="end" onClick={handleMenu} color="inherit">
                        <AccountCircle />
                    </IconButton>
                    {/* Account menu items */}
                    <Menu
                        anchorEl={anchorEl}
                        open={Boolean(anchorEl)}
                        onClose={handleCloseMenu}
                        anchorOrigin={{ vertical: "top", horizontal: "right" }}
                    >
                        {/* "Change Password" menu item */}
                        <MenuItem onClick={handleOpenChangePassword}>Αλλαγή Κωδικού</MenuItem>
                        {/* Existing "Logout" menu item */}
                        <MenuItem onClick={handleLogout}>Αποσύνδεση</MenuItem>
                    </Menu>
                </Toolbar>
            </AppBar>

            {/* Left-Sidebar Drawer */}
            <Drawer
                sx={{
                    width: drawerWidth,
                    flexShrink: 0,
                    "& .MuiDrawer-paper": { width: drawerWidth, boxSizing: "border-box" },
                }}
                variant="permanent"
                anchor="left"
            >
                {/* DEVELOPMENT Logo at the Top Left */}
                <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", height: "125px"}}>
                    <img src={developmentLogo} alt="Development Logo" style={{ width: "70%" }} />
                </Box>

                <Divider />
                <List>
                    {/* Home Page (Accessible to all users) */}
                    <ListItem component={Link} to="/dashboard/home" sx={{ cursor: "pointer" }}>
                        <ListItemIcon><HomeIcon sx={{ color: "black" }} /></ListItemIcon>
                        <ListItemText primary="Αρχική Σελίδα" sx={{ color: "black" }} />
                    </ListItem>
                    <Divider />
                    {/* Manage User (Only for admins) */}
                    {hasPrivilege(PRIVILEGES.ADMIN_PRIVILEGE) && (
                        <>
                            <ListItem component={Link} to="/dashboard/manage-users" sx={{ cursor: "pointer" }}>
                                <ListItemIcon>
                                    <SupervisedUserCircleIcon sx={{ color: "black" }} />
                                </ListItemIcon>
                                <ListItemText primary="Διαχείριση Χρηστών" sx={{ color: "black" }} />
                            </ListItem>
                            <Divider />
                        </>
                    )}
                    {/* Demand Forecasting (Only if below privilege exists) */}
                    {hasPrivilege(PRIVILEGES.DEMAND_FORECASTING) && (
                        <>
                            <ListItem component={Link} to="/dashboard/demand-forecasting" sx={{ cursor: "pointer" }}>
                                <ListItemIcon><AssessmentIcon sx={{ color: "black" }} /></ListItemIcon>
                                <ListItemText primary="Πρόβλεψη Ζήτησης" sx={{ color: "black" }} />
                            </ListItem>
                            <Divider />
                        </>
                    )}
                    {/* Inventory Optimization */}
                    {hasPrivilege(PRIVILEGES.INVENTORY_OPTIMIZATION) && (
                        <>
                            <ListItem component={Link} to="/dashboard/inventory-optimization" sx={{ cursor: "pointer" }}>
                                <ListItemIcon><InventoryIcon sx={{ color: "black" }} /></ListItemIcon>
                                <ListItemText primary="Βελτιστοποίηση Αποθεμάτων" sx={{ color: "black" }} />
                            </ListItem>
                            <Divider />
                        </>
                    )}
                    {/* Routing (Only if below privilege exists) */}
                    {hasPrivilege(PRIVILEGES.ROUTING) && (
                        <>
                            <ListItem component={Link} to="/dashboard/distribution-optimization" sx={{ cursor: "pointer" }}>
                                <ListItemIcon><DirectionsIcon sx={{ color: "black" }} /></ListItemIcon>
                                <ListItemText primary="Βελτιστοποίηση Δρομολόγησης Οχημάτων" sx={{ color: "black" }} />
                            </ListItem>
                            <Divider />
                        </>
                    )}
                </List>
            </Drawer>

            {/* Main content area */}
            <Box component="main" sx={{ flexGrow: 1, p: 3, position: "relative" }}>
                {/* The empty Toolbar ensures content is below the AppBar */}
                <Toolbar />
                {/* Nested routes will render here */}
                <Outlet />
            </Box>

            {/* SNACKBAR NOTIFICATION for success/error messages */}
            <SnackbarNotification
                open={snackbarOpen}
                onClose={() => setSnackbarOpen(false)}
                message={snackbarMessage}
                severity={snackbarSeverity}
            />

            {/* CHANGE PASSWORD MODAL */}
            <ChangePasswordModal
                open={changePasswordOpen}
                onClose={handleCloseChangePassword}
                userEmail={userEmail}
                onResult={handleChangePasswordResult}  // Let the parent show the snackbar
            />
        </Box>
    );
}

export default Dashboard;
