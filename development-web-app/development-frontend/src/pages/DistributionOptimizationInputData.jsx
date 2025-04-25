import React, { useEffect, useState } from "react";
import {
    Box,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography
} from "@mui/material";
import Loader from "../components/Loader";
import SnackbarNotification from "../components/SnackbarNotification";
import { FAILED_LOAD_INPUT_DATA_EL, SUCCESS_LOAD_INPUT_DATA_EL } from "../utils/constants";

/**
 * Component to display input data used for distribution optimization.
 */
const DistributionOptimizationInputData = () => {
    const [inputData, setInputData] = useState(() => {
        const savedData = sessionStorage.getItem("optimizationInputData");
        return savedData ? JSON.parse(savedData) : null;
    });
    const [loading, setLoading] = useState(true);
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState("");
    const [snackbarSeverity, setSnackbarSeverity] = useState("success");

    useEffect(() => {
        setTimeout(() => {
            if (inputData) {
                setSnackbarMessage(SUCCESS_LOAD_INPUT_DATA_EL);
                setSnackbarSeverity("success");
            } else {
                setSnackbarMessage(FAILED_LOAD_INPUT_DATA_EL);
                setSnackbarSeverity("error");
            }
            setSnackbarOpen(true);
            setLoading(false);
        }, 500);
    }, [inputData]);

    return (
        <Box sx={{ width: "100%", p: 1 }}>
            <Typography variant="h5" sx={{ mb: 2 }}>
                Αποτέλεσμα Υπολογισμού Βέλτιστης Διανομής
            </Typography>

            {loading ? (
                <Loader open={loading} />
            ) : inputData ? (
                <TableContainer component={Paper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                {/* Index column with a right border separator */}
                                <TableCell sx={{ fontWeight: "bold", borderRight: "1px solid rgba(0, 0, 0, 0.2)", pr: 2 }}>
                                    <strong>Α/Α</strong>
                                </TableCell>
                                <TableCell sx={{ fontWeight: "bold" }}>ID Οχήματος</TableCell>
                                <TableCell sx={{ fontWeight: "bold" }}>Τοποθεσία έναρξης</TableCell>
                                <TableCell sx={{ fontWeight: "bold" }}>Τοποθεσία προορισμού</TableCell>
                                <TableCell sx={{ fontWeight: "bold" }}>Αρ. Προϊόντων</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {inputData.routes && inputData.routes.map((route, idx) => (
                                <TableRow key={idx}>
                                    {/* Index column value; using idx+1 */}
                                    <TableCell sx={{ borderRight: "1px solid rgba(0, 0, 0, 0.2)", pr: 2 }}>
                                        <strong>{idx + 1}</strong>
                                    </TableCell>
                                    <TableCell>{route.vehicle_id}</TableCell>
                                    <TableCell>{route.start_location_name}</TableCell>
                                    <TableCell>{route.destination_location_name}</TableCell>
                                    <TableCell>{route.units}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            ) : (
                <Typography variant="body1" sx={{ mt: 3 }}>
                    {FAILED_LOAD_INPUT_DATA_EL}
                </Typography>
            )}

            <SnackbarNotification
                open={snackbarOpen}
                onClose={() => setSnackbarOpen(false)}
                message={snackbarMessage}
                severity={snackbarSeverity}
            />
        </Box>
    );
};

export default DistributionOptimizationInputData;
