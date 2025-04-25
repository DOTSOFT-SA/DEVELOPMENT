import React, {useEffect, useState} from "react";
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
    TablePagination,
} from "@mui/material";
import Loader from "../components/Loader";
import SnackbarNotification from "../components/SnackbarNotification";
import {
    fetchAllInventoryOptimizations,
    fetchSkuInventoryParams,
    runInventoryOptimization
} from "../services/inventoryOptimizationService";
import {
    SUCCESS_INVENTORY_OPTIMIZATION_EL,
    FAILED_INVENTORY_OPTIMIZATION_EL,
    ALL_FIELDS_REQUIRED,
    FIX_FIELDS_WITH_RED,
    REPORT_INVENTORY_MESSAGE
} from "../utils/constants";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import {formatTimestampGreek} from "../utils/shared.js";
import Tooltip from "@mui/material/Tooltip";
import ExpandableTextField from "../components/ExpandableTextField.jsx";

/**
 * Component for Inventory Optimization.
 * Allows users to input SKU and optional parameters to calculate the optimal inventory order.
 */
const InventoryOptimization = () => {
    // State to store SKU number input field
    const [skuNumber, setSkuNumber] = useState("");
    // Loading state for async API call
    const [loading, setLoading] = useState(false);
    // State to enable/disable the 'report' text area
    const [allowReport, setAllowReport] = useState(false);
    // Report message state (will be displayed in the report area)
    const [reportMessage, setReportMessage] = useState("");
    // Others
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState("");
    const [snackbarSeverity, setSnackbarSeverity] = useState("success");
    const [inventoryOptimizations, setInventoryOptimizations] = useState([]);
    const [filteredOptimizations, setFilteredOptimizations] = useState([]);
    const [searchTerm, setSearchTerm] = useState("");
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [fetchedInventoryParams, setFetchedInventoryParams] = useState(null);

    // Fetch all optimizations for the user, sort by updated_at descending
    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const userId = localStorage.getItem("userId");
                const results = await fetchAllInventoryOptimizations(userId);
                const sorted = results.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
                setInventoryOptimizations(sorted);
                setFilteredOptimizations(sorted);
            } catch (err) {
                console.error("Error fetching optimizations:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // State to store inventory parameters (optional user input fields)
    const [inventoryParams, setInventoryParams] = useState({
        lambda_: "",
        sigma: "",
        stock_level: "",
        time_period_t: "",
        fixed_order_cost_k: "",
        penalty_cost_p: "",
        holding_cost_rate_i: "",
        unit_cost_c: "",
        truckload_capacity_ftl: "",
        transportation_cost_tr: ""
    });

    // Initial output table state showing default values (dashes)
    const [optimizationResult, setOptimizationResult] = useState({
        order_quantity_q: "-",
        reorder_point_r: "-",
        holding_cost: "-",
        setup_transportation_cost: "-",
        stockout_cost: "-",
        total_cost: "-",
        order_frequency: "-",  // computed in handleOptimize
        cycle_time: "-"        // computed in handleOptimize
    });

    // If a field has an invalid (non-numeric) value, it will be set to `true`
    const [invalidFields, setInvalidFields] = useState({
        lambda_: false,
        sigma: false,
        stock_level: false,
        time_period_t: false,
        fixed_order_cost_k: false,
        penalty_cost_p: false,
        holding_cost_rate_i: false,
        unit_cost_c: false,
        // The below are not used in UI anymore
        truckload_capacity_ftl: false,
        transportation_cost_tr: false
    });

    // Reset when you press the clear button
    const clearInventoryParams = () => {
        setInventoryParams({
            lambda_: "",
            sigma: "",
            stock_level: "",
            time_period_t: "",
            fixed_order_cost_k: "",
            penalty_cost_p: "",
            holding_cost_rate_i: "",
            unit_cost_c: "",
            truckload_capacity_ftl: "",
            transportation_cost_tr: ""
        });
        setInvalidFields({
            lambda_: false,
            sigma: false,
            stock_level: false,
            time_period_t: false,
            fixed_order_cost_k: false,
            penalty_cost_p: false,
            holding_cost_rate_i: false,
            unit_cost_c: false,
            truckload_capacity_ftl: false,
            transportation_cost_tr: false
        });
    };

    // If any fields was typed/given a value
    const anyField = Boolean(
        inventoryParams.lambda_ ||
        inventoryParams.sigma ||
        inventoryParams.stock_level ||
        inventoryParams.time_period_t ||
        inventoryParams.fixed_order_cost_k ||
        inventoryParams.penalty_cost_p ||
        inventoryParams.holding_cost_rate_i ||
        inventoryParams.unit_cost_c
        // inventoryParams.truckload_capacity_ftl ||
        // inventoryParams.transportation_cost_tr
    );

    const computeOrderFreqAndCycleTime = (lambda, orderQuantity) => {
        if (!lambda || !orderQuantity) {
            return { orderFreq: "-", cycTime: "-" };
        }
        const orderFreq =
            Number(lambda) / orderQuantity < 1
                ? Math.ceil(Number(lambda) / orderQuantity)
                : Math.floor(Number(lambda) / orderQuantity);
        const cycTime = Math.ceil(orderQuantity / Number(lambda))
        return { orderFreq, cycTime };
    };

    // Computes the suggestion text based on stock level and the reorder point.
    const computeInventorySuggestion = (stockLevel, reorderPoint) => {
        const roundedStockLevel = Math.ceil(stockLevel);
        const roundedReorderPoint = Math.ceil(reorderPoint);
        const diff = roundedStockLevel - roundedReorderPoint;
        const diffText = ` (Διαθέσιμο Απόθεμα - Σημείο Αναπαραγγελίας (R) = <strong>${roundedStockLevel}</strong> - <strong>${roundedReorderPoint}</strong> = <strong>${diff}</strong> τεμάχια).`;

        if (diff > 0) {
            return "Το τρέχον απόθεμα είναι <strong><span style=\"color: green;\">πάνω</span></strong> από το σημείο αναπαραγγελίας" + diffText;
        } else if (diff < 0) {
            return "Το τρέχον απόθεμα είναι <strong><span style=\"color: red;\">κάτω</span></strong> από το σημείο αναπαραγγελίας" + diffText;
        } else {
            return "Το τρέχον απόθεμα είναι <strong><span style=\"color: goldenrod;\">ακριβώς</span></strong> στο σημείο αναπαραγγελίας" + diffText;
        }
    };

    // Build the report message.
    const buildReportMessage = ({
                                    sku_name,
                                    skuNumber,
                                    orderQ,
                                    reorder_point_r,
                                    holding_cost,
                                    stockout_cost,
                                    totalCostWithoutTransportCost,
                                    orderFreq,
                                    cycTime
                                }) => {
        // Convert the stock level and reorder point to numbers.
        const stockLevel = Number(inventoryParams.stock_level);
        const reorderPoint = Number(reorder_point_r); // reorder_point_r from optimization result
        // Compute the inventory suggestion if stock level is provided.
        const suggestionText = inventoryParams.stock_level
            ? computeInventorySuggestion(stockLevel, reorderPoint)
            : "";
        // Build the report message using the provided values.
        return REPORT_INVENTORY_MESSAGE
            .replace("{sku_name}", `<strong>${sku_name}</strong>`)
            .replace("{sku_number}", `<strong>${skuNumber}</strong>`)
            .replace("{Q}", `<strong>${Math.ceil(orderQ)}</strong>`)
            .replace("{R}", `<strong>${Math.ceil(Number(reorder_point_r))}</strong>`)
            .replace("{inventorySuggestion}", suggestionText)
            .replace("{holdingCost}", `<strong>${holding_cost?.toFixed(2) ?? "-"}</strong>`)
            .replace("{stockoutCost}", `<strong>${stockout_cost?.toFixed(2) ?? "-"}</strong>`)
            .replace("{totalCost}", `<strong>${totalCostWithoutTransportCost.toFixed(2)}</strong>`)
            .replace("{orderFrequency}", `<strong>${orderFreq}</strong>`)
            .replace("{Q}", `<strong>${Math.ceil(orderQ)}</strong>`)
            .replace("{cycleTime}", `<strong>${cycTime}</strong>`);
    };

    /**
     * Handles the inventory optimization request when the "ΥΠΟΛΟΓΙΣΜΟΣ" button is clicked.
     */
    const handleOptimize = async () => {
        if (!skuNumber) return;
        setLoading(true);
        try {
            const userId = localStorage.getItem("userId");
            // If any field is marked invalid, display an error and stop
            if (Object.values(invalidFields).some((isInvalid) => isInvalid)) {
                setSnackbarMessage(FIX_FIELDS_WITH_RED);
                setSnackbarSeverity("error");
                setSnackbarOpen(true);
                setLoading(false);
                return;
            }
            // Always validate that all mandatory fields are provided
            const {
                lambda_,
                sigma,
                stock_level,  // optional
                time_period_t,
                fixed_order_cost_k,
                penalty_cost_p,
                holding_cost_rate_i,
                unit_cost_c
            } = inventoryParams;
            if (
                !lambda_ ||
                !sigma ||
                !time_period_t ||
                !fixed_order_cost_k ||
                !penalty_cost_p ||
                !holding_cost_rate_i ||
                !unit_cost_c
            ) {
                setSnackbarMessage(ALL_FIELDS_REQUIRED);
                setSnackbarSeverity("error");
                setSnackbarOpen(true);
                setLoading(false);
                return;
            }
            // Build input object
            let finalParams = {
                id: null,
                lambda_: Number(lambda_),
                sigma: Number(sigma),
                stock_level: Number(stock_level),   // optional
                time_period_t: Number(time_period_t),
                fixed_order_cost_k: Number(fixed_order_cost_k),
                penalty_cost_p: Number(penalty_cost_p),
                holding_cost_rate_i: Number(holding_cost_rate_i),
                unit_cost_c: Number(unit_cost_c),
                truckload_capacity_ftl: 0.0001,
                transportation_cost_tr: 0.0001
            };
            // If fetched parameters exist, compare them with the current values.
            // Create an object with the current numeric values for the mandatory fields.
            if (fetchedInventoryParams) {
                const currentParams = {
                    lambda_: Number(inventoryParams.lambda_),
                    sigma: Number(inventoryParams.sigma),
                    stock_level: Number(inventoryParams.stock_level),
                    time_period_t: Number(inventoryParams.time_period_t),
                    fixed_order_cost_k: Number(inventoryParams.fixed_order_cost_k),
                    penalty_cost_p: Number(inventoryParams.penalty_cost_p),
                    holding_cost_rate_i: Number(inventoryParams.holding_cost_rate_i),
                    unit_cost_c: Number(inventoryParams.unit_cost_c),
                };
                // If no fields have been changed (i.e. currentParams match fetchedInventoryParams), then use null.
                if (JSON.stringify(currentParams) === JSON.stringify(fetchedInventoryParams)) {
                    finalParams = null;
                }
            }
            // Extract optimization results from API response
            const response = await runInventoryOptimization(
                Number(skuNumber),
                Number(userId),
                finalParams
            );
            const { inventory_params, inventory_optimization_dto } = response;
            const {
                sku_name,
                order_quantity_q,
                reorder_point_r,
                holding_cost,
                setup_transportation_cost,
                stockout_cost,
                total_cost
            } = inventory_optimization_dto;
            // Calculate total cost (without transportation cost)
            const totalCostWithoutTransportCost = total_cost - setup_transportation_cost;
            // Compute order frequency and cycle time
            const orderQ = Number(order_quantity_q);
            const { orderFreq, cycTime } = computeOrderFreqAndCycleTime(inventory_params?.lambda_, orderQ);
            // Update the optimization result state with the resulted values
            setOptimizationResult({
                sku_number: skuNumber,
                sku_name: sku_name,
                order_quantity_q: isNaN(Number(order_quantity_q)) ? "-" : order_quantity_q,
                reorder_point_r: isNaN(Number(reorder_point_r)) ? "-" : reorder_point_r,
                holding_cost: holding_cost?.toFixed?.(2) ?? "-",
                setup_transportation_cost: setup_transportation_cost?.toFixed?.(2) ?? "-",
                stockout_cost: stockout_cost?.toFixed?.(2) ?? "-",
                total_cost: isNaN(totalCostWithoutTransportCost) ? "-" : totalCostWithoutTransportCost.toFixed(2),
                order_frequency: orderFreq,
                cycle_time: cycTime
            });
            // Fetch all inventory optimization results for the logged-in user
            const results = await fetchAllInventoryOptimizations(userId);
            // Sort the results in descending order by the 'updated_at' timestamp (most recent first)
            const sorted = results.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
            // Store the sorted list in the state for displaying in the history table
            setInventoryOptimizations(sorted);
            // Set the filtered list (used for search) to the same sorted results initially
            setFilteredOptimizations(sorted);
            // Enable the report area so the message will now be visible
            setAllowReport(true);
            // Generate the report
            const message = buildReportMessage({
                sku_name,
                skuNumber,
                orderQ,
                reorder_point_r,
                holding_cost,
                stockout_cost,
                totalCostWithoutTransportCost,
                orderFreq,
                cycTime
            });
            // Set the message string into the state, so it can be rendered in the report area
            setReportMessage(message);
            // Display success message in the snackbar
            setSnackbarMessage(SUCCESS_INVENTORY_OPTIMIZATION_EL);
            setSnackbarSeverity("success");
            setSnackbarOpen(true);
        } catch (error) {
            // Reset table values in case of failure
            setOptimizationResult({
                sku_name: "-",
                order_quantity_q: "-",
                reorder_point_r: "-",
                holding_cost: "-",
                setup_transportation_cost: "-",
                stockout_cost: "-",
                total_cost: "-",
                order_frequency: "-",
                cycle_time: "-"
            });
            // Display error message in the snackbar
            setSnackbarMessage(FAILED_INVENTORY_OPTIMIZATION_EL);
            setSnackbarSeverity("error");
            setSnackbarOpen(true);
        } finally {
            setLoading(false);  // Hide loader after request completion
        }
    };

    // Handlers for search, pagination changes:
    const handleSearchChange = (e) => {
        const value = e.target.value;
        setSearchTerm(value);
        const filtered = inventoryOptimizations.filter(item =>
            String(item.sku_number).includes(value)
        );
        setFilteredOptimizations(filtered);
        setPage(0);
    };
    const handleChangePage = (event, newPage) => setPage(newPage);
    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };
    const handleFetchInventoryParams = async () => {
        if (!skuNumber) return;
        setLoading(true);
        try {
            const userId = localStorage.getItem("userId");
            const params = await fetchSkuInventoryParams(Number(skuNumber), Number(userId));
            // Autofill the inventory parameter fields with the values from the backend
            setInventoryParams(prev => ({
                ...prev,  // keeps everything that didn't change
                lambda_: params.lambda_ || "",
                sigma: params.sigma || "",
                stock_level: params.stock_level || "",
                time_period_t: params.time_period_t || "",
                fixed_order_cost_k: params.fixed_order_cost_k || "",
                unit_cost_c: params.unit_cost_c || "",
                penalty_cost_p: params.penalty_cost_p || "",
                holding_cost_rate_i: params.holding_cost_rate_i || "",
                truckload_capacity_ftl: params.truckload_capacity_ftl || "",
                transportation_cost_tr: params.transportation_cost_tr || ""
            }));
            // Store a copy of the fetched values for later comparison.
            setFetchedInventoryParams({
                lambda_: Number(params.lambda_),
                sigma: Number(params.sigma),
                stock_level: Number(params.stock_level),
                time_period_t: Number(params.time_period_t),
                fixed_order_cost_k: Number(params.fixed_order_cost_k),
                penalty_cost_p: Number(params.penalty_cost_p),
                holding_cost_rate_i: Number(params.holding_cost_rate_i),
                unit_cost_c: Number(params.unit_cost_c)
            });
            setSnackbarMessage("Τα δεδομένα βρέθηκαν επιτυχώς.");
            setSnackbarSeverity("success");
            setSnackbarOpen(true);
        } catch (error) {
            setSnackbarMessage(error.message || "Αποτυχία φόρτωσης παραμέτρων αποθέματος.");
            setSnackbarSeverity("error");
            setSnackbarOpen(true);
        } finally {
            setLoading(false);
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
            <Typography variant="h5" gutterBottom>
                ΣΥΝΙΣΤΩΜΕΝΗ ΠΟΣΟΤΗΤΑ ΑΠΟΘΕΜΑΤΟΣ
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
                Εισάγετε τον αριθμό SKU για να δείτε τη συνιστώμενη ποσότητα αποθέματός του:
            </Typography>

            {/* SKU Input & ΕΡΕΥΣΗ Field */}
            <Grid container spacing={2} alignItems="center" sx={{mb: 3}}>
                <Grid item>
                    <TextField
                        label="Αριθμός SKU"
                        variant="outlined"
                        value={skuNumber}
                        onChange={(e) => setSkuNumber(e.target.value)}
                        required
                        size="small"
                        sx={{width: "200px"}}
                    />
                </Grid>
                {/* 'ΕΥΡΕΣΗ' button */}
                <Grid item>
                    <Button
                        variant="contained"
                        onClick={handleFetchInventoryParams}
                        disabled={!skuNumber || loading}
                        sx={{ width: "117%" }}
                    >
                        ΕΥΡΕΣΗ
                    </Button>
                </Grid>
                {/* Info Icon */}
                <Tooltip
                    title={
                        <Typography sx={{ fontSize: "0.85rem", maxWidth: 300 }}>
                            Αφού εισαγάγετε τον αριθμό SKU, πατήστε «ΕΥΡΕΣΗ» για να συμπληρωθούν αυτόματα τα παρακάτω πεδία με τις τιμές των παραμέτρων που είναι ήδη καταχωρισμένες στο ERP. Εναλλακτικά, μπορείτε να εισαγάγετε τις δικές σας τιμές χειροκίνητα.
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
                            ml: 3,
                            mt: 2
                        }}
                    >
                        <InfoOutlinedIcon sx={{ fontSize: "20px", verticalAlign: "middle" }} />
                    </Typography>
                </Tooltip>
            </Grid>
            {/* Inventory Params Input Fields */}
            <Grid container spacing={2} alignItems="flex-end" sx={{ mb: 2 }}>
                <Grid item>
                    <Typography variant="body2" sx={{ mb: 2, fontWeight: "normal"}}>
                        Διαθέσιμο Απόθεμα <br /> (σε τεμάχια)
                    </Typography>
                    <ExpandableTextField
                        label="stock level"
                        variant="outlined"
                        placeholder="π.χ. 800"
                        value={inventoryParams.stock_level}
                        onChange={(e) => {
                            const val = e.target.value;
                            setInventoryParams({...inventoryParams, stock_level: val});
                            setInvalidFields({
                                ...invalidFields,
                                stock_level: !!(val && !/^\d+(\.\d+)?$/.test(val))
                            });
                        }}
                        size="small"
                        sx={{width: "115px"}}
                        error={invalidFields.stock_level}
                    />
                </Grid>
                <Grid item>
                    <Typography variant="body2" sx={{ mb: 2, fontWeight: "normal"}}>
                        Προβλεπόμενος <br /> Ρυθμός Ζήτησης <br /> (τμχ / εβδομάδα)
                    </Typography>
                    <ExpandableTextField
                        label="mean *"  // LAMDA
                        variant="outlined"
                        placeholder="π.χ. 500"
                        value={inventoryParams.lambda_}
                        onChange={(e) => {
                            const val = e.target.value;
                            setInventoryParams({...inventoryParams, lambda_: val});
                            setInvalidFields({
                                ...invalidFields,
                                lambda_: !!(val && !/^\d+(\.\d+)?$/.test(val))
                            });
                        }}
                        size="small"
                        sx={{width: "115px"}}
                        error={invalidFields.lambda_}
                    />
                </Grid>
                <Grid item>
                    <Typography variant="body2" sx={{ mb: 2, fontWeight: "normal"}}>
                        Προβλεπόμενη Τυπική <br /> Απόκλιση Ζήτησης <br /> (τμχ / εβδομάδα)
                    </Typography>
                    <ExpandableTextField
                        label="std dev *"  // SIGMA
                        variant="outlined"
                        placeholder="π.χ. 100"
                        value={inventoryParams.sigma}
                        onChange={(e) => {
                            const val = e.target.value;
                            setInventoryParams({...inventoryParams, sigma: val});
                            setInvalidFields({
                                ...invalidFields,
                                sigma: !!(val && !/^\d+(\.\d+)?$/.test(val))
                            });
                        }}
                        size="small"
                        sx={{width: "115px"}}
                        error={invalidFields.sigma}
                    />
                </Grid>
                <Grid item>
                    <Typography variant="body2" sx={{ mb: 2, fontWeight: "normal"}}>
                        Χρόνος Ικανοποίησης <br /> της Παραγγελίας
                    </Typography>
                    <ExpandableTextField
                        label="lead time *"   // T
                        variant="outlined"
                        placeholder="π.χ. 1"
                        value={inventoryParams.time_period_t}
                        onChange={(e) => {
                            const val = e.target.value;
                            setInventoryParams({...inventoryParams, time_period_t: val});
                            setInvalidFields({
                                ...invalidFields,
                                time_period_t: !!(val && !/^\d+(\.\d+)?$/.test(val))
                            });
                        }}
                        size="small"
                        sx={{width: "115px"}}
                        error={invalidFields.time_period_t}
                    />
                </Grid>
                <Grid item>
                    <Typography variant="body2" sx={{ mb: 2, fontWeight: "normal"}}>
                        Κόστος (€) ανά <br /> παραγγελία
                    </Typography>
                    <ExpandableTextField
                        label="K *"
                        variant="outlined"
                        placeholder="π.χ. 50"
                        value={inventoryParams.fixed_order_cost_k}
                        onChange={(e) => {
                            const val = e.target.value;
                            setInventoryParams({...inventoryParams, fixed_order_cost_k: val});
                            setInvalidFields({
                                ...invalidFields,
                                fixed_order_cost_k: !!(val && !/^\d+(\.\d+)?$/.test(val))
                            });
                        }}
                        size="small"
                        sx={{width: "115px"}}
                        error={invalidFields.fixed_order_cost_k}
                    />
                </Grid>
                <Grid item>
                    <Typography variant="body2" sx={{ mb: 2, fontWeight: "normal"}}>
                        Κόστος κεφαλαίου <br /> (€ / € ανά εβδομάδα)
                    </Typography>
                    <ExpandableTextField
                        label="i *"
                        variant="outlined"
                        placeholder="π.χ. 0.1"
                        value={inventoryParams.holding_cost_rate_i}
                        onChange={(e) => {
                            const val = e.target.value;
                            setInventoryParams({...inventoryParams, holding_cost_rate_i: val});
                            setInvalidFields({
                                ...invalidFields,
                                holding_cost_rate_i: !!(val && !/^\d+(\.\d+)?$/.test(val))
                            });
                        }}
                        size="small"
                        sx={{width: "115px"}}
                        error={invalidFields.holding_cost_rate_i}
                    />
                </Grid>
                <Grid item>
                    <Typography variant="body2" sx={{ mb: 2, fontWeight: "normal"}}>
                        Κόστος αγοράς (€) <br /> ανά τεμάχιο
                    </Typography>
                    <ExpandableTextField
                        label="c *"
                        variant="outlined"
                        placeholder="π.χ. 25"
                        value={inventoryParams.unit_cost_c}
                        onChange={(e) => {
                            const val = e.target.value;
                            setInventoryParams({...inventoryParams, unit_cost_c: val});
                            setInvalidFields({
                                ...invalidFields,
                                unit_cost_c: !!(val && !/^\d+(\.\d+)?$/.test(val))
                            });
                        }}
                        size="small"
                        sx={{width: "115px"}}
                        error={invalidFields.unit_cost_c}
                    />
                </Grid>
                <Grid item>
                    <Typography variant="body2" sx={{ mb: 2, fontWeight: "normal"}}>
                        Κόστος (€) ανά Μονάδα <br /> Ανικανοποίητης Ζήτησης
                    </Typography>
                    <ExpandableTextField
                        label="b *"   // P
                        variant="outlined"
                        placeholder="π.χ. 10"
                        value={inventoryParams.penalty_cost_p}
                        onChange={(e) => {
                            const val = e.target.value;
                            setInventoryParams({...inventoryParams, penalty_cost_p: val});
                            setInvalidFields({
                                ...invalidFields,
                                penalty_cost_p: !!(val && !/^\d+(\.\d+)?$/.test(val))
                            });
                        }}
                        size="small"
                        sx={{width: "115px"}}
                        error={invalidFields.penalty_cost_p}
                    />
                </Grid>
            </Grid>
            {/* Buttons */}
            <Grid container spacing={2} alignItems="center" sx={{ mt: 2 }}>
                <Grid item>
                    <Button
                        variant="contained"
                        onClick={handleOptimize}
                        disabled={loading}
                    >
                        ΥΠΟΛΟΓΙΣΜΟΣ
                    </Button>
                </Grid>
                <Grid item>
                    <Button
                        variant="outlined"
                        onClick={clearInventoryParams}
                        sx={{
                            backgroundColor: "#fff",
                            boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.1)",
                            "&:hover": {
                                backgroundColor: "#f5f5f5",
                                boxShadow: "0px 3px 6px rgba(0, 0, 0, 0.10)"
                            }
                        }}
                    >
                        ΕΚΚΑΘΑΡΙΣΗ
                    </Button>
                </Grid>
            </Grid>

            {/* Optimization Result Table */}
            <Box sx={{mt: 3}}>
                <Typography variant="h6" gutterBottom>
                    Αποτέλεσμα Βελτιστοποίησης Αποθέματος SKU
                </Typography>
                <TableContainer component={Paper} sx={{width: "100%"}}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell><strong>Αριθμός SKU</strong></TableCell>
                                <TableCell><strong>Ονομασία SKU</strong></TableCell>
                                <TableCell><strong>Ποσότητα (Q) Παραγγελίας</strong></TableCell>
                                <TableCell><strong>Σημείο (R) Αναπαραγγελίας</strong></TableCell>
                                <TableCell><strong>Κόστος Διατήρησης Αποθέματος (ανά κύκλο)</strong></TableCell>
                                <TableCell><strong>Κόστος Ανικανοποίητης Ζήτησης (ανά κύκλο)</strong></TableCell>
                                <TableCell><strong>Συνολικό Κόστος</strong></TableCell>
                                <TableCell>
                                    <strong>
                                        Αριθμός Παραγγελιών (ανά κύκλο)
                                    </strong>
                                </TableCell>
                                <TableCell><strong>Κύκλος Παραγγελίας (σε εβδομάδες)</strong></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            <TableRow>
                                <TableCell>
                                    {optimizationResult?.sku_number || "-"}
                                </TableCell>
                                <TableCell>
                                    {optimizationResult?.sku_name || "-"}
                                </TableCell>
                                <TableCell>
                                    {isNaN(Number(optimizationResult.order_quantity_q)) ? "-" : Math.ceil(Number(optimizationResult.order_quantity_q)) + ' τμχ'}
                                </TableCell>
                                <TableCell>
                                    {isNaN(Number(optimizationResult.reorder_point_r)) ? "-" : Math.ceil(Number(optimizationResult.reorder_point_r)) + ' τμχ'}
                                </TableCell>
                                <TableCell>
                                    {optimizationResult.holding_cost !== "-" ? Number(optimizationResult.holding_cost).toFixed(2) + ' €' : "-"}
                                </TableCell>
                                <TableCell>
                                    {optimizationResult.stockout_cost !== "-" ? Number(optimizationResult.stockout_cost).toFixed(2) + ' €' : "-"}
                                </TableCell>
                                <TableCell>
                                    {optimizationResult.total_cost !== "-" ? Number(optimizationResult.total_cost).toFixed(2) + ' €' : "-"}
                                </TableCell>
                                <TableCell>{optimizationResult.order_frequency}</TableCell>
                                <TableCell>{optimizationResult.cycle_time}</TableCell>
                            </TableRow>
                        </TableBody>
                    </Table>
                </TableContainer>
            </Box>

            {/* Report Message Area - Always displayed; styled as "disabled" by default */}
            <Box
                sx={{
                    mt: 2,
                    width: "90%",
                    p: 2,
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                    bgcolor: allowReport ? "#f9f9f9" : "#f5f5f5",
                    minHeight: "35px"
                }}
            >
                <Typography
                    variant="body2"
                    sx={{
                        whiteSpace: "pre-line",
                        lineHeight: 1.7,
                        color: allowReport ? "black" : "#9e9e9e"
                    }}
                    dangerouslySetInnerHTML={{
                        __html: reportMessage || "Περιγραφή Αποτελέσματος"
                    }}
                />
            </Box>
            {/* Spacer element for space before <hr /> */}
            <div style={{ height: '20px' }}></div>
            <hr/>
            { /* "Ιστορικό Συνιστώμενης Ποσότητας Αποθεμάτων" table */}
            <Box sx={{mt: 3}}>
                <Typography variant="h6" gutterBottom>
                    Ιστορικό Συνιστώμενης Ποσότητας Αποθεμάτων
                </Typography>
                <TextField
                    label="Αναζήτηση SKU"
                    variant="outlined"
                    value={searchTerm}
                    onChange={handleSearchChange}
                    size="small"
                    sx={{width: "150px", mb: 2}}
                />
                <TableContainer component={Paper} sx={{width: "100%"} }>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell><strong>Αριθμός SKU</strong></TableCell>
                                <TableCell><strong>Ποσότητα Παραγγελίας (Q)</strong></TableCell>
                                <TableCell><strong>Σημείο Αναπαραγγελίας (R)</strong></TableCell>
                                <TableCell><strong>Κόστος Διατήρησης Αποθέματος (ανά κύκλο)</strong></TableCell>
                                <TableCell><strong>Κόστος Ανικανοποίητης Ζήτησης (ανά κύκλο)</strong></TableCell>
                                <TableCell><strong>Συνολικό Κόστος</strong></TableCell>
                                <TableCell><strong>Αριθμός Παραγγελιών (ανά εβδομάδα)</strong></TableCell>
                                <TableCell><strong>Κύκλος Παραγγελίας (σε εβδομάδες)</strong></TableCell>
                                <TableCell><strong>Τελευταία Ενημέρωση</strong></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {filteredOptimizations
                                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                                .map((item) => (
                                    <TableRow key={item.id}>
                                        <TableCell>{item.sku_number}</TableCell>
                                        <TableCell>{Math.ceil(Number(item.order_quantity_q))} τχμ</TableCell>
                                        <TableCell>{Math.ceil(Number(item.reorder_point_r))} τχμ</TableCell>
                                        <TableCell>{item.holding_cost.toFixed(2)} €</TableCell>
                                        <TableCell>{item.stockout_cost.toFixed(2)} €</TableCell><TableCell>{(Number(item.total_cost) - Number(item.setup_transportation_cost)).toFixed(2)} €</TableCell>
                                        <TableCell>
                                            {isNaN(Number(item.order_frequency))
                                                ? "-"
                                                : Number(item.order_frequency) < 1
                                                    ? Math.ceil(Number(item.order_frequency))
                                                    : Math.floor(Number(item.order_frequency))}
                                        </TableCell>
                                        <TableCell>
                                            {isNaN(Number(item.cycle_time))
                                                ? "-"
                                                : Math.ceil(Number(item.cycle_time))}
                                        </TableCell>
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
            {/* Components */}
            <Loader open={loading}/>
            <SnackbarNotification
                open={snackbarOpen}
                onClose={() => setSnackbarOpen(false)}
                message={snackbarMessage}
                severity={snackbarSeverity}
            />
        </Box>
    );
};

export default InventoryOptimization;
