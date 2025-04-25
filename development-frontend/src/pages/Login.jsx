import * as React from "react";
import { useNavigate } from "react-router-dom";
import Button from "@mui/material/Button";
import CssBaseline from "@mui/material/CssBaseline";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { login } from "../services/authService.js";
import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import Tooltip from "@mui/material/Tooltip";
import {Checkbox, FormControlLabel} from "@mui/material";

/**
 * Component to display copyright information.
 */
function Copyright(props) {
    return (
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 2 }}>
            {"Copyright © "}
            DOTSOFT SA {" "}
            {new Date().getFullYear()}
        </Typography>
    );
}

// Default MUI theme
const defaultTheme = createTheme();

// Alert component for snackbars
const Alert = React.forwardRef(function Alert(props, ref) {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export default function Login() {
    const navigate = useNavigate();
    const [email, setEmail] = React.useState("");
    const [password, setPassword] = React.useState("");
    const [showPassword, setShowPassword] = React.useState(false);
    const [error, setError] = React.useState("");
    const [loading, setLoading] = React.useState(false);
    const [snackbarOpen, setSnackbarOpen] = React.useState(false);
    const [snackbarMessage, setSnackbarMessage] = React.useState("");
    const [snackbarSeverity, setSnackbarSeverity] = React.useState("success");

    /**
     * Handles form submission for login.
     */
    const handleSubmit = async (event) => {
        setLoading(true); // Loading while authorizing the token
        event.preventDefault(); // Prevent page reload on form submit

        const data = new FormData(event.currentTarget); // Get form data
        try {
            // Call login API
            await login(data.get("email"), data.get("password"));
            navigate("/dashboard/home"); // Redirect to dashboard after successful login
        } catch (err) {
            setError(err.error || "Αποτυχία σύνδεσης. Ελέγξτε τα στοιχεία σας."); // Set error message
            setSnackbarMessage("Αποτυχία σύνδεσης. Παρακαλώ προσπαθήστε ξανά.");
            setSnackbarSeverity("error");
            setSnackbarOpen(true);
            setLoading(false); // Stop loading
        }
    };

    /**
     * Toggles password visibility.
     */
    const togglePasswordVisibility = () => {
        setShowPassword((prev) => !prev);
    };

    /**
     * Handles closing of the snackbar.
     */
    const handleSnackbarClose = (event, reason) => {
        if (reason === "clickaway") {
            return;
        }
        setSnackbarOpen(false);
    };

    return (
        <ThemeProvider theme={defaultTheme}>
            <CssBaseline />

            {/* Main horizontal container with left logos and right login form */}
            <Box
                sx={{
                    display: "flex",
                    flexDirection: "row",
                    justifyContent: "center",
                    alignItems: "center",
                    minHeight: "90vh",
                    px: 2,
                }}
            >
                {/* Left side: Logos column */}
                <Box
                    sx={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        width: "45%",
                        mr: 15,
                    }}
                >
                    <Box>
                        {/* Title and description */}
                        <Box sx={{ textAlign: "center", width: "100%", maxWidth: "1000px", mx: "auto", mb: 5, mt: 10} }>
                            <Typography variant="h3" fontWeight="bold" gutterBottom>
                                DEVELOPMENT
                            </Typography>
                            <Typography variant="h4" sx={{fontSize: "1.9rem"}}>
                                <span style={{whiteSpace: "nowrap"}}>
                                Πλατφόρμα πρόβλεψης της ζήτησης, βελτιστοποίησης <br/>
                                    των αποθεμάτων και της δρομολόγησης οχημάτων
                                </span>
                            </Typography>
                        </Box>
                        {/* EU logo & Project Code */}
                        <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                            <img
                                src="src/assets/visual_id_ESPA.jpg"
                                alt="ESPA EU Funding"
                                style={{ width: "75%", marginTop: "110px", marginBottom: "10px" }}
                            />
                            <Typography
                                sx={{
                                    alignSelf: "flex-start",
                                    width: "75%", // match image width for alignment
                                    marginLeft: "auto",
                                    marginRight: "auto",
                                }}
                            >
                                Κωδικός Έργου ΚΜΡ6-0078774
                            </Typography>
                        </Box>
                        {/* IMET, DOTSOFT logos */}
                        <Box
                            sx={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                                mt: 5,
                                px: 11,
                                mx: "auto" // centers the whole box horizontally
                            }}
                        >
                            <img
                                src="src/assets/dotsoft_logo.png"
                                alt="DOTSOFT LOGO"
                                style={{ width: "190px" }}
                            />
                            <img
                                src="src/assets/IMETlogoGR.png"
                                alt="IMET LOGO GR"
                                style={{ width: "160px" }}
                            />
                        </Box>
                    </Box>
                </Box>

                {/* Right side: Login form */}
                <Box
                    component="main"
                    sx={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        width: "55%",
                        maxWidth: 500,
                        p: 2,
                        border: "1px solid #ccc",
                        borderRadius: "8px",
                        boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
                        mt: 3,
                        transform: "translateX(40px)"
                    }}
                >
                    <Box
                        component="form"
                        onSubmit={handleSubmit}
                        sx={{ width: "100%" }}
                    >
                        {/* Development Logo */}
                        <Box sx={{ display: "flex", justifyContent: "center", mb: -5, mt: -2 }}>
                            <img
                                src="src/assets/DEVELOPMENT_logo.png"
                                alt="Development Logo"
                                style={{ width: "300px", maxWidth: "100%" }}
                            />
                        </Box>
                        {/* Email input field */}
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="email"
                            label="Διεύθυνση Email"
                            name="email"
                            autoComplete="email"
                            autoFocus
                            value={email}
                            error={!!error}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                        {/* Password input field with visibility toggle */}
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="password"
                            label="Κωδικός πρόσβασης"
                            type={showPassword ? "text" : "password"}
                            id="password"
                            autoComplete="current-password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            InputProps={{
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <IconButton onClick={togglePasswordVisibility} edge="end">
                                            {showPassword ? <VisibilityOff /> : <Visibility />}
                                        </IconButton>
                                    </InputAdornment>
                                ),
                            }}
                        />
                        {/* Display error message if exists */}
                        {error && (
                            <Typography color="error" variant="body2">
                                {error}
                            </Typography>
                        )}
                        {/* Submit button */}
                        <Box sx={{ display: "flex", justifyContent: "center", mt: 3, mb: 2 }}>
                            <Button type="submit" variant="contained" sx={{ width: "50%" }} disabled={loading}>
                                ΣΥΝΔΕΣΗ
                            </Button>
                        </Box>
                        <FormControlLabel
                            control={
                                <Checkbox
                                    checked={true}
                                    disabled
                                    sx={{ ml: "50px" }}
                                />
                            }
                            label={
                                <Typography variant="body2" sx={{fontSize: "0.95rem"}}>
                                    Με τη σύνδεσή σας, αποδέχεστε τους{" "}
                                    <a
                                        href="/terms-of-use"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        style={{color: "#1976D2", textDecoration: "underline"}}
                                    >
                                        Όρους Χρήσης
                                    </a>
                                </Typography>
                            }
                        />
                        {/* Forgot password tooltip text */}
                        <Box sx={{ display: "flex", justifyContent: "center", mb: 2 }}>
                            <Tooltip
                                title="Πατήστε εδώ για να επικοινωνήστε με τον διαχειριστή του συστήματος"
                                arrow
                                componentsProps={{
                                    tooltip: {
                                        sx: {
                                            fontSize: "0.9rem",
                                            width: "200px"
                                        },
                                    },
                                }}
                            >
                                <Typography
                                    variant="body2"
                                    component="a"
                                    href="mailto:info@dotsoft.gr"
                                    sx={{
                                        color: "#1976D2",
                                        cursor: "pointer",
                                        textDecoration: "underline",
                                        fontSize: "0.95rem",
                                    }}
                                >
                                    Ξεχάσατε τον κωδικό σας;
                                </Typography>
                            </Tooltip>
                        </Box>
                    </Box>
                </Box>
            </Box>
            <Copyright />
            <Snackbar
                open={snackbarOpen}
                autoHideDuration={6000}
                onClose={handleSnackbarClose}
            >
                <Alert onClose={handleSnackbarClose} severity={snackbarSeverity}>
                    {snackbarMessage}
                </Alert>
            </Snackbar>
        </ThemeProvider>
    );
}
