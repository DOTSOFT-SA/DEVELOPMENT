// Use local storage to store the access/refresh token in the browser
export const ACCESS_TOKEN = "accessToken";
export const REFRESH_TOKEN = "refreshToken";

// Constant messages
export const SUCCESS_CREATE = "Επιτυχής δημιουργία!"
export const FAILED_CREATE = "Δημιουργία απέτυχε!"
export const SUCCESS_UPDATE = "Επιτυχής ενημέρωση!"
export const FAILED_UPDATE = "Ενημέρωση απέτυχε!"

export const FAILED_OPEN_NEW_TAB_EL = "Παρακαλώ επιτρέψτε τα αναδυόμενα παράθυρα στο πρόγραμμα περιήγησης.";
export const FAILED_LOGIN_EL = "Αποτυχία σύνδεσης. Επικοινωνήστε με την Υποστήριξη IT για βοήθεια.";

export const ALL_FIELDS_REQUIRED = "Παρακαλώ συμπληρώστε όλα τα πεδία."

export const FIX_FIELDS_WITH_RED = "Παρακαλώ διορθώστε τα πεδία με κόκκινο πριν συνεχίσετε."

export const SUCCESS_DEMAND_FORECASTING_EL = "Η πρόβλεψη ολοκληρώθηκε με επιτυχία!";
export const FAILED_DEMAND_FORECASTING_EL = "Αποτυχία στην πρόβλεψη ζήτησης (Δεν βρέθηκε!)";

export const SUCCESS_LOAD_INPUT_DATA_EL = "Τα δεδομένα εισόδου φορτώθηκαν με επιτυχία!";

export const FAILED_FETCH_INPUT_DATA_EL = "Δεν υπάρχουν δεδομένα εισόδου για προβολή.";

export const FAILED_LOAD_INPUT_DATA_EL = "Αποτυχία φόρτωσης δεδομένων εισόδου.";

export const SUCCESS_INVENTORY_OPTIMIZATION_EL = "H συνιστώμενη ποσότητα του αποθέματος δημιουργήθηκε με επιτυχία!"
export const FAILED_FETCH_SKU_ORDER_PREDICTIONS_EL = "Αποτυχία φόρτωσης προβλέψεων ζήτησης.";

export const FAILED_INVENTORY_OPTIMIZATION_EL = "Αποτυχία στην δημιουργία συνιστώμενης ποσότητας του αποθέματος."

export const FAILED_FETCH_INVENTORY_OPTIMIZATIONS_EL = "Αποτυχία φόρτωσης συνιστώμενης ποσότητας των αποθεμάτων."

export const SUCCESS_DISTRIBUTION_OPTIMIZATION_EL = "Η βελτιστοποίηση διανομής ολοκληρώθηκε με επιτυχία!";
export const FAILED_DISTRIBUTION_OPTIMIZATION_EL = "Αποτυχία στην βελτιστοποίηση διανομής.";

export const FAILED_FETCH_DISTRIBUTION_OPTIMIZATIONS_EL = "Αποτυχία φόρτωσης δεδομένων βελτιστοποίησης διανομής.";

export const FAILED_FETCH_USERS_EL = "Αποτυχία λήψης δεδομένων χρηστών.";

export const FAILED_FETCH_USER_ERP_API_EL = "Αποτυχία λήψης δεδομένων ERP API χρήστη.";

export const FAILED_CHANGE_USER_PASSWORD_EL = "Αποτυχία αλλαγής κωδικού χρήστη."

export const SUCCESS_CREATE_USER_BUT_FAILED_CREATE_USER_ERP_API = "Ο χρήστης δημιουργήθηκε, αλλά τα ERP API URLs χρειάζονται διόρθωση στην επεξεργασία.";

// Constant variables for UI labels based on different conditions.
export const REPORT_INVENTORY_MESSAGE =
    "Η βέλτιστη ποσότητα παραγγελίας για το προϊόν <strong>{sku_name}</strong> με κωδικό <strong>{sku_number}</strong> " +
    "είναι <strong>{Q}</strong> τεμάχια. Η παραγγελία αυτή πρέπει να τίθεται όταν το πραγματικό " +
    "απόθεμα φτάσει στα <strong>{R}</strong> τεμάχια. {inventorySuggestion} " +
    "Το συνολικό κόστος ανέρχεται στα <strong>{totalCost}</strong>€ ανά εβδομάδα. " +
    "Συγκεκριμένα, το κόστος διατήρησης είναι <strong>{holdingCost}</strong>€ " +
    "και το κόστος ανικανοποίητης ζήτησης του αποθέματος είναι <strong>{stockoutCost}</strong>€ ανά εβδομάδα. " +
    "Τέλος, προτείνεται να πραγματοποιείται <strong>{orderFrequency}</strong> παραγγελία των <strong>{Q}</strong> τεμαχίων κάθε <strong>{cycleTime}</strong> εβδομάδες.";

export const ADMIN_DASHBOARD_TITLE = "Περιβάλλον Διαχειριστή"
export const USER_DASHBOARD_TITLE = "Πίνακας Ελέγχου"
