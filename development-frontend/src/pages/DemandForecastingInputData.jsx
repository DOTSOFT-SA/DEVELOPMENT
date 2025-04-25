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
import {
    FAILED_LOAD_INPUT_DATA_EL,
    SUCCESS_LOAD_INPUT_DATA_EL
} from "../utils/constants";
import {formatTimestampGreek} from "../utils/shared.js";


/**
 * Component to display input data used for demand forecasting.
 */
const DemandForecastingInputData = () => {
    const [inputData, setInputData] = useState(() => {
        // Preserve data on refresh page
        const savedData = sessionStorage.getItem("inputData");
        return savedData ? JSON.parse(savedData) : null;
    });
    const [loading, setLoading] = useState(true);
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState("");
    const [snackbarSeverity, setSnackbarSeverity] = useState("success");

    useEffect(() => {
        // Simulated API delay for loader effect
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
    }, [inputData]); // Trigger only when inputData changes

    // Mapping for Greek translations with parenthesis
    const greekLabels = {
        order_date: "Ημερομηνία Παραγγελίας (order_date)",
        sku_number: "Αριθμός SKU (sku_number)",
        sku_name: "Όνομα SKU (sku_name)",
        class_display_name: "Κατηγορία SKU (class_display_name)",
        order_item_price_in_main_currency: "Τιμή Παραγγελίας (order_item_price_in_main_currency)",
        order_item_unit_count: "Μονάδες Παραγγελίας (order_item_unit_count)",
        cl_price: "Τιμή Ανταγωνιστή (cl_price)",
        is_weekend: "Είναι Σαββατοκύριακο (is_weekend)",
        is_holiday: "Είναι Αργία (is_holiday)",
        mean_temperature: "Μέση Θερμοκρασία (mean_temperature)",
        rain: "Βροχόπτωση (rain)",
        average_competition_price_external: "Μέση Τιμή Ανταγωνισμού (average_competition_price_external)",
        review_sentiment_score: "Βαθμολογία Συναισθήματος (review_sentiment_score)",
        review_sentiment_timestamp: "Χρόνος Συναισθήματος (review_sentiment_timestamp)",
        trend_value: "Τιμή Τάσης (trend_value)"
    };

    return (
        <Box sx={{ width: "100%", p: 1 }}>
            {/* Title */}
            <Typography variant="h5" sx={{ mb: 2 }}>
                Δεδομένα Εισόδου (Χρησιμοποιήθηκαν στην Πρόβλεψη)
            </Typography>

            {/* Show loader before displaying data */}
            {loading ? (
                <Loader open={loading} />
            ) : inputData ? (
                // ML Input Data Table
                <TableContainer component={Paper} sx={{ width: "100%", overflowX: "auto" }}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell sx={{ fontWeight: "bold" }}>Χαρακτηριστικό</TableCell>
                                <TableCell sx={{ fontWeight: "bold" }}>Τιμή</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {Object.entries(greekLabels).map(([key, label]) => (
                                <TableRow key={key}>
                                    <TableCell>{label}</TableCell>
                                    <TableCell>
                                        {inputData[key] !== undefined
                                            ? // Apply date formatting only for date fields
                                            ["order_date", "review_sentiment_timestamp"].includes(key)
                                                ? formatTimestampGreek(inputData[key])
                                                : typeof inputData[key] === "boolean"
                                                    ? inputData[key] ? "Ναι" : "Όχι"
                                                    : inputData[key]
                                            : "-"} {/* Show dashes if value is missing */}
                                    </TableCell>
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

            {/* Snackbar Notification */}
            <SnackbarNotification
                open={snackbarOpen}
                onClose={() => setSnackbarOpen(false)}
                message={snackbarMessage}
                severity={snackbarSeverity}
            />
        </Box>
    );
};

export default DemandForecastingInputData;
