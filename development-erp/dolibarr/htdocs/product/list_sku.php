<?php
// Load Dolibarr environment
require '../main.inc.php'; // Main Dolibarr environment
require_once DOL_DOCUMENT_ROOT.'/core/lib/admin.lib.php';
require_once DOL_DOCUMENT_ROOT.'/product/class/product.class.php';

// Define number of records per page
$records_per_page = 10;

// Get the current page number from the URL, default is page 1
$page = isset($_GET['page']) ? intval($_GET['page']) : 1;
$offset = ($page - 1) * $records_per_page;

// Set the page title and load necessary language files
$langs->load("products");

// Function to render page header and footer
function renderPageHeader($page_name) {
    llxHeader('', $page_name);
}

function renderPageFooter() {
    llxFooter();
}

// Function to render the hide/show sidebar button
function renderToggleButton() {
    print '
    <style>
        #side-menu {
            transition: width 0.3s ease;
        }
        #content-area {
            transition: margin-left 0.3s ease;
        }
        #toggle-menu {
            padding: 8px 16px;
            background-color: #0073aa;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        #toggle-menu:hover {
            background-color: #005f8a;
        }
    </style>

    <button id="toggle-menu" style="margin-bottom: 20px;">Hide Menu</button>

    <script>
        document.getElementById("toggle-menu").onclick = function() {
            var sideMenu = document.getElementById("id-left");
            var contentArea = document.getElementById("id-right");
            if (sideMenu.style.display === "none") {
                sideMenu.style.display = "block";
                contentArea.style.marginLeft = "220px"; // Adjust according to the default width of the menu
                this.textContent = "Hide Menu";
            } else {
                sideMenu.style.display = "none";
                contentArea.style.marginLeft = "0";
                this.textContent = "Show Menu";
            }
        };
    </script>
    ';
}

function renderNavigateButton() {
    print '
    <style>
        #navigate-button {
            float: right;
            padding: 8px 16px;
            background-color: #0073aa;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        #navigate-button:hover {
            background-color: #005f8a;
        }
    </style>

    <a id="navigate-button" href="http://localhost:5174/dashboard/demand-forecasting" target="_blank">Dynamic Demand Forecasting</a>
    ';
}

// Function to get total records
function getTotalRecords($db) {
    $sql_count = "SELECT COUNT(*) as total FROM sku_order_development";
    $resql_count = $db->query($sql_count);
    return $db->fetch_object($resql_count)->total;
}

// Function to get paginated data
function getPaginatedData($db, $records_per_page, $offset) {
    $sql = "SELECT * FROM sku_order_development LIMIT $records_per_page OFFSET $offset";
    return $db->query($sql);
}

// Function to check and replace null or empty values with "N/A"
function checkValueIfNull($value) {
    return (is_null($value) || $value === '') ? "N/A" : $value;
}

// Function to render the data table
function renderTable($resql, $db) {
    // Print the table headers with inline bold style
    print '<h1>Product Orders Table (SKUs)</h1>';
    print '<table class="noborder" width="100%">';
    print '<tr class="liste_titre">';
    print '<th style="font-weight: bold;">SKU Number</th>';
    print '<th style="font-weight: bold;">SKU Name</th>';
    print '<th style="font-weight: bold;">Review Count</th>';
    print '<th style="font-weight: bold;">Review Score</th>';
    print '<th style="font-weight: bold;">Class Display Name</th>';
    print '<th style="font-weight: bold;">SKU Short Description</th>';
    print '<th style="font-weight: bold;">Order Item Price</th>';
    print '<th style="font-weight: bold;">Order Item Unit Count</th>';
    print '<th style="font-weight: bold;">Order Date</th>';
    print '<th style="font-weight: bold;">Product Cost</th>';
    print '<th style="font-weight: bold;">CL Price</th>';
    print '<th style="font-weight: bold;">Price Date</th>';
    print '</tr>';
    // Loop through the results and print each row
    while ($obj = $db->fetch_object($resql)) {
        print '<tr>';
        print '<td>'.checkValueIfNull($obj->sku_number).'</td>';
        print '<td>'.checkValueIfNull($obj->sku_name).'</td>';
        print '<td>'.checkValueIfNull($obj->review_count).'</td>';
        print '<td>'.checkValueIfNull($obj->review_score).'</td>';
        print '<td>'.checkValueIfNull($obj->class_display_name).'</td>';
        print '<td>'.checkValueIfNull($obj->sku_short_description).'</td>';
        print '<td>'.checkValueIfNull($obj->order_item_price_in_main_currency).'</td>';
        print '<td>'.checkValueIfNull($obj->order_item_unit_count).'</td>';
        print '<td>'.checkValueIfNull($obj->order_date).'</td>';
        print '<td>'.checkValueIfNull($obj->product_cost).'</td>';
        print '<td>'.checkValueIfNull($obj->cl_price).'</td>';
        print '<td>'.checkValueIfNull($obj->price_date).'</td>';
        print '</tr>';
    }
    print '</table>';
}

// Function to render pagination controls
function renderPaginationControls($page, $total_pages) {
    print '<div style="text-align:center; margin-top:20px;">';
    // Show "Previous" button if not on the first page
    if ($page > 1) {
        print '<a href="?page='.($page-1).'" style="margin-right:10px;">Previous</a>';
    }
    // Logic to show limited page numbers
    $range = 3; // Adjust this number to show more or fewer page numbers around the current page
    $first_page = 1;
    $last_page = $total_pages;
    // Display the first page always
    if ($page > $range + 1) {
        print '<a href="?page=1">1</a> ';
        if ($page > $range + 2) {
            print '... ';  // Ellipsis before the page range
        }
    }
    // Display the range of page numbers around the current page
    for ($i = max($first_page, $page - $range); $i <= min($last_page, $page + $range); $i++) {
        if ($i == $page) {
            print '<strong>'.$i.'</strong> ';  // Current page
        } else {
            print '<a href="?page='.$i.'">'.$i.'</a> ';
        }
    }
    // Display the last page always
    if ($page < $total_pages - $range) {
        if ($page < $total_pages - $range - 1) {
            print '... ';  // Ellipsis after the page range
        }
        print '<a href="?page='.$total_pages.'">'.$total_pages.'</a> ';
    }
    // Show "Next" button if not on the last page
    if ($page < $total_pages) {
        print '<a href="?page='.($page+1).'" style="margin-left:10px;">Next</a>';
    }
    print '</div>';
}

// --- Main logic ---

// Render page header
renderPageHeader("Products List");

// Render toggle button
renderToggleButton();

// Render navigate button
renderNavigateButton();

// Get total records and paginated data
$total_records = getTotalRecords($db);
$total_pages = ceil($total_records / $records_per_page); // round a number up to the next highest integer
$resql = getPaginatedData($db, $records_per_page, $offset);

// Check if query was successful and render table
if ($resql) {
    renderTable($resql, $db);
    renderPaginationControls($page, $total_pages);
} else {
    print "Error fetching data from development table.";
}

// Render page footer
renderPageFooter();

$db->close();
