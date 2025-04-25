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
import { Close, Visibility, VisibilityOff } from "@mui/icons-material";
import { changePasswordByAdmin } from "../../services/userService";

const ChangeUserPasswordByAdminModal = ({ open, onClose, user, onSuccess, onError }) => {
    const [newPassword, setNewPassword] = useState("");
    const [code, setCode] = useState("");
    const [showNewPassword, setShowNewPassword] = useState(false);
    const [showCode, setShowCode] = useState(false);
    const [loading, setLoading] = useState(false);

    const toggleShowNewPassword = () => {
        setShowNewPassword((prev) => !prev);
    };

    const toggleShowCode = () => {
        setShowCode((prev) => !prev);
    };

    const handleSave = async () => {
        setLoading(true);
        try {
            const adminRole = localStorage.getItem("userRole"); // should be "ΔΙΑΧΕΙΡΙΣΤΗΣ"
            const payload = {
                email: user.email,
                new_password: newPassword,
                role: adminRole,
                code: code
            };
            await changePasswordByAdmin(payload);
            // Call the parent's onSuccess callback to show a success snackbar in ManageUsers
            if (onSuccess) {
                onSuccess("Ο κωδικός αλλάχτηκε επιτυχώς.", "success");
            }
            onClose();
        } catch (error) {
            console.error("Error changing password:", error);
            if (onError) {
                onError("Αποτυχία αλλαγής κωδικού.", "error");
            }
        } finally {
            setLoading(false);
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
                    width: 400,
                    bgcolor: "background.paper",
                    p: 4,
                    borderRadius: 2,
                }}
            >
                <IconButton
                    onClick={onClose}
                    sx={{ position: "absolute", top: 8, right: 8 }}
                >
                    <Close />
                </IconButton>

                <Typography variant="h6" gutterBottom>
                    Αλλαγή Κωδικού Πρόσβασης Χρήστη
                </Typography>

                <TextField
                    label="Email"
                    value={user.email}
                    fullWidth
                    margin="normal"
                    InputProps={{ readOnly: true }}
                />

                <TextField
                    label="Νέος Κωδικός"
                    type={showNewPassword ? "text" : "password"}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    fullWidth
                    margin="normal"
                    InputProps={{
                        endAdornment: (
                            <InputAdornment position="end">
                                <IconButton onClick={toggleShowNewPassword} edge="end">
                                    {showNewPassword ? <VisibilityOff /> : <Visibility />}
                                </IconButton>
                            </InputAdornment>
                        )
                    }}
                />

                <TextField
                    label="Κωδικός Επιβεβαίωσης Διαχειριστή"
                    type={showCode ? "text" : "password"}
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    fullWidth
                    margin="normal"
                    InputProps={{
                        endAdornment: (
                            <InputAdornment position="end">
                                <IconButton onClick={toggleShowCode} edge="end">
                                    {showCode ? <VisibilityOff /> : <Visibility />}
                                </IconButton>
                            </InputAdornment>
                        )
                    }}
                />

                <Box sx={{ mt: 2, display: "flex", gap: 2, justifyContent: "flex-end" }}>
                    <Button variant="contained" onClick={handleSave} disabled={loading}>
                        ΑΠΟΘΗΚΕΥΣΗ
                    </Button>
                    <Button variant="outlined" onClick={onClose} disabled={loading}>
                        ΑΚΥΡΩΣΗ
                    </Button>
                </Box>
            </Box>
        </Modal>
    );
};

export default ChangeUserPasswordByAdminModal;
