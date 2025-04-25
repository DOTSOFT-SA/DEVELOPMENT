import React, { useState, useEffect } from "react";
import {
    Box,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    TextField,
    Typography,
    Grid,
    TablePagination
} from "@mui/material";
import { run_inference, fetchAllSkuOrderQuantityPredictions } from "../services/demandForecastingService";
import Loader from "../components/Loader";
import SnackbarNotification from "../components/SnackbarNotification";
import {
    SUCCESS_DEMAND_FORECASTING_EL,
    FAILED_DEMAND_FORECASTING_EL,
    FAILED_FETCH_INPUT_DATA_EL,
    FAILED_OPEN_NEW_TAB_EL
} from "../utils/constants.js";
import {formatTimestampGreek, formatWeekNumberGreek} from "../utils/shared.js";
import Tooltip from "@mui/material/Tooltip";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";

const DemandForecasting = () => {
    const [skuNumber, setSkuNumber] = useState("");
    const [prediction, setPrediction] = useState({  // Initialized them as empty
        sku_number: "-",
        week_number: "-",
        year_of_the_week: "",
        predicted_value: "-",
        mape: "-"
    });
    const [inputData, setInputData] = useState(null);
    const [isInputDataAvailable, setIsInputDataAvailable] = useState(false);
    const [loading, setLoading] = useState(false); // Unified loading state
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState("");
    const [snackbarSeverity, setSnackbarSeverity] = useState("success");
    const [predictions, setPredictions] = useState([]);
    const [filteredPredictions, setFilteredPredictions] = useState([]);
    const [searchTerm, setSearchTerm] = useState("");
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);

    // If a field has an invalid (non-numeric) value, it will be set to `true`
    const [invalidFields, setInvalidFields] = useState({
        sku_number: false
    });

    useEffect(() => {
        const fetchAllPreds = async () => {
            try {
                setLoading(true);
                const userId = localStorage.getItem("userId");
                const results = await fetchAllSkuOrderQuantityPredictions(userId);
                // Sort results by `updated_at` in descending order (most recent first)
                const sortedResults = results.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
                setPredictions(sortedResults);
                setFilteredPredictions(sortedResults);
            } catch (err) {
                console.error("Error fetching all predictions:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchAllPreds();
    }, []);

    const handleSearchChange = (e) => {
        const value = e.target.value;
        setSearchTerm(value);
        const filtered = predictions.filter(pred => String(pred.sku_number).includes(value));
        setFilteredPredictions(filtered);
        setPage(0);
    };

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    // Function to handle the prediction request
    const handlePredict = async () => {
        if (!skuNumber) return;
        setLoading(true); // Show loader
        try {
            // Initialization
            const userId = localStorage.getItem("userId");
            const response = await run_inference(skuNumber, userId);
            // Set the prediction output table values
            setPrediction(response.sku_order_quantity_prediction);
            setInputData(response.merged_sku_metric);
            setIsInputDataAvailable(true);
            // Show success snackbar
            setSnackbarMessage(SUCCESS_DEMAND_FORECASTING_EL);
            setSnackbarSeverity("success");
            setSnackbarOpen(true);
            // Refresh the "Ιστορικό Προβλέψεων" table
            const newResults = await fetchAllSkuOrderQuantityPredictions(userId);
            const sorted = newResults.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
            setPredictions(sorted);
            setFilteredPredictions(sorted);
        } catch (error) {
            console.error("Error fetching prediction:", error);
            // Show error snackbar
            setSnackbarMessage(FAILED_DEMAND_FORECASTING_EL);
            setSnackbarSeverity("error");
            setSnackbarOpen(true);
        } finally {
            setLoading(false); // Hide loader
        }
    };

    // Function to navigate to input data page in a new tab
    const handleViewInputData = () => {
        if (!isInputDataAvailable) {
            setSnackbarMessage(FAILED_FETCH_INPUT_DATA_EL);
            setSnackbarSeverity("error");
            setSnackbarOpen(true);
            return;
        }
        // Store SKU and input data in sessionStorage (to ensure cleanup after closing tab)
        sessionStorage.setItem("selectedSku", skuNumber);
        sessionStorage.setItem("inputData", JSON.stringify(inputData));
        // Open in a new tab
        const newTab = window.open(`/dashboard/demand-forecasting-input-data`, "_blank");
        // Check if the tab opened successfully
        if (!newTab) {
            setSnackbarMessage(FAILED_OPEN_NEW_TAB_EL);
            setSnackbarSeverity("error");
            setSnackbarOpen(true);
        }
    };

    return (
        <Box sx={{
            p: 3,
            border: "2px solid #ccc",
            borderRadius: "8px",
            boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
            mb: 3
        }}>
            {/* Title */}
            <Typography variant="h5" gutterBottom>
                Πρόβλεψη Ζήτησης
            </Typography>

            <Typography
                sx={{
                    mt: 1,
                    mb: 2,
                    fontSize: '1.17rem',
                    borderBottom: "1px solid rgba(0, 0, 0, 0.2)",
                    display: "inline-block",
                    pb: 0
                }}
            >
                Εισάγετε τον αριθμό SKU για να δείτε την πρόβλεψη ζήτησής του (σε ορίζοντα εβδομάδας):
            </Typography>

            {/* SKU Input and Predict Button */}
            <Grid container spacing={2} alignItems="center">
                <Grid item>
                    <TextField
                        label="Εισαγάγετε Αριθμό SKU"
                        variant="outlined"
                        value={skuNumber}
                        onChange={(e) => {
                            const val = e.target.value;
                            setSkuNumber(val);
                            setInvalidFields({
                                ...invalidFields,
                                sku_number: val && !/^\d+(\.\d+)?$/.test(val),
                            });
                        }}
                        required
                        size="small"
                        sx={{ width: "250px" }}
                        error={Boolean(invalidFields.sku_number)}
                    />
                </Grid>
                <Grid item>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handlePredict}
                        disabled={loading}
                    >
                        ΠΡΟΒΛΕΨΗ
                    </Button>
                </Grid>
            </Grid>

            {/* Prediction Output Table */}
            <Typography variant="h6" sx={{ mt: 3 }}>
                Αποτέλεσμα Πρόβλεψης SKU
            </Typography>
            <TableContainer component={Paper} sx={{ width: "70%", mt: 1 }}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell><strong>Αριθμός SKU</strong></TableCell>
                            <TableCell><strong>Ονομασία SKU</strong></TableCell>
                            <TableCell><strong>Χρονικό Διάστημα Πρόβλεψης</strong></TableCell>
                            <TableCell><strong>Προβλεπόμενη Ζήτηση</strong></TableCell>
                            <TableCell>
                                <strong>MAPE (%)</strong>
                                <Tooltip
                                    title={
                                        <Typography variant="body1" sx={{ fontSize: '0.85rem', lineHeight: 1.5 }}>
                                            Το MAPE δείχνει πόσο απέχει, κατά μέσο όρο, η πρόβλεψή μας από την πραγματική ζήτηση,
                                            εκφρασμένο ως ποσοστό. Για παράδειγμα, MAPE 10% σημαίνει ότι πέφτουμε έξω περίπου 10%
                                            από την πραγματική τιμή. Μικρότερο ποσοστό = πιο ακριβής πρόβλεψη.
                                        </Typography>
                                    }
                                    arrow
                                    placement="top"
                                >
                                    <InfoOutlinedIcon
                                        sx={{
                                            fontSize: 20,
                                            ml: 0.5,
                                            verticalAlign: 'middle',
                                            color: '#1976D2',
                                            cursor: 'pointer'
                                        }}
                                    />
                                </Tooltip>
                            </TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        <TableRow>
                            <TableCell>{prediction.sku_number}</TableCell>
                            <TableCell>{inputData?.sku_name || "-"}</TableCell>
                            <TableCell>{`${formatWeekNumberGreek(prediction.week_number)} ${prediction.year_of_the_week}`}</TableCell>
                            <TableCell>
                                {prediction?.predicted_value && !isNaN(Number(prediction.predicted_value))
                                    ? Math.ceil(Number(prediction.predicted_value)) + " τμχ"
                                    : "-"}
                            </TableCell>
                            <TableCell>
                                {prediction?.mape && !isNaN(Number(prediction.mape))
                                    ? Number(prediction.mape * 100).toFixed(2) + " %"
                                    : "-"}
                            </TableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </TableContainer>

            {/* View Input Data Button */}
            <Grid container spacing={2} alignItems="center" sx={{ mt: 2 }}>
                <Grid item>
                    <Button
                        variant="contained"
                        onClick={handleViewInputData}
                        disabled={!isInputDataAvailable || loading}
                        sx={{
                            bgcolor: !isInputDataAvailable ? "#bdbdbd" : "primary.main",
                            color: "white",
                            "&:hover": {
                                bgcolor: !isInputDataAvailable ? "#bdbdbd" : "primary.dark",  // Darker shade when hovered
                            },
                        }}
                    >
                        ΠΡΟΒΟΛΗ ΔΕΔΟΜΕΝΩΝ ΜΟΝΤΕΛΟΥ ΠΡΟΒΛΕΨΗΣ
                    </Button>
                </Grid>

            </Grid>
            {/* Spacer element for space before <hr /> */}
            <div style={{ height: '20px' }}></div>
            <hr/>
            <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                    Ιστορικό Προβλέψεων
                </Typography>
                <TextField
                    label="Αναζήτηση SKU"
                    variant="outlined"
                    value={searchTerm}
                    onChange={handleSearchChange}
                    size="small"
                    sx={{ width: "150px", mb: 2 }}
                />
                <TableContainer component={Paper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell><strong>Αριθμός SKU</strong></TableCell>
                                <TableCell><strong>Χρονικό Διάστημα Πρόβλεψης</strong></TableCell>
                                <TableCell><strong>Προβλεπόμενη Ζήτηση</strong></TableCell>
                                <TableCell><strong>MAPE (%)</strong></TableCell>
                                <TableCell><strong>Τελευταία Πρόβλεψη</strong></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {filteredPredictions
                                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                                .map((item) => (
                                    <TableRow key={item.id}>
                                        <TableCell>{item.sku_number}</TableCell>
                                        <TableCell> {`${formatWeekNumberGreek(item.week_number)} ${item.year_of_the_week}`} </TableCell>
                                        <TableCell>{Math.ceil(Number(item.predicted_value)) + " τμχ"}</TableCell>
                                        <TableCell>{Number(item.mape * 100).toFixed(2) + " %" }
                                        </TableCell>
                                        <TableCell>{formatTimestampGreek(item.updated_at)}</TableCell>
                                    </TableRow>
                                ))}
                        </TableBody>
                    </Table>
                    <TablePagination
                        rowsPerPageOptions={[5, 10, 25]}
                        component="div"
                        count={filteredPredictions.length}
                        rowsPerPage={rowsPerPage}
                        page={page}
                        onPageChange={handleChangePage}
                        onRowsPerPageChange={handleChangeRowsPerPage}
                    />
                </TableContainer>
            </Box>

            {/* Loader Component */}
            <Loader open={loading} />

            {/* Snackbar Notification Component */}
            <SnackbarNotification
                open={snackbarOpen}
                onClose={() => setSnackbarOpen(false)}
                message={snackbarMessage}
                severity={snackbarSeverity}
            />

        </Box>
    );
};

export default DemandForecasting;
