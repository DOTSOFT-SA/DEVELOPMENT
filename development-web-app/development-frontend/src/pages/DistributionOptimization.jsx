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
    Typography,
    Grid,
    TablePagination,
    TextField
} from "@mui/material";
import Loader from "../components/Loader";
import SnackbarNotification from "../components/SnackbarNotification";
import { runDistributionOptimization, fetchAllDistributionOptimizations } from "../services/distributionOptimizationService";
import { SUCCESS_DISTRIBUTION_OPTIMIZATION_EL, FAILED_DISTRIBUTION_OPTIMIZATION_EL, FAILED_FETCH_DISTRIBUTION_OPTIMIZATIONS_EL } from "../utils/constants";
import {formatTimestampGreek} from "../utils/shared.js";
import Tooltip from "@mui/material/Tooltip";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";

const DistributionOptimization = () => {
    const [userId, setUserId] = useState(localStorage.getItem("userId"));
    const [optimizationData, setOptimizationData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState("");
    const [snackbarSeverity, setSnackbarSeverity] = useState("success");
    const [searchTerm, setSearchTerm] = useState("");
    const [filteredOptimizations, setFilteredOptimizations] = useState([]);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [sortDirection, setSortDirection] = useState('asc');
    const [sortBy, setSortBy] = useState('updated_at');

    const handleSort = () => {
        const newSortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        setSortDirection(newSortDirection);
    };

    // Function to handle optimization request
    const handleOptimization = async () => {
        setLoading(true);
        try {
            const response = await runDistributionOptimization(userId);
            setOptimizationData(response);

            // Store the optimization input data in sessionStorage
            sessionStorage.setItem("optimizationInputData", JSON.stringify(response));

            // Open a new tab with the input data page
            const newTab = window.open("/dashboard/distribution-optimization-input-data", "_blank");
            if (!newTab) {
                setSnackbarMessage("Δεν ήταν δυνατή η ανοίγμα του νέου παραθύρου.");
                setSnackbarSeverity("error");
                setSnackbarOpen(true);
            }

            // Fetch all optimizations again to refresh the table data
            const freshOptimizations = await fetchAllDistributionOptimizations(userId);
            setOptimizationData(freshOptimizations);
            setFilteredOptimizations(freshOptimizations); // Update the filtered optimizations

            setSnackbarMessage(SUCCESS_DISTRIBUTION_OPTIMIZATION_EL);
            setSnackbarSeverity("success");
        } catch (error) {
            setSnackbarMessage(FAILED_DISTRIBUTION_OPTIMIZATION_EL);
            setSnackbarSeverity("error");
        } finally {
            setSnackbarOpen(true);
            setLoading(false);
        }
    };

    // Fetch all optimizations on component mount
    useEffect(() => {
        const fetchOptimizations = async () => {
            setLoading(true);
            try {
                const data = await fetchAllDistributionOptimizations(userId);
                setOptimizationData(data);
                setFilteredOptimizations(data); // Filtered data for search
                if (sortDirection === 'asc') {
                    return aDate - bDate; // Ascending order
                }
                return bDate - aDate; // Descending order
            } catch (error) {
                setSnackbarMessage(FAILED_FETCH_DISTRIBUTION_OPTIMIZATIONS_EL);
                setSnackbarSeverity("error");
            } finally {
                setLoading(false);
            }
        };
        fetchOptimizations();
    }, [userId]);

    const sortedOptimizations = filteredOptimizations.sort((a, b) => {
        const aDate = new Date(a.updated_at);
        const bDate = new Date(b.updated_at);
        if (sortDirection === 'asc') {
            return aDate - bDate; // Ascending order
        }
        return bDate - aDate; // Descending order
    });

    // Handle search functionality
    const handleSearchChange = (e) => {
        const value = e.target.value;
        setSearchTerm(value);
        const filtered = optimizationData ? optimizationData.filter(item => String(item.vehicle_id).includes(value)) : [];
        setFilteredOptimizations(filtered);
        setPage(0);
    };

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    return (
        <Box sx={{ p: 3, border: "2px solid #ccc", borderRadius: "8px", boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)", mb: 3 }}>
            {/* Title */}
            <Typography variant="h5" gutterBottom>
                Βελτιστοποίηση Διανομής
            </Typography>

            <Grid container spacing={1} alignItems="center" sx={{ mt: 2 }}>
                {/* Button */}
                <Grid item>
                    <Button variant="contained" color="primary" onClick={handleOptimization} disabled={loading}>
                        ΥΠΟΛΟΓΙΣΜΟΣ ΒΕΛΤΙΣΤΟΠΟΙΗΣΗΣ
                    </Button>
                </Grid>

                {/* Info Text */}
                <Grid item>
                        {/* Info Icon */}
                        <Tooltip
                            title={
                                <Typography sx={{ fontSize: "0.80rem", maxWidth: 300 }}>
                                    Βασίζεται σε όλα τα διαθέσιμα δεδομένα διανομής της ERP βάσης
                                </Typography>
                            }
                            arrow
                            placement="right"
                            PopperProps={{
                                modifiers: [
                                    {
                                        name: "offset",
                                        options: {
                                            offset: [0, 8],
                                        },
                                    },
                                ],
                            }}
                        >
                            <Typography
                                variant="body2"
                                sx={{
                                    color: "#1976D2",
                                    cursor: "pointer",
                                    textDecoration: "underline",
                                    ml: 1
                                }}
                            >
                                <InfoOutlinedIcon sx={{ fontSize: "20px", verticalAlign: "middle" }} />
                            </Typography>
                        </Tooltip>
                </Grid>
            </Grid>

            {/* Search Input */}
            <Grid container spacing={2} alignItems="center" sx={{ mt: 2 }}>
                <Grid item>
                    <TextField
                        label="Αναζήτηση ID Οχήματος"
                        variant="outlined"
                        value={searchTerm}
                        onChange={handleSearchChange}
                        size="small"
                        sx={{ width: "250px" }}
                    />
                </Grid>
            </Grid>

            {/* Filtered Optimization History Table */}
            <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                    Ιστορικό Βέλτιστων Διανομών
                </Typography>
                <TableContainer component={Paper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                {/* Index column header with a right border separator */}
                                <TableCell
                                    sx={{ fontWeight: "bold", borderRight: "1px solid rgba(0,0,0,0.2)", pr: 2 }}
                                >
                                    <strong>Α/Α</strong>
                                </TableCell>
                                <TableCell><strong>ID Οχήματος</strong></TableCell>
                                <TableCell><strong>Τοποθεσία έναρξης</strong></TableCell>
                                <TableCell><strong>Τοποθεσία προορισμού</strong></TableCell>
                                <TableCell><strong>Αρ. Προϊόντων</strong></TableCell>
                                <TableCell onClick={handleSort} style={{ cursor: 'pointer' }}>
                                    <strong>Τελευταία Ενημέρωση</strong>
                                    {sortDirection === 'asc' ? ' ↑' : ' ↓'}
                                </TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {sortedOptimizations.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((item, idx) => (
                                <TableRow key={item.id}>
                                    {/* Index column using the current page offset */}
                                    <TableCell
                                        sx={{ borderRight: "1px solid rgba(0,0,0,0.2)", pr: 2 }}
                                    >
                                        <strong>{page * rowsPerPage + idx + 1}</strong>
                                    </TableCell>
                                    <TableCell>{item.vehicle_id}</TableCell>
                                    <TableCell>{item.start_location_name}</TableCell>
                                    <TableCell>{item.destination_location_name}</TableCell>
                                    <TableCell>{item.units}</TableCell>
                                    <TableCell>{formatTimestampGreek(item.updated_at)}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                    <TablePagination
                        rowsPerPageOptions={[5, 10, 25]}
                        component="div"
                        count={filteredOptimizations.length}
                        rowsPerPage={rowsPerPage}
                        page={page}
                        onPageChange={handleChangePage}
                        onRowsPerPageChange={handleChangeRowsPerPage}
                    />
                </TableContainer>
            </Box>

            {/* Loader and Snackbar Notification */}
            <Loader open={loading} />
            <SnackbarNotification
                open={snackbarOpen}
                onClose={() => setSnackbarOpen(false)}
                message={snackbarMessage}
                severity={snackbarSeverity}
            />
        </Box>
    );
};

export default DistributionOptimization;
