import React, { useState } from "react";
import {
    Box,
    Modal,
    Typography,
    TextField,
    Button,
    IconButton,
    InputAdornment
} from "@mui/material";
import { Visibility, VisibilityOff, Close } from "@mui/icons-material";
import { changePassword } from "../../services/userService";

const ChangePasswordModal = ({ open, onClose, userEmail, onResult }) => {
    const [oldPassword, setOldPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmNewPassword, setConfirmNewPassword] = useState("");

    const [showOldPassword, setShowOldPassword] = useState(false);
    const [showNewPassword, setShowNewPassword] = useState(false);
    const [showConfirmNewPassword, setShowConfirmNewPassword] = useState(false);

    const handleToggleOldPassword = () => setShowOldPassword((prev) => !prev);
    const handleToggleNewPassword = () => setShowNewPassword((prev) => !prev);
    const handleToggleConfirmNewPassword = () => setShowConfirmNewPassword((prev) => !prev);

    const handleCloseModal = () => {
        setOldPassword("");
        setNewPassword("");
        setConfirmNewPassword("");
        onClose();
    };

    const handleSubmit = async () => {
        if (!oldPassword || !newPassword || !confirmNewPassword) {
            onResult(false, "Παρακαλώ συμπληρώστε όλα τα πεδία.");
            return;
        }
        if (newPassword !== confirmNewPassword) {
            onResult(false, "Ο νέος κωδικός και η επιβεβαίωση δεν ταιριάζουν.");
            return;
        }
        try {
            await changePassword({
                email: userEmail,
                old_password: oldPassword,
                new_password: newPassword,
            });
            onResult(true, "Ο κωδικός πρόσβασης άλλαξε επιτυχώς!");
            handleCloseModal();
        } catch (error) {
            console.error("Error changing password:", error);
            onResult(false, "Αποτυχία αλλαγής κωδικού. Ελέγξτε τα στοιχεία και δοκιμάστε ξανά.");
        }
    };

    return (
        <Modal open={open} onClose={handleCloseModal}>
            <Box
                sx={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                    width: 380,
                    bgcolor: "background.paper",
                    p: 3,
                    borderRadius: 2,
                }}
            >
                {/* “X” icon to close */}
                <IconButton
                    onClick={handleCloseModal}
                    sx={{ position: "absolute", top: 8, right: 8 }}
                >
                    <Close />
                </IconButton>

                <Typography variant="h6" gutterBottom>
                    Αλλαγή Κωδικού
                </Typography>

                {/* Old Password */}
                <TextField
                    label="Παλιός Κωδικός"
                    type={showOldPassword ? "text" : "password"}
                    value={oldPassword}
                    onChange={(e) => setOldPassword(e.target.value)}
                    fullWidth
                    sx={{ mb: 2 }}
                    InputProps={{
                        endAdornment: (
                            <InputAdornment position="end">
                                <IconButton onClick={handleToggleOldPassword} edge="end">
                                    {showOldPassword ? <VisibilityOff /> : <Visibility />}
                                </IconButton>
                            </InputAdornment>
                        )
                    }}
                />

                {/* New Password */}
                <TextField
                    label="Νέος Κωδικός"
                    type={showNewPassword ? "text" : "password"}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    fullWidth
                    sx={{ mb: 2 }}
                    InputProps={{
                        endAdornment: (
                            <InputAdornment position="end">
                                <IconButton onClick={handleToggleNewPassword} edge="end">
                                    {showNewPassword ? <VisibilityOff /> : <Visibility />}
                                </IconButton>
                            </InputAdornment>
                        )
                    }}
                />

                {/* Confirm New Password */}
                <TextField
                    label="Επιβεβαίωση Νέου Κωδικού"
                    type={showConfirmNewPassword ? "text" : "password"}
                    value={confirmNewPassword}
                    onChange={(e) => setConfirmNewPassword(e.target.value)}
                    fullWidth
                    sx={{ mb: 2 }}
                    InputProps={{
                        endAdornment: (
                            <InputAdornment position="end">
                                <IconButton onClick={handleToggleConfirmNewPassword} edge="end">
                                    {showConfirmNewPassword ? <VisibilityOff /> : <Visibility />}
                                </IconButton>
                            </InputAdornment>
                        )
                    }}
                />

                <Box sx={{ display: "flex", gap: 2, mt: 2 }}>
                    <Button variant="contained" onClick={handleSubmit}>
                        ΑΛΛΑΓΗ
                    </Button>
                    <Button variant="outlined" onClick={handleCloseModal}>
                        ΑΚΥΡΩΣΗ
                    </Button>
                </Box>
            </Box>
        </Modal>
    );
};

export default ChangePasswordModal;
