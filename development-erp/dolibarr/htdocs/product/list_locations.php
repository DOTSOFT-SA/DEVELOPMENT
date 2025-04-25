<?php
// Load Dolibarr environment
require '../main.inc.php';
require_once DOL_DOCUMENT_ROOT.'/core/lib/admin.lib.php';

// Define number of records per page
$records_per_page = 10;

// Get the current page number from the URL, default is page 1
$page = isset($_GET['page']) ? intval($_GET['page']) : 1;
$offset = ($page - 1) * $records_per_page;

// Set the page title
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

    <a id="navigate-button" href="http://localhost:5174/dashboard/distribution-optimization" target="_blank">Dynamic Distribution Optimization</a>
    ';
}

// Function to render the data table for locations
function renderLocationTable($resql, $db) {
    // Define notranslate words
    $notranslate_word_ID = '<span class="notranslate"> ID</span>';
    // Display Columns
    print '<h1>Locations Table</h1>';
    print '<table class="noborder" width="100%">';
    print '<tr class="liste_titre">';
//     print '<th style="font-weight: bold;">' . $notranslate_word_ID . '</th>';
    print '<th style="font-weight: bold;">Location' . $notranslate_word_ID . '</th>';
    print '<th style="font-weight: bold;">Location Name</th>';
    print '<th style="font-weight: bold;">Demand</th>';
    print '<th style="font-weight: bold;">Is Depot</th>';
    print '<th style="font-weight: bold;">Created</th>';
    print '</tr>';

    // Loop through results
    while ($obj = $db->fetch_object($resql)) {
        $isDepot = $obj->is_depot ? "Yes" : "No";
        print '<tr>';
//         print '<td>'.$obj->id.'</td>';
        print '<td>'.$obj->location_id.'</td>';
        print '<td>'.$obj->location_name.'</td>';
        print '<td>'.$obj->demand.'</td>';
        print '<td>'.$isDepot.'</td>';
        print '<td>'.$obj->created_at.'</td>';
        print '</tr>';
    }
    print '</table>';
}

// Pagination logic
function renderPagination($page, $total_pages) {
    print '<div style="text-align:center; margin-top:20px;">';
    if ($page > 1) {
        print '<a href="?page='.($page-1).'">Previous</a> ';
    }
    for ($i = 1; $i <= $total_pages; $i++) {
        if ($i == $page) {
            print '<strong>'.$i.'</strong> ';
        } else {
            print '<a href="?page='.$i.'">'.$i.'</a> ';
        }
    }
    if ($page < $total_pages) {
        print '<a href="?page='.($page+1).'">Next</a>';
    }
    print '</div>';
}

// Main logic
renderPageHeader("Locations List");

// Render toggle button
renderToggleButton();

// Render navigate button
renderNavigateButton();

$sql_count = "SELECT COUNT(*) as total FROM location_development";
$resql_count = $db->query($sql_count);
$total_records = $db->fetch_object($resql_count)->total;
$total_pages = ceil($total_records / $records_per_page);

$sql = "SELECT * FROM location_development LIMIT $records_per_page OFFSET $offset";
$resql = $db->query($sql);

if ($resql) {
    renderLocationTable($resql, $db);
    renderPagination($page, $total_pages);
} else {
    print "Error fetching data from location_development table.";
}

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
