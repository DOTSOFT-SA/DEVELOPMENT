import React, { useEffect, useState } from "react";
import {
    Box,
    TextField,
    Typography,
    Grid,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    TablePagination,
    IconButton,
    Button
} from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import Tooltip from "@mui/material/Tooltip";
import { format } from "date-fns";
import { el } from "date-fns/locale";
import Loader from "../components/Loader";
import SnackbarNotification from "../components/SnackbarNotification";
import { fetchAllUsers } from "../services/userService";
import {
    FAILED_FETCH_USERS_EL,
    SUCCESS_UPDATE,
    FAILED_UPDATE,
    SUCCESS_CREATE,
    FAILED_CREATE
} from "../utils/constants";
import EditIcon from "@mui/icons-material/Edit";
import VpnKeyIcon from "@mui/icons-material/VpnKey";
import UserEditModal from "./modals/UserEditModal";
import AddUserModal from "./modals/AddUserModal";
import ViewUserErpApiModal from "./modals/ViewUserErpApiModal";
import ChangeUserPasswordByAdminModal from "./modals/ChangeUserPasswordByAdminModal.jsx";

const ManageUsers = () => {
    const [loading, setLoading] = useState(false);
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState("");
    const [snackbarSeverity, setSnackbarSeverity] = useState("success");

    const [users, setUsers] = useState([]);
    const [filteredUsers, setFilteredUsers] = useState([]);
    const [searchTerm, setSearchTerm] = useState("");
    // Pagination states
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    // Admin role check
    const userRole = localStorage.getItem("userRole"); // e.g. "ΔΙΑΧΕΙΡΙΣΤΗΣ"
    // For editing an existing user
    const [selectedUser, setSelectedUser] = useState(null);
    const [editModalOpen, setEditModalOpen] = useState(false);
    // For creating a new user
    const [addModalOpen, setAddModalOpen] = useState(false);
    // For viewing ERP API details
    const [erpApiModalOpen, setErpApiModalOpen] = useState(false);
    const [erpUser, setErpUser] = useState(null);
    // For changing user password by admin
    const [changePasswordModalOpen, setChangePasswordModalOpen] = useState(false);
    const [passwordUser, setPasswordUser] = useState(null);

    /**
     * Opens the UserEditModal with the selected user.
     */
    const handleOpenEditModal = (user) => {
        setSelectedUser(user);
        setEditModalOpen(true);
    };

    /**
     * Closes the UserEditModal.
     */
    const handleCloseEditModal = () => {
        setSelectedUser(null);
        setEditModalOpen(false);
    };

    /**
     * Called after user update success/failure.
     * If success, updates user in local state, shows success. Otherwise, error.
     */
    const handleUserUpdated = (updatedUser, success) => {
        if (success) {
            setUsers((prev) => prev.map((u) => (u.id === updatedUser.id ? updatedUser : u)));
            setFilteredUsers((prev) => prev.map((u) => (u.id === updatedUser.id ? updatedUser : u)));
            setSnackbarMessage(SUCCESS_UPDATE);
            setSnackbarSeverity("success");
        } else {
            setSnackbarMessage(FAILED_UPDATE);
            setSnackbarSeverity("error");
        }
        setSnackbarOpen(true);
    };

    /**
     * Opens the AddUserModal for creating a new user.
     */
    const handleOpenAddModal = () => {
        setAddModalOpen(true);
    };

    /**
     * Closes the AddUserModal.
     */
    const handleCloseAddModal = () => {
        setAddModalOpen(false);
    };

    /**
     * Called after user creation success/failure.
     * If success, re-fetch user list and show success. Otherwise, show error.
     */
    const handleUserCreated = async (success, optionalMessage = null) => {
        if (success) {
            setSnackbarMessage(SUCCESS_CREATE);
            setSnackbarSeverity("success");
        } else {
            setSnackbarMessage(optionalMessage || FAILED_CREATE);
            setSnackbarSeverity("error");
        }
        // Re-fetch to show new user
        try {
            setLoading(true);
            const data = await fetchAllUsers();
            setUsers(data);
            setFilteredUsers(data);
        } catch (error) {
            // console.error("Error re-fetching users after creation:", error);
        } finally {
            setLoading(false);
        }
        setSnackbarOpen(true);
    };

    /**
     * Opens the ERP API modal for a selected user.
     */
    const handleOpenErpApiModal = (user) => {
        setErpUser(user);
        setErpApiModalOpen(true);
    };

    /**
     * Closes the ERP API modal.
     */
    const handleCloseErpApiModal = () => {
        setErpUser(null);
        setErpApiModalOpen(false);
    };

    /**
     * Fetches the users from the backend if the user has admin privileges.
     */
    useEffect(() => {
        if (userRole !== "ΔΙΑΧΕΙΡΙΣΤΗΣ") {
            setSnackbarMessage("Δεν έχετε δικαιώματα πρόσβασης σε αυτήν τη σελίδα.");
            setSnackbarSeverity("error");
            setSnackbarOpen(true);
            return;
        }
        const fetchData = async () => {
            setLoading(true);
            try {
                const data = await fetchAllUsers();
                setUsers(data);
                setFilteredUsers(data);
            } catch (error) {
                console.error("Error fetching users:", error);
                setSnackbarMessage(error.error || FAILED_FETCH_USERS_EL);
                setSnackbarSeverity("error");
                setSnackbarOpen(true);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [userRole]);

    /**
     * Filters the user list by email whenever the search input changes.
     */
    const handleSearchChange = (e) => {
        const value = e.target.value.toLowerCase();
        setSearchTerm(value);

        const filtered = users.filter((user) =>
            user.email?.toLowerCase().includes(value)
        );
        setFilteredUsers(filtered);
        setPage(0);
    };

    /**
     * Pagination handler for page changes.
     */
    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    /**
     * Pagination handler for rows-per-page changes.
     */
    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    // Handler to open the Change Password modal
    const handleOpenChangePasswordModal = (user) => {
        setPasswordUser(user);
        setChangePasswordModalOpen(true);
    };
    const handleCloseChangePasswordModal = () => {
        setPasswordUser(null);
        setChangePasswordModalOpen(false);
    };

    /**
     * Formats date to "dd/MM/yyyy - HH:mm" in Greek, or returns "-" if null.
     */
    const formatGreekDateTime = (dateString) => {
        if (!dateString) return "-";
        const parsed = new Date(dateString);
        return format(parsed, "dd/MM/yyyy - HH:mm", { locale: el });
    };

    return (
        <Box
            sx={{
                p: 3,
                border: "2px solid #ccc",
                borderRadius: "8px",
                boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
                mb: 3
            }}
        >
            {userRole !== "ΔΙΑΧΕΙΡΙΣΤΗΣ" ? (
                <Typography color="error">
                    Δεν έχετε δικαιώματα πρόσβασης σε αυτήν τη σελίδα.
                </Typography>
            ) : (
                <>
                    <Grid container justifyContent="space-between" alignItems="center" sx={{ mt: 2, mb: 2 }}>
                        {/* Search Field */}
                        <Grid item>
                            <TextField
                                label="Αναζήτηση Email"
                                variant="outlined"
                                value={searchTerm}
                                onChange={handleSearchChange}
                                size="small"
                                sx={{ width: "250px" }}
                            />
                        </Grid>
                        {/* Add User Button */}
                        <Grid item>
                            {userRole === "ΔΙΑΧΕΙΡΙΣΤΗΣ" && (
                                <Button variant="contained" onClick={handleOpenAddModal}>
                                    ΔΗΜΙΟΥΡΓΙΑ ΧΡΗΣΤΗ
                                </Button>
                            )}
                        </Grid>
                    </Grid>

                    {/* Table with users */}
                    <Box sx={{ mt: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Λίστα Χρηστών
                        </Typography>
                        <TableContainer component={Paper}>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell><strong>Email</strong></TableCell>
                                        <TableCell><strong>Ρόλος</strong></TableCell>
                                        <TableCell><strong>Λειτουργίες</strong></TableCell>
                                        <TableCell><strong>Ενεργός</strong></TableCell>
                                        <TableCell><strong>Τελευταία Σύνδεση</strong></TableCell>
                                        <TableCell><strong>Ημ/νία Δημιουργίας</strong></TableCell>
                                        <TableCell><strong>Λειτουργίες</strong></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {filteredUsers
                                        .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                                        .map((user) => (
                                            <TableRow key={user.id}>
                                                <TableCell>{user.email}</TableCell>
                                                <TableCell>{user.role}</TableCell>
                                                <TableCell>{user.privilege_names?.join(", ")}</TableCell>
                                                <TableCell>{user.is_active ? "Ναι" : "Όχι"}</TableCell>
                                                <TableCell>{formatGreekDateTime(user.login_at)}</TableCell>
                                                <TableCell>{formatGreekDateTime(user.created_at)}</TableCell>
                                                <TableCell>
                                                    <Box
                                                        sx={{
                                                            display: "flex",
                                                            alignItems: "center",
                                                            whiteSpace: "nowrap" // prevents wrapping
                                                        }}
                                                    >
                                                        {/* Edit icon with hover message */}
                                                        <Tooltip title="Επεξεργασία χρήστη" arrow>
                                                            <IconButton onClick={() => handleOpenEditModal(user)} size="small">
                                                                <EditIcon />
                                                            </IconButton>
                                                        </Tooltip>

                                                        {/* Eye icon with hover message */}
                                                        <Tooltip title="Προβολή στοιχείων χρήστη" arrow>
                                                            <IconButton onClick={() => handleOpenErpApiModal(user)} size="small">
                                                                <VisibilityIcon fontSize="small" />
                                                            </IconButton>
                                                        </Tooltip>

                                                        {/* Key icon with hover message */}
                                                        <Tooltip title="Αλλαγή κωδικού πρόσβασης χρήστη" arrow>
                                                            <IconButton onClick={() => handleOpenChangePasswordModal(user)} size="small">
                                                                <VpnKeyIcon fontSize="small" />
                                                            </IconButton>
                                                        </Tooltip>
                                                    </Box>
                                                </TableCell>

                                            </TableRow>
                                        ))
                                    }
                                </TableBody>
                            </Table>
                            <TablePagination
                                rowsPerPageOptions={[5, 10, 25]}
                                component="div"
                                count={filteredUsers.length}
                                rowsPerPage={rowsPerPage}
                                page={page}
                                onPageChange={handleChangePage}
                                onRowsPerPageChange={handleChangeRowsPerPage}
                            />
                        </TableContainer>
                    </Box>
                </>
            )}

            <Loader open={loading} />
            <SnackbarNotification
                open={snackbarOpen}
                onClose={() => setSnackbarOpen(false)}
                message={snackbarMessage}
                severity={snackbarSeverity}
            />

            {/* Modal for editing an existing user */}
            {editModalOpen && selectedUser && (
                <UserEditModal
                    open={editModalOpen}
                    onClose={handleCloseEditModal}
                    user={selectedUser}
                    onUserUpdated={(updatedUser, success) => {
                        handleUserUpdated(updatedUser, success);
                        handleCloseEditModal();
                    }}
                />
            )}

            {/* Modal for creating a new user */}
            {addModalOpen && (
                <AddUserModal
                    open={addModalOpen}
                    onClose={handleCloseAddModal}
                    onUserCreated={handleUserCreated}
                />
            )}

            {/* Modal for viewing ERP API details */}
            {erpApiModalOpen && erpUser && (
                <ViewUserErpApiModal
                    open={erpApiModalOpen}
                    onClose={handleCloseErpApiModal}
                    user={erpUser}
                />
            )}

            {/* Modal for changing user password by admin */}
            {changePasswordModalOpen && passwordUser && (
                <ChangeUserPasswordByAdminModal
                    open={changePasswordModalOpen}
                    onClose={handleCloseChangePasswordModal}
                    user={passwordUser}
                    onSuccess={(message, severity) => {
                        setSnackbarMessage(message);
                        setSnackbarSeverity(severity);
                        setSnackbarOpen(true);
                    }}
                    onError={(message, severity) => {
                        setSnackbarMessage(message);
                        setSnackbarSeverity(severity);
                        setSnackbarOpen(true);
                    }}
                />
            )}

        </Box>
    );
};

export default ManageUsers;
