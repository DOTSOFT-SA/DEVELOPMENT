<?php
// Load Dolibarr environment
require '../main.inc.php'; // Main Dolibarr environment
require_once DOL_DOCUMENT_ROOT.'/core/lib/admin.lib.php';

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

    <a id="navigate-button" href="http://localhost:5174/dashboard/inventory-optimization" target="_blank">Dynamic Inventory Optimization</a>
    ';
}

// Function to get total records
function getTotalRecords($db) {
    $sql_count = "SELECT COUNT(*) as total FROM inventory_params_development";
    $resql_count = $db->query($sql_count);
    return $db->fetch_object($resql_count)->total;
}

// Function to get paginated data
function getPaginatedData($db, $records_per_page, $offset) {
    $sql = "SELECT * FROM inventory_params_development LIMIT $records_per_page OFFSET $offset";
    return $db->query($sql);
}

// Function to render the data table
function renderTable($resql, $db) {
    // Define notranslate words
    $notranslate_word_ID = '<span class="notranslate"> ID</span>';
    // Display Columns
    print '<h1>Inventory Parameters Table</h1>';
    print '<table class="noborder" width="100%">';
    print '<tr class="liste_titre">';
//     print '<th style="font-weight: bold;">' . $notranslate_word_ID . '</th>';
    print '<th style="font-weight: bold;">SKU Number</th>';
    print '<th style="font-weight: bold;">Stock Level</th>';
    print '<th style="font-weight: bold;">Time Period (T)</th>';
    print '<th style="font-weight: bold;">Fixed Order Cost (K)</th>';
    print '<th style="font-weight: bold;">Penalty Cost (P)</th>';
    print '<th style="font-weight: bold;">Holding Cost Rate (I)</th>';
    print '<th style="font-weight: bold;">Unit Cost (C)</th>';
    print '<th style="font-weight: bold;">Truckload Capacity (FTL)</th>';
    print '<th style="font-weight: bold;">Transportation Cost (TR)</th>';
    print '<th style="font-weight: bold;">Created</th>';
    print '</tr>';

    // Loop through the results and print each row
    while ($obj = $db->fetch_object($resql)) {
        print '<tr>';
//         print '<td>'.$obj->id.'</td>';
        print '<td>'.$obj->sku_number.'</td>';
        print '<td>'.$obj->stock_level.'</td>';
        print '<td>'.$obj->time_period_t.'</td>';
        print '<td>'.$obj->fixed_order_cost_k.'</td>';
        print '<td>'.$obj->penalty_cost_p.'</td>';
        print '<td>'.$obj->holding_cost_rate_i.'</td>';
        print '<td>'.$obj->unit_cost_c.'</td>';
        print '<td>'.$obj->truckload_capacity_ftl.'</td>';
        print '<td>'.$obj->transportation_cost_tr.'</td>';
        print '<td>'.$obj->created_at.'</td>';
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
renderPageHeader("Inventory Parameters");

// Render toggle button
renderToggleButton();

// Render navigate button
renderNavigateButton();

// Get total records and paginated data
$total_records = getTotalRecords($db);
$total_pages = ceil($total_records / $records_per_page);
$resql = getPaginatedData($db, $records_per_page, $offset);

// Check if query was successful and render table
if ($resql) {
    renderTable($resql, $db);
    renderPaginationControls($page, $total_pages);
} else {
    print "Error fetching data from inventory_params_development table.";
}

// Render page footer
renderPageFooter();

$db->close();

// Prevent translation of text within elements using the "notranslate" class
// (e.g., by browser plugins like Google Translate).
print '
<style>
    .notranslate {
        unicode-bidi: isolate;
    }
</style>
';
